// Размеры экранов
function resetAndAdjustGridItems() {
    const container = document.querySelector('.grid-container'); // Контейнер грида
    const items = Array.from(container.children); // Все элементы внутри контейнера

    // Сбрасываем стили элементов
    items.forEach(item => {
        item.style.removeProperty('height');
        item.style.removeProperty('width');
        item.style.removeProperty('minHeight');
        item.style.removeProperty('minWidth');
        item.style.removeProperty('maxWidth');
    });

    // Пересчитываем стили
    adjustGridItems();
}

// Функция для сброса стилей и пересчета элементов при загрузке страницы
function adjustGridItems() {
    const container = document.querySelector('.grid-container'); // Контейнер грида
    const items = Array.from(container.children); // Все элементы внутри контейнера

    // Проверяем, есть ли элементы с data-primary="primary"
    const primaryItems = items.filter(item => item.getAttribute('data-primary') === 'primary');

    // Создаем контейнер для не-primary элементов под основным контейнером
    let nonPrimaryContainer = document.querySelector('.grid-container-secondary');
    if (!nonPrimaryContainer) {
        nonPrimaryContainer = document.createElement('div');
        nonPrimaryContainer.className = 'grid-container-secondary';
        container.appendChild(nonPrimaryContainer); // Добавляем под-контейнер внутри grid-container
    } else {
        // Перемещаем контейнер в конец основного контейнера, если он уже существует
        container.appendChild(nonPrimaryContainer);
    }

    if (primaryItems.length > 0) {
        // Если есть элементы с data-primary="primary", распределяем их, как указано ранее
        const primaryCount = primaryItems.length;

        for (let item of items) {
            if (item.getAttribute('data-primary') === 'primary') {
                // Стили в зависимости от количества primary элементов
                if (primaryCount == 1) {
                    item.style.height = 'calc(100% - 100px)';
                    item.style.width = '100%';
                } else if (primaryCount == 2) {
                    item.style.height = 'calc(100% - 100px)';
                    item.style.width = '50%';
                } else if (primaryCount > 2 && primaryCount <= 4) {
                    item.style.height = 'calc(50% - 100px)';
                    item.style.width = '50%';
                } else if (primaryCount > 4 && primaryCount <= 6) {
                    item.style.height = 'calc(50% - 100px)';
                    item.style.width = '33%';
                } else if (primaryCount > 6 && primaryCount <= 9) {
                    item.style.height = 'calc(33% - 100px)';
                    item.style.width = '33%';
                } else if (primaryCount > 9 && primaryCount <= 12) {
                    item.style.height = 'calc(33% - 100px)';
                    item.style.width = '24%';
                } else if (primaryCount > 12 && primaryCount <= 16) {
                    item.style.height = 'calc(33% - 100px)';
                    item.style.width = '25%';
                }
            }
        }

        // Перемещаем не-primary элементы в отдельный контейнер
        for (let item of items) {
            if (!primaryItems.includes(item)) {
                item.style.minHeight = '100px';
                item.style.minWidth = '100px';
                item.style.maxWidth = '100px';
                nonPrimaryContainer.appendChild(item); // Перемещаем в новый контейнер
            }
        }
    } else {
        // Если нет primary элементов, распределяем их в зависимости от количества элементов
        const itemCount = items.length;

        for (let item of items) {
            if (itemCount == 1) {
                item.style.height = '100%';
                item.style.width = '100%';
            } else if (itemCount == 2) {
                item.style.height = '100%';
                item.style.width = '50%';
            } else if (itemCount > 2 && itemCount <= 4) {
                item.style.height = '50%';
                item.style.width = '50%';
            } else if (itemCount > 4 && itemCount <= 6) {
                item.style.height = '50%';
                item.style.width = '33%';
            } else if (itemCount > 6 && itemCount <= 9) {
                item.style.height = '33%';
                item.style.width = '33%';
            } else if (itemCount > 9 && itemCount <= 12) {
                item.style.height = '33%';
                item.style.width = '24%';
            } else if (itemCount > 12 && itemCount <= 16) {
                item.style.height = '25%';
                item.style.width = '25%';
            }
        }
    }
}

// Запуск функции при загрузке страницы
document.addEventListener('DOMContentLoaded', adjustGridItems);


//*************//


// Изменение состояния закрытия конференции
document.getElementById("toggle-closed").addEventListener("click", function() {
    fetch(conferenceContext.toggleStatusUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": conferenceContext.csrfToken,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "field=is_closed",
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
});

// Изменение состояния начала конференции
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("toggle-start").addEventListener("click", function() {
        fetch(conferenceContext.toggleStatusUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: "field=is_start",
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error: ${response.status} - ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === "ok") {
                } else {
                    console.error(data.message);
                }
            })
            .catch(error => {
                console.error("An error occurred:", error);
            });
    });
});


// Добавление пользователя в посетители
document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой добавления в посетители или участники
    if (event.target.matches("[id^='add-to-visitors-']") || event.target.matches("[id^='add-to-participants-']")) {
        // Получаем id пользователя из id кнопки
        const userId = event.target.id.split("-").pop();
        // Определяем группу, в которую нужно добавить пользователя
        const group = event.target.id.includes('visitors') ? 'visitors' : 'participants';
        // Отправляем POST запрос для добавления пользователя в группу
        fetch(conferenceContext.addUserToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&group=${group}`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Обработка успешного ответа, если необходимо
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});

// Добавление пользователя в участники
document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой добавления в участники
    if (event.target.matches("[id^='add-to-participants-']")) {
        // Получаем id пользователя из id кнопки
        const userId = event.target.id.split("-").pop();
        // Отправляем POST запрос для добавления пользователя в группу участников
        fetch(conferenceContext.addUserToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&group=participants`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Обработка успешного ответа, если необходимо
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});


// Кнопки управления как spiker
document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой управления участниками
    if (event.target.matches("[id^='participants-']")) {
        // Получаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();
        let field;  // Поле, которое нужно переключить

        // Определяем поле в зависимости от id кнопки
        if (event.target.id.includes("hand")) {
            field = "hand";
        } else if (event.target.id.includes("sound")) {
            field = "sound_root";
        } else if (event.target.id.includes("saved_video")) {
            field = "saved_video";
        } else if (event.target.id.includes("video")) {
            field = "video_root";
        }

        // Отправляем POST запрос для переключения поля участника
        fetch(`/toggle_user_field/${userId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `field=${field}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                console.log(`Поле '${field}' пользователя с id ${userId} обновлено.`);
                // Обновляем состояние кнопки в зависимости от нового значения
                if (data.new_value === false) {
                    // Если значение false, добавить класс 'bg-danger' и удалить класс 'bg-dark'
                    event.target.classList.add('bg-danger');
                    event.target.classList.remove('bg-dark');
                } else {
                    // Если значение не false, добавить класс 'bg-dark' и удалить класс 'bg-danger'
                    event.target.classList.add('bg-dark');
                    event.target.classList.remove('bg-danger');
                }
            } else {
                console.error(`Ошибка при обновлении поля: ${data.message}`);
            }
        })
        .catch(error => {
            console.error(`Ошибка при отправке запроса: ${error}`);
        });
    }
});


// Перемещать из participants
document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой управления удалением участников
    if (event.target.matches("[id^='noparticipants-']")) {
        // Получаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();

        // Отправляем POST запрос для удаления участника
        fetch(conferenceContext.UpdateToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&action=remove_participant`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Обработка успешного удаления участника
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});

document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой управления добавлением участников
    if (event.target.matches("[id^='not_added-']")) {
        // Получаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();

        // Отправляем POST запрос для добавления участника
        fetch(conferenceContext.UpdateToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&action=add_to_not_added`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Обработка успешного добавления участника
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});

document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой управления закреплением участника
    if (event.target.matches("[id^='pin-']")) {
        // Получаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();

        // Отправляем POST запрос для выполнения действия по закреплению участника
        fetch(conferenceContext.UpdateToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&action=pin_primary`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Обработка успешного выполнения действия
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});


// Мои кнопки
document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой управления для пользователя
    if (event.target.matches("[id^='mybutton-']")) {
        // Получаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();
        let field;  // Поле, которое нужно переключить

        // Определяем поле в зависимости от id кнопки
        if (event.target.id.includes("hand")) {
            field = "hand";
        } else if (event.target.id.includes("sound")) {
            field = "sound";
        } else if (event.target.id.includes("desktop")) {
            field = "desktop";
        } else if (event.target.id.includes("video")) {
            field = "video";
        }

        // Отправляем POST запрос для выполнения действия по изменению поля
        fetch(`/toggle_myuser_field/${userId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `field=${field}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                console.log(`Поле '${field}' пользователя с id ${userId} обновлено.`);
                // Обновляем состояние кнопки в зависимости от нового значения
                // Например, изменяем стиль или класс кнопки
                event.target.classList.toggle("bg-danger", data.new_value);
            } else {
                console.error(`Ошибка при обновлении поля: ${data.message}`);
            }
        })
        .catch(error => {
            console.error(`Ошибка при отправке запроса: ${error}`);
        });
    }
});

// Мои статус (Перемещать из participants)
// Обработчик клика на кнопках для удаления участника
document.addEventListener('click', function(event) {
    // Проверяем, является ли целевой элемент кнопкой для удаления участника
    if (event.target.matches("[id^='mybutton_noparticipants-']")) {
        // Получаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();

        // Отправляем POST запрос для удаления участника
        fetch(conferenceContext.UpdateToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&action=remove_participant`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Действие выполнено успешно
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});

// Делегирование событий для кнопок "add_to_not_added"
document.addEventListener("click", function(event) {
    // Проверяем, является ли целевой элемент кнопкой "add_to_not_added"
    if (event.target.matches("[id^='mybutton_not_added-']")) {
        // Извлекаем user_id из id кнопки
        const userId = event.target.id.split("-").pop();

        // Отправляем POST запрос для добавления пользователя в список не добавленных
        fetch(conferenceContext.UpdateToGroupUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": conferenceContext.csrfToken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_id=${userId}&action=add_to_not_added`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                // Успешно выполнено
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('An error occurred:', error);
        });
    }
});

//Чат
document.querySelector('#send-button').addEventListener('click', function() {
    const videochatId = this.getAttribute('data-videochat-id');  // Получаем videochatId
    const messageInput = document.querySelector('#leading-button-add-on-multiple-add-ons');  // Поле ввода
    const messageContent = messageInput.value;  // Содержание сообщения

    fetch(`/videochat/${videochatId}/send-message/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": conferenceContext.csrfToken,
        },
        body: `content=${messageContent}`,
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
        })
        .then(data => {
            if (data.status === 'ok') {
                console.log(data.message);  // Сообщение отправлено
                messageInput.value = '';  // Очистка поля ввода после отправки
            } else {
                console.error(data.message);  // Ошибка в отправке
            }
        })
        .catch(error => {
            console.error('Произошла ошибка:', error);
        });
});