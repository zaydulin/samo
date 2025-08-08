from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from conference.models import VideoChatMessages, VideoChatRoom, VideoChatUser
import json
from django.utils.dateformat import DateFormat
from datetime import datetime
# =======================
# Consumer для чата
# =======================
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Имя группы для комнаты. Обычно используется префикс, например "chat_"
        self.room_group_name = f'chat_{self.room_name}'

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу при отключении
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Обработка входящих сообщений.
        На клиенте ожидается JSON с ключами:
         - message
         - username
         - avatar
        """
        data = json.loads(text_data)
        message = data.get('message')

        # Пользователь из скоупа
        user = self.scope.get("user")
        # Получаем комнату по slug (self.room_name)
        room = await self.get_room(self.room_name)

        # Если пользователь аутентифицирован, сохраняем сообщение в БД
        if user and user.is_authenticated:
            await self.save_message(user, room, message)

        # Рассылаем сообщение всем участникам группы
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # вызовет метод chat_message
                'message': message,
                'username': data.get('username'),
                'avatar': data.get('avatar'),
            }
        )

    async def chat_message(self, event):
        """Отправка сообщения конкретному WebSocket-клиенту."""
        message = event['message']
        username = event['username']
        avatar = event['avatar']
        # Форматируем текущее время (например, 'HH:MM')
        time = DateFormat(datetime.now()).format('H:i')

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'avatar': avatar,
            'time': time,
        }))

    @database_sync_to_async
    def get_room(self, room_name):
        """
        Получаем объект комнаты по слагу.
        Если комната не существует, можно добавить обработку исключения.
        """
        return VideoChatRoom.objects.get(slug=room_name)

    @database_sync_to_async
    def save_message(self, user, room, message):
        """
        Сохраняем сообщение в БД.
        """
        return VideoChatMessages.objects.create(
            author=user,
            videoroom=room,
            content=message
        )

# =======================
# Consumer для видеосвязи (сигналинг WebRTC)
# =======================
# Простая структура для хранения участников комнаты потом к модели подвяжу
ROOMS = {}

class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'video_{self.room_slug}'
        self.user_id = str(self.scope["user"].id)  # уникальный идентификатор пользователя


        # Добавляем пользователя в список участников с дополнительными данными
        await self.add_user_to_room(
            self.room_slug,
            self.user_id,
            self.scope["user"].username,
            self.scope["user"].avatar.url  # предполагается, что поле avatar содержит URL
        )


        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Отправляем всем обновлённый список участников
        await self.send_participants_update()

    async def disconnect(self, code):
        await self.remove_user_from_room(self.room_slug, self.user_id)
        await self.send_participants_update()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        data["sender"] = self.user_id
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "signal_message",
                "data": data,
            }
        )

    async def signal_message(self, event):
        data = event["data"]
        # Если указан target и он не совпадает с нашим, пропускаем
        if "target" in data and data["target"] and data["target"] != self.user_id:
            return
        await self.send(text_data=json.dumps(data))

    async def send_participants_update(self):
        # Получаем список участников как список словарей с данными пользователя
        participants = list(ROOMS.get(self.room_slug, {}).values())
        update_message = {
            "type": "participants_update",
            "participants": participants,
        }
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "signal_message",
                "data": update_message,
            }
        )

    @database_sync_to_async
    def add_user_to_room(self, room, user_id, username, avatar):
        if room not in ROOMS:
            ROOMS[room] = {}
        ROOMS[room][user_id] = {
            "id": user_id,
            "username": username,
            "avatar": avatar,
        }

    @database_sync_to_async
    def remove_user_from_room(self, room, user_id):
        if room in ROOMS:
            ROOMS[room].pop(user_id, None)
            if not ROOMS[room]:
                del ROOMS[room]

# =======================
# Consumer для взаимодействий с комнатой
# =======================
class RoomControlConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'video_control_{self.room_slug}'

        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"[ROOM CONTROL] Подключён контроллер для комнаты: {self.room_slug}")
        except Exception as e:
            print(f"[ERROR] Ошибка при подключении: {e}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"[ROOM CONTROL] Отключён контроллер для комнаты: {self.room_slug}")
        except Exception as e:
            print(f"[ERROR] Ошибка при отключении: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "start":
                await self.handle_start()
            elif message_type == "stop":
                await self.handle_stop()
            elif message_type == "room_canceled":
                await self.handle_room_canceled()
            else:
                print(f"[ERROR] Неизвестный тип сообщения: {message_type}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Неизвестный тип сообщения."
                }))
        except Exception as e:
            print(f"[ERROR] Исключение в receive: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Произошла внутренняя ошибка сервера."
            }))
            await self.close(code=1011)

    async def handle_start(self):
        try:
            if not await self.is_user_spiker(self.room_slug, self.scope["user"]):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Только ответственный (spiker) может открыть комнату."
                }))
                return

            await self.set_room_open(self.room_slug)
            update_message = {
                "type": "room_open",
                "is_start": True,
                "message": "Комната открыта",
                "token": await self.get_room_token(self.room_slug),
            }

            try:
                # Отправляем уведомление всем контроллерам
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "room_open",
                        "data": update_message,
                    }
                )

                # Отправляем сообщение группе redirect_<slug>
                redirect_group = f'redirect_{self.room_slug}'
                await self.channel_layer.group_send(
                    redirect_group,
                    {
                        "type": "redirect_user",
                        "token": update_message["token"],
                    }
                )

                print(f"[ROOM CONTROL] Комната {self.room_slug} открыта!")
            except Exception as e:
                print(f"[ERROR] Ошибка при отправке room_open: {e}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Ошибка при уведомлении участников об открытии комнаты."
                }))
        except Exception as e:
            print(f"[ERROR] Исключение в handle_start: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Внутренняя ошибка при открытии комнаты."
            }))

    async def handle_stop(self):
        try:
            if not await self.is_user_spiker(self.room_slug, self.scope["user"]):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Только ответственный (spiker) может остановить комнату."
                }))
                return

            await self.set_room_closed(self.room_slug)
            update_message = {
                "type": "room_closed",
                "is_closed": True,
                "message": "Комната закрыта",
                "token": await self.get_room_token(self.room_slug),
            }

            try:
                # Отправляем уведомление всем контроллерам
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "room_closed",
                        "data": update_message,
                    }
                )

                # Отправляем сообщение группе redirect_<slug>
                redirect_group = f'redirect_{self.room_slug}'
                await self.channel_layer.group_send(
                    redirect_group,
                    {
                        "type": "redirect_user",
                        "token": update_message["token"],
                    }
                )

                print(f"[ROOM CONTROL] Комната {self.room_slug} закрыта!")
            except Exception as e:
                print(f"[ERROR] Ошибка при отправке room_closed: {e}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Ошибка при уведомлении участников о закрытии комнаты."
                }))
        except Exception as e:
            print(f"[ERROR] Исключение в handle_stop: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Внутренняя ошибка при закрытии комнаты."
            }))

    async def handle_room_canceled(self):
        try:
            if not await self.is_user_spiker(self.room_slug, self.scope["user"]):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Только ответственный (spiker) может отменить комнату."
                }))
                return

            await self.set_room_type(self.room_slug, 2)
            update_message = {
                "type": "room_canceled",
                "message": "Комната стала доступна только по ключу",
                "token": await self.get_room_token(self.room_slug),
            }

            try:
                # Отправляем уведомление всем контроллерам
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "room_canceled",
                        "data": update_message,
                    }
                )

                # Отправляем сообщение группе redirect_<slug>
                redirect_group = f'redirect_{self.room_slug}'
                await self.channel_layer.group_send(
                    redirect_group,
                    {
                        "type": "redirect_user",
                        "token": update_message["token"],
                    }
                )

                print(f"[ROOM CONTROL] Комната {self.room_slug} стала доступна только по ключу!")
            except Exception as e:
                print(f"[ERROR] Ошибка при отправке room_canceled: {e}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Ошибка при уведомлении участников об отмене комнаты."
                }))
        except Exception as e:
            print(f"[ERROR] Исключение в handle_room_canceled: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Внутренняя ошибка при отмене комнаты."
            }))

    async def room_open(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def room_closed(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def room_canceled(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def is_user_spiker(self, room_slug, user):
        room = VideoChatRoom.objects.get(slug=room_slug)
        return room.spiker_id == user.id

    @database_sync_to_async
    def set_room_open(self, room_slug):
        room = VideoChatRoom.objects.get(slug=room_slug)
        room.is_closed = False
        room.is_start = True
        room.save()

    @database_sync_to_async
    def set_room_closed(self, room_slug):
        room = VideoChatRoom.objects.get(slug=room_slug)
        room.is_closed = True
        room.is_start = False
        room.save()

    @database_sync_to_async
    def set_room_type(self, room_slug, new_type):
        room = VideoChatRoom.objects.get(slug=room_slug)
        room.type = new_type
        room.save()

    @database_sync_to_async
    def get_room_token(self, room_slug):
        room = VideoChatRoom.objects.get(slug=room_slug)
        if not room.token:
            raise ValueError(f"Токен для комнаты '{room_slug}' отсутствует.")
        return room.token


# =======================
# Consumer для отлючения всех в комнате когда она закрывается
# =======================

class ParticipantConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_slug = self.scope['url_route']['kwargs']['slug']
            self.group_name = f'redirect_{self.room_slug}'
            print(f"[DEBUG] Подключение к комнате с slug: {self.room_slug}")

            # Получаем объект VideoChatRoom
            self.video_chat_room = await self.get_video_chat_room(self.room_slug)
            if not self.video_chat_room:
                print(f"[DEBUG] Комната с slug '{self.room_slug}' не найдена. Закрытие соединения.")
                await self.close()
                return
            else:
                print(f"[DEBUG] Комната найдена: {self.video_chat_room}")

            # Временно закомментируем проверку аутентификации
            # user = self.scope['user']
            # if not user.is_authenticated:
            #     print("[DEBUG] Пользователь не аутентифицирован. Закрытие соединения.")
            #     await self.close()
            #     return

            # Проверяем, является ли пользователь visitor или spiker
            user = self.scope.get('user', None)
            if user:
                is_visitor = await self.is_user_visitor(user, self.video_chat_room)
                is_spiker = await self.is_user_spiker(user, self.video_chat_room)
                print(f"[DEBUG] Пользователь: {user.username}, Visitor: {is_visitor}, Spiker: {is_spiker}")
            else:
                print("[DEBUG] Пользователь не найден в scope.")
                is_visitor = False
                is_spiker = False

            if not is_visitor and not is_spiker:
                print(f"[DEBUG] Добавление в группу '{self.group_name}' для перенаправления.")
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
            else:
                print("[DEBUG] Пользователь является visitor или spiker. Не добавляем в группу перенаправления.")

            await self.accept()
            print(f"[PARTICIPANT] Пользователь подключен к комнате {self.room_slug}")
        except Exception as e:
            print(f"[ERROR] Ошибка при подключении: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            print(f"[DEBUG] Отключение пользователя из комнаты {self.room_slug} с кодом закрытия {close_code}")
            user = self.scope.get('user', None)
            if user:
                is_visitor = await self.is_user_visitor(user, self.video_chat_room)
                is_spiker = await self.is_user_spiker(user, self.video_chat_room)
                print(f"[DEBUG] Пользователь: {user.username}, Visitor: {is_visitor}, Spiker: {is_spiker}")
            else:
                print("[DEBUG] Пользователь не найден в scope.")
                is_visitor = False
                is_spiker = False

            if not is_visitor and not is_spiker:
                print(f"[DEBUG] Удаление из группы '{self.group_name}'")
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            print(f"[PARTICIPANT] Пользователь отключился от комнаты {self.room_slug}")
        except Exception as e:
            print(f"[ERROR] Ошибка при отключении: {e}")

    # Обработка сообщений типа redirect_user
    async def redirect_user(self, event):
        try:
            token = event.get('token')
            redirect_url = f"/ru/request/conference/?slug={self.room_slug}"
            print(f"[DEBUG] Отправка перенаправления на URL: {redirect_url}")
            await self.send(text_data=json.dumps({
                'type': 'redirect',
                'url': redirect_url
            }))
        except Exception as e:
            print(f"[ERROR] Ошибка при отправке перенаправления: {e}")

    @database_sync_to_async
    def get_video_chat_room(self, slug):
        try:
            room = VideoChatRoom.objects.get(slug=slug)
            print(f"[DEBUG] Найдена комната: {room}")
            return room
        except VideoChatRoom.DoesNotExist:
            print(f"[DEBUG] Комната с slug '{slug}' не существует.")
            return None

    @database_sync_to_async
    def is_user_visitor(self, user, video_chat_room):
        try:
            is_visitor = video_chat_room.visitors.filter(id=user.id).exists()
            print(f"[DEBUG] Проверка is_user_visitor: {is_visitor}")
            return is_visitor
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке is_user_visitor: {e}")
            return False

    @database_sync_to_async
    def is_user_spiker(self, user, video_chat_room):
        try:
            is_spiker = video_chat_room.spiker == user
            print(f"[DEBUG] Проверка is_user_spiker: {is_spiker}")
            return is_spiker
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке is_user_spiker: {e}")
            return False

# =======================
# Consumer для вывода не одобренных
# =======================

class NotAddedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = f'notadded_{self.slug}'
        print(f"[CONNECT] Подключение к комнате: {self.slug}")

        # Проверяем существование комнаты
        self.room = await self.get_room(self.slug)
        if not self.room:
            print(f"[CONNECT] Комната с slug '{self.slug}' не найдена. Закрытие соединения.")
            await self.close()
            return

        # Проверяем права пользователя
        user = self.scope.get('user', None)
        if user:
            is_spiker = await self.is_user_spiker(user, self.room)
        else:
            is_spiker = False

        if not is_spiker:
            username = await self.get_username_sync(user) if user else 'Unknown'
            print(f"[CONNECT] Пользователь '{username}' не является спикером комнаты '{self.slug}'. Закрытие соединения.")
            await self.close()
            return

        # Подключаемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        username = await self.get_username_sync(user)
        print(f"[CONNECT] Пользователь '{username}' подключен к комнате '{self.slug}'.")
        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"[DISCONNECT] Пользователь отключился от комнаты '{self.slug}' с кодом закрытия {close_code}.")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            videochat_user_id = data.get('videochat_user_id')

            print(f"[RECEIVE] Получено действие: '{action}', Пользователь ID: '{videochat_user_id}'.")

            if action and videochat_user_id:
                videochat_user = await self.get_videochat_user(videochat_user_id)
                if videochat_user:
                    if action == 'allow_watch':
                        await self.allow_watch(videochat_user)
                    elif action == 'allow_participate':
                        await self.allow_participate(videochat_user)
                    else:
                        print(f"[RECEIVE] Неизвестное действие: {action}")
                else:
                    print(f"[RECEIVE] Пользователь с ID '{videochat_user_id}' не найден.")
            else:
                print("[RECEIVE] Некорректные данные.")
        except Exception as e:
            print(f"[ERROR] Ошибка в методе receive: {e}")

    async def allow_watch(self, videochat_user):
        try:
            print(f"[ALLOW_WATCH] Начало обработки для пользователя ID: {videochat_user.id}")
            await self.remove_notadded(videochat_user)
            await self.add_visitor(videochat_user)
            username = await self.get_username_sync(videochat_user)
            print(f"[ALLOW_WATCH] Разрешено смотреть пользователю '{username}'.")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_notadded',
                    'videochat_user_id': videochat_user.id,
                }
            )
        except Exception as e:
            print(f"[ERROR] Ошибка в allow_watch: {e}")

    async def allow_participate(self, videochat_user):
        try:
            print(f"[ALLOW_PARTICIPATE] Начало обработки для пользователя ID: {videochat_user.id}")
            await self.remove_notadded(videochat_user)
            await self.add_participant(videochat_user)
            username = await self.get_username_sync(videochat_user)
            print(f"[ALLOW_PARTICIPATE] Разрешено участвовать пользователю '{username}'.")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_notadded',
                    'videochat_user_id': videochat_user.id,
                }
            )
        except Exception as e:
            print(f"[ERROR] Ошибка в allow_participate: {e}")

    async def update_notadded(self, event):
        try:
            videochat_user_id = event['videochat_user_id']
            print(f"[UPDATE_NOTADDED] Удаление пользователя ID: '{videochat_user_id}' из notadded.")

            # Отправляем сообщение клиенту
            await self.send(text_data=json.dumps({
                'action': 'remove_user',
                'videochat_user_id': videochat_user_id,
            }))
        except Exception as e:
            print(f"[ERROR] Ошибка в update_notadded: {e}")

    async def add_user(self, event):
        try:
            user_data = event['user']
            print(f"[ADD_USER] Добавление пользователя: {user_data['username']}")

            # Отправляем сообщение клиенту
            await self.send(text_data=json.dumps({
                'action': 'add_user',
                'user': user_data,
            }))
        except Exception as e:
            print(f"[ERROR] Ошибка в add_user: {e}")

    async def clear_notadded(self, event):
        try:
            print("[CLEAR_NOTADDED] Очистка списка notadded.")

            # Отправляем сообщение клиенту для очистки списка
            await self.send(text_data=json.dumps({
                'action': 'clear_notadded',
            }))
        except Exception as e:
            print(f"[ERROR] Ошибка в clear_notadded: {e}")

    @database_sync_to_async
    def get_room(self, slug):
        try:
            room = VideoChatRoom.objects.get(slug=slug)
            print(f"[GET_ROOM] Найдена комната: {room}")
            return room
        except VideoChatRoom.DoesNotExist:
            print(f"[GET_ROOM] Комната с slug '{slug}' не существует.")
            return None

    @database_sync_to_async
    def is_user_spiker(self, user, video_chat_room):
        try:
            is_spiker = video_chat_room.spiker == user
            print(f"[IS_USER_SPIKER] Пользователь является спикером: {is_spiker}")
            return is_spiker
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке is_user_spiker: {e}")
            return False

    @database_sync_to_async
    def get_videochat_user(self, videochat_user_id):
        try:
            return VideoChatUser.objects.get(id=videochat_user_id)
        except VideoChatUser.DoesNotExist:
            return None

    @sync_to_async
    def remove_notadded(self, videochat_user):
        try:
            self.room.notadded.remove(videochat_user)
            print(f"[REMOVE_NOTADDED] Пользователь ID '{videochat_user.id}' удалён из notadded.")
        except Exception as e:
            print(f"[ERROR] Ошибка в remove_notadded: {e}")
            raise

    @sync_to_async
    def add_visitor(self, videochat_user):
        try:
            self.room.visitors.add(videochat_user)
            print(f"[ADD_VISITOR] Пользователь ID '{videochat_user.id}' добавлен в visitors.")
        except Exception as e:
            print(f"[ERROR] Ошибка в add_visitor: {e}")
            raise

    @sync_to_async
    def add_participant(self, videochat_user):
        try:
            self.room.participants.add(videochat_user)
            print(f"[ADD_PARTICIPANT] Пользователь ID '{videochat_user.id}' добавлен в participants.")
        except Exception as e:
            print(f"[ERROR] Ошибка в add_participant: {e}")
            raise

    @sync_to_async
    def get_username_sync(self, videochat_user):
        try:
            return videochat_user.user.username
        except Exception as e:
            print(f"[ERROR] Ошибка при получении username: {e}")
            return "Unknown"

# =======================
# Consumer для редиректа одобренных
# =======================
class UserRedirectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f'user_{user.id}'
        print(f"[CONNECT_USER] Подключение к личной группе: {self.user_group_name}")

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"[CONNECT_USER] Пользователь '{user.username}' подключен к личной группе.")

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            print(f"[DISCONNECT_USER] Пользователь '{user.username}' отключился от личной группы.")

    # Метод для обработки сообщения 'user_allowed'
    async def user_allowed(self, event):
        redirect_url = event['redirect_url']
        print(f"[USER_ALLOWED] Отправка команды на редирект на URL {redirect_url}")

        await self.send(text_data=json.dumps({
            'action': 'user_allowed',
            'redirect_url': redirect_url,
        }))