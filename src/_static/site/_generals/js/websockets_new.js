document.addEventListener("DOMContentLoaded", function() {
    var loc = window.location;
    const messagesList = document.getElementById('chat');
    if (messagesList) {
        messagesList.scrollTop = messagesList.scrollHeight;
    } else {
        console.error("Element with id 'chat' not found.");
    }
    var endPoint = '';
    var wsStart = 'ws://';
    if(loc.protocol == 'https:'){
        wsStart = 'wss://';
    }

    // Извлечение slug из URL
    var pathSegments = loc.pathname.split('/').filter(Boolean); // Убираем пустые сегменты
    console.log(pathSegments)
    var slug = pathSegments[pathSegments.length - 1]; // Берем последний сегментRL
    var endPoint = wsStart + loc.host + '/messages/' + slug + '/';
    console.log(endPoint);
    const messageSocket = new WebSocket(
        endPoint
    );

    messageSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.type === 'new_message') {
            // Обработка новых сообщений
            let profileImageURL = data.message.sender_image;
            let senderName = data.message.sender;

            const newMessageHTML = `
                <div class="p-3">
                    <div class="flex items-center gap-3">
                        <div class="h-10 w-10 flex-shrink-0">
                            <img class="h-10 w-10 rounded-full" src="${profileImageURL}" alt="">
                        </div>
                        <div class="flex-grow truncate">
                            <div class="font-medium text-gray-900 dark:text-gray-300">${senderName}</div>
                            <p class="text-gray-600 dark:text-gray-400">${data.message.content}</p>
                        </div>
                    </div>
                </div>
            `;

            messagesList.insertAdjacentHTML('beforeend', newMessageHTML);
            messagesList.scrollTop = messagesList.scrollHeight;
        }
        else if (data.type === 'participants_changed') {
            // Обработка изменений в списке участников
            const participantsList = document.getElementById('participants-list');
            // Получаем id текущего пользователя и спикера из атрибутов data-my-id и data-spiker
            const myId = participantsList.getAttribute('data-my-id');
            const spikerId = participantsList.getAttribute('data-spiker');
            // Если текущий пользователь является спикером, добавляем часть кода только для спикера
            if (myId === spikerId) {
                // Если происходит добавление участника
                if (data.action === 'post_add') {
                    // Проверяем, есть ли участник с таким id в списке
                    const existingParticipant = document.getElementById(`list-user-participant-${data.participants[0].id}`);
                    // Если участника с таким id нет, добавляем его
                    if (!existingParticipant) {
                        const participantHTML = `
                    <div class="grid-item" id="list-user-participant-${data.participants[0].id}" data-spiker="user-${data.participants[0].id}">
                        <video id="video-${data.participants[0].id}" class="video-bg" autoplay playsinline></video>                              
                        <div class="relative" style="display: inline-flex; position: absolute; top: 50px; z-index: 1000; ">
                            <button type="button" id="participants-sound-${data.participants[0].id}" data-user="${data.participants[0].id}" data-button-type="sound" class="btn btn-lg bg-danger text-white">
                                <i class="mgc_volume_mute_line text-base "></i>
                            </button>
                            <button type="button" id="participants-video-${data.participants[0].id}" data-user="${data.participants[0].id}" data-button-type="video"  class="btn btn-lg bg-danger text-white">
                                <i class="mgc_computer_camera_off_line text-base "></i>
                            </button>
                            <button type="button" id="noparticipants-${data.participants[0].id}" data-user="${data.participants[0].id}" data-button-type="noparticipants"  data-action="remove_participant" data-action="block_participant" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">
                                <i class="mgc_phone_block_line text-base"></i>
                            </button>
                            <button type="button" id="not_added-${data.participants[0].id}" data-action="add_to_not_added" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">
                                <i class="mgc_exit_fill text-base"></i>
                            </button>
                            <button type="button" id="participants-saved_video-${data.participants[0].id}"  data-user="${data.participants[0].id}" data-button-type="saved_video"  class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">                
                                <i class="mgc_save_2_line text-base "></i>
                            </button>
                            <button type="button" id="pin-${data.participants[0].id}" data-action="pin_primary"  data-user="${data.participants[0].id}" data-button-type="pin"  class="btn btn-lg bg-danger/25 text-danger hover:bg-secondary hover:text-white">
                                <i class="mgc_pin_2_line text-base "></i>
                            </button>
                        </div>
                    </div>
                `;
                        participantsList.insertAdjacentHTML('beforeend', participantHTML);
                        // После добавления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }

                // Если происходит удаление участника
                else if (data.action === 'post_remove') {
                    // Проверяем, есть ли участник с таким id в списке
                    const existingParticipant = document.getElementById(`list-user-participant-${data.participants[0].id}`);
                    // Если участник с таким id есть, удаляем его
                    if (existingParticipant) {
                        existingParticipant.remove();
                        // После удаления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }
            } else {
                if (data.action === 'post_add') {
                    // Если текущий пользователь не является спикером, добавляем часть кода для всех пользователей, кроме спикера
                    const existingParticipant = document.getElementById(`list-user-participant-${data.participants[0].id}`);
                    // Если участника с таким id нет, добавляем его
                    if (!existingParticipant) {
                        const participantHTML = `
                            <div class="grid-item" id="list-user-participant-${data.participants[0].id}" data-spiker="user-${data.participants[0].id}">
                                <div class="my-button" style="position: relative; z-index: 1000; left: 20px; top: 20px;width: 0;">
                                    <!---Для всех пользователей--->    
                                    <button type="button" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200" disabled>
                                        <i class="mgc_volume_mute_line text-base"></i>
                                    </button>
                                    <button type="button" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200" disabled>
                                        <i class="mgc_computer_camera_off_line text-base"></i>
                                    </button>   
                                    <!---////--->    
                                </div>
                                <video id="video-${data.participants[0].id}" class="video-bg" autoplay playsinline></video>
                            </div>
                        `;
                        participantsList.insertAdjacentHTML('beforeend', participantHTML);
                        // После добавления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }
                // Если происходит удаление участника
                else if (data.action === 'post_remove') {
                    // Проверяем, есть ли участник с таким id в списке
                    const existingParticipant = document.getElementById(`list-user-participant-${data.participants[0].id}`);
                    // Если участник с таким id есть, удаляем его
                    if (existingParticipant) {
                        existingParticipant.remove();
                        // После удаления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }

            }
        }
        else if (data.type === 'primary_changed') {
            // Обработка изменений в списке участников
            const primaryList = document.getElementById('participants-list');

            // Получаем id текущего пользователя и спикера из атрибутов data-my-id и data-spiker
            const myId = primaryList.getAttribute('data-my-id');
            const spikerId = primaryList.getAttribute('data-spiker');

            // Если текущий пользователь является спикером, добавляем часть кода только для спикера
            if (myId === spikerId) {
                // Если происходит добавление участника
                if (data.action === 'post_add') {
                    // Проверяем, есть ли участник с таким id в списке
                    const existingPrimary = document.getElementById(`list-user-primary-${data.primary[0].id}`);
                    // Если участника с таким id нет, добавляем его
                    if (!existingPrimary) {
                        const primarHTML = `
                    <div class="grid-item"  data-primary="primary"  id="list-user-primary-${data.primary[0].id}" data-spiker="user-${data.primary[0].id}">
                        <video id="video-${data.participants[0].id}" class="video-bg" autoplay playsinline></video>                              
                        <div class="relative" style="display: inline-flex; position: absolute; top: 50px; z-index: 1000; ">
                            <button type="button" id="primary-sound-${data.primary[0].id}" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">
                                <i class="mgc_volume_mute_line text-base "></i>
                            </button>
                            <button type="button" id="primary-video-${data.primary[0].id}" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">
                                <i class="mgc_computer_camera_off_line text-base "></i>
                            </button>
                            <button type="button" id="noprimary-${data.primary[0].id}" data-action="remove_primar" data-action="block_primar" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">
                                <i class="mgc_phone_block_line text-base"></i>
                            </button>
                            <button type="button" id="not_added-${data.primary[0].id}" data-action="add_to_not_added" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">
                                <i class="mgc_exit_fill text-base"></i>
                            </button>
                            <button type="button" id="primary-saved_video-${data.primary[0].id}" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200">                
                                <i class="mgc_save_2_line text-base "></i>
                            </button>
                            <button type="button" id="pin-${data.primary[0].id}" data-action="pin_primary"  class="btn btn-lg bg-danger/25 text-danger hover:bg-secondary hover:text-white">
                                <i class="mgc_pin_2_line text-base "></i>
                            </button>
                        </div>
                    </div>
                `;
                        primaryList.insertAdjacentHTML('beforeend', primarHTML);
                        // После добавления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }

                // Если происходит удаление участника
                else if (data.action === 'post_remove') {
                    // Проверяем, есть ли участник с таким id в списке
                    const existingPrimary = document.getElementById(`list-user-primary-${data.primary[0].id}`);
                    // Если участник с таким id есть, удаляем его
                    if (existingPrimary) {
                        existingPrimary.remove();
                        // После удаления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }
            } else {
                if (data.action === 'post_add') {
                    // Если текущий пользователь не является спикером, добавляем часть кода для всех пользователей, кроме спикера
                    const existingPrimary = document.getElementById(`list-user-primary-${data.primary[0].id}`);
                    // Если участника с таким id нет, добавляем его
                    if (!existingPrimary) {
                        const primarHTML = `
                            <div class="grid-item"  data-primary="primary"  id="list-user-primar-${data.primary[0].id}" data-spiker="user-${data.primary[0].id}">
                                <div class="my-button" style="position: relative; z-index: 1000; left: 20px; top: 20px;width: 0;">
                                    <!---Для всех пользователей--->    
                                    <button type="button" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200" disabled>
                                        <i class="mgc_volume_mute_line text-base"></i>
                                    </button>
                                    <button type="button" class="btn btn-lg bg-light text-slate-900 dark:text-slate-200" disabled>
                                        <i class="mgc_computer_camera_off_line text-base"></i>
                                    </button>   
                                    <!---////--->    
                                </div>
                                <video id="video-${data.participants[0].id}" class="video-bg" autoplay playsinline></video>
                            </div>
                        `;
                        primaryList.insertAdjacentHTML('beforeend', primarHTML);
                        // После добавления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }
                // Если происходит удаление участника
                else if (data.action === 'post_remove') {
                    // Проверяем, есть ли участник с таким id в списке
                    const existingPrimary = document.getElementById(`list-user-primary-${data.primary[0].id}`);
                    // Если участник с таким id есть, удаляем его
                    if (existingPrimary) {
                        existingPrimary.remove();
                        // После удаления участника обновляем расположение элементов сетки
                        resetAndAdjustGridItems();
                        initializeVideoChat();
                    }
                }

            }
        }
        else if (data.type === 'visitors_changed') {
            // Обработка изменений в списке участников
            const visitorsList = document.getElementById('visitors-list');

            // Если происходит добавление участника
            if (data.action === 'post_add') {
                // Проверяем, есть ли участник с таким id в списке
                const existingVisitors = document.getElementById(`list-user-visitors-${data.visitors[0].id}`);
                // Если участника с таким id нет, добавляем его
                if (!existingVisitors) {
                    const visitorsHTML = `                        
                        <div class="flex relative" id="list-user-visitors--${data.visitors[0].id}">
                            <img alt="gallery" class="absolute w-full object-cover object-center rounded" width="150px" src="${data.visitors[0].user__avatar}">
                            <div class="px-8 py-10 relative z-10 w-full bg-white opacity-0 hover:opacity-80">
                                <h1 class="title-font text-lg font-medium text-gray-900 mb-3">
                                    ${data.visitors[0].user__username}
                                </h1>
                            </div>
                        </div>
                    `;
                    visitorsList.insertAdjacentHTML('beforeend', visitorsHTML);
                }
            }
            // Если происходит удаление участника
            else if (data.action === 'post_remove') {
                // Проверяем, есть ли участник с таким id в списке
                const existingVisitors = document.getElementById(`list-user-visitors-${data.visitors[0].id}`);
                // Если участник с таким id есть, удаляем его
                if (existingVisitors) {
                    existingVisitors.remove();
                }
            }
        }
        else if (data.type === 'not_added_changed') {
            // Обработка изменений в списке не добавленых
            const not_addedList = document.getElementById('not_added-list');

            // Если происходит добавление участника
            if (data.action === 'post_add') {
                // Проверяем, есть ли участник с таким id в списке
                const existingNot_added = document.getElementById(`list-user-not_added-${data.not_added[0].id}`);
                // Если участника с таким id нет, добавляем его
                if (!existingNot_added) {
                    const primaryHTML = `
                        <div class="p-3"  id="list-user-not_added-${data.not_added[0].id}">    
                            <div class="flex items-center gap-3">                       
                                <div class="h-10 w-10 flex-shrink-0">
                                    <img class="h-10 w-10 rounded-full" src="${data.not_added[0].user__avatar}" alt="">
                                </div>
                                <div class="flex-grow truncate">
                                    <div class="font-medium text-gray-900 dark:text-gray-300"> ${data.not_added[0].user__username}</div>
                                </div>
                                <div class="ms-auto">
                                    <dutton id="add-to-visitors-${data.not_added[0].id}" class=" px-3 py-1 rounded text-xs font-medium bg-primary/25 text-primary">Разрешить смотреть</dutton>
                                </div>
                                <div class="ms-auto">
                                    <dutton id="add-to-participants-${data.not_added[0].id}"  class=" px-3 py-1 rounded text-xs font-medium bg-success/25 text-success">Разрешить участвовать</dutton>
                                </div>
                            </div>
                        </div>
                    `;
                    not_addedList.insertAdjacentHTML('beforeend', primaryHTML);
                }
            }
            // Если происходит удаление участника
            else if (data.action === 'post_remove') {
                // Проверяем, есть ли участник с таким id в списке
                const existingNot_added = document.getElementById(`list-user-not_added-${data.not_added[0].id}`);
                // Если участник с таким id есть, удаляем его
                if (existingNot_added) {
                    existingNot_added.remove();
                }
            }
        }
        else if (data.type === 'user_update_settings') {
            // Мои кнопки, публичные значки, кнопки
            // Получение элементов кнопок звука и видео для данного пользователя
            const soundButton = document.getElementById(`mybutton-sound-${data.user_updates[0].id}`);
            const videoButton = document.getElementById(`mybutton-video-${data.user_updates[0].id}`);
            const handButton = document.getElementById(`mybutton-hand-${data.user_updates[0].id}`);
            const saveButton = document.getElementById(`mybutton-video-${data.user_updates[0].id}`);
            const desktopButton = document.getElementById(`mybutton-video-${data.user_updates[0].id}`);

            // Проверка, есть ли такие кнопки
            if (soundButton && videoButton) {
                // Проверяем состояние звука и видео для данного пользователя
                const userUpdates = data.user_updates[0];
                // Проверяем состояние звука
                if (userUpdates.sound === false) {
                    // Если звук выключен, меняем классы кнопки звука на bg-light
                    soundButton.classList.remove('bg-success', 'text-white');
                    soundButton.classList.add('bg-danger', 'text-white');
                    soundButton.disabled = false;
                }  else if (userUpdates.sound_root === true) {
                    // Если звук включен и пользователь является спикером, добавляем класс bg-dark и атрибут disabled
                    soundButton.classList.remove('bg-success', 'text-white', 'bg-danger');
                    soundButton.classList.add('bg-dark', 'text-white');
                    soundButton.disabled = true; // Добавляем атрибут disabled
                } else if (userUpdates.sound === true) {
                    // Если звук включен, меняем классы кнопки звука на исходные bg-danger и text-white
                    soundButton.classList.remove('bg-danger', 'text-white', 'bg-dark');
                    soundButton.classList.add('bg-success', 'text-white');
                    soundButton.disabled = false;
                }
                //кнопки видео
                if (userUpdates.video === false) {
                    // Если звук выключен, меняем классы кнопки звука на bg-light
                    videoButton.classList.remove('bg-success', 'text-white');
                    videoButton.classList.add('bg-danger', 'text-white');
                    videoButton.disabled = false;
                }  else if (userUpdates.video_root === true) {
                    // Если звук включен и пользователь является спикером, добавляем класс bg-dark и атрибут disabled
                    videoButton.classList.remove('bg-success', 'text-white', 'bg-danger');
                    videoButton.classList.add('bg-dark', 'text-white');
                    videoButton.disabled = true; // Добавляем атрибут disabled
                } else if (userUpdates.video === true) {
                    // Если звук включен, меняем классы кнопки звука на исходные bg-danger и text-white
                    videoButton.classList.remove('bg-danger', 'text-white', 'bg-dark');
                    videoButton.classList.add('bg-success', 'text-white');
                    videoButton.disabled = false;
                }
                // Проверяем состояние видео
                if (userUpdates.video === false) {
                    // Если видео выключено, меняем классы кнопки видео на bg-light
                    handButton.classList.remove('bg-success', 'text-white');
                    handButton.classList.add('bg-danger', 'text-white');
                } else {
                    // Если видео включено, меняем классы кнопки видео на исходные bg-danger и text-white
                    handButton.classList.remove('bg-danger', 'text-white');
                    handButton.classList.add('bg-success', 'text-white');
                }
            }
        }
    };

    document.querySelector('#send-button').onclick = function (e) {
        e.preventDefault();
        const message = document.querySelector('#leading-button-add-on-multiple-add-ons');
        const text = message.value;
        console.log(text);
        if (text.trim() !== '') {
            messageSocket.send(JSON.stringify({
                'text': text
            }));
            message.value = '';
        }
    };
    // Проверяем соответствие data-my-id и data-spiker
    const myId = document.querySelector('main').getAttribute('data-my-id');
    const spikerSections = document.querySelectorAll('[data-spiker]');
    spikerSections.forEach(section => {
        if (section.getAttribute('data-spiker') === myId) {
            section.style.display = 'inline-flex';
        }
    });
});