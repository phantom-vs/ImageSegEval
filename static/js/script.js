//// Функция для отображения уведомлений
function showAlert(message, type = 'error') {
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) oldAlert.remove();

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.auth-container') || document.body;
    container.prepend(alertDiv);

    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// Обработчик формы регистрации
//document.getElementById('registerForm').addEventListener('submit', async function(e) {
//    e.preventDefault();
//    const form = e.target;
//    const formData = new FormData(form);
//
//    try {
//        const response = await fetch(form.action, {
//            method: 'POST',
//            body: formData
//        });
//
//        if (response.ok) {
//            window.location.href = '/login';
//        } else {
//            const error = await response.json();
//            // Создаем элемент ошибки
//            const errorDiv = document.createElement('div');
//            errorDiv.className = 'alert alert-error';
//            errorDiv.textContent = error.detail || 'Ошибка регистрации';
//            // Удаляем старую ошибку
//            const oldError = document.querySelector('.alert-error');
//            if (oldError) oldError.remove();
//            // Вставляем перед формой
//            form.parentNode.insertBefore(errorDiv, form);
//        }
//    } catch (err) {
//        alert('Ошибка сети: ' + err.message);
//    }
//});

// Обработчик выхода из системы
document.getElementById('logoutBtn')?.addEventListener('click', async function(e) {
    e.preventDefault();

    try {
        const response = await fetch('/logout', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/login';
        } else {
            showAlert('Ошибка при выходе из системы');
        }
    } catch (error) {
        showAlert('Ошибка сети при выходе: ' + error.message);
    }
});


// Функция отправки отзыва
async function sendFeedback(isGood) {
    const resultContainer = document.getElementById('resultContainer');
    const fileInput = document.getElementById('imageInput');
    const buttons = document.querySelectorAll('.btn-success, .btn-danger');

    try {
        // Блокируем кнопки
        buttons.forEach(btn => btn.disabled = true);

        const response = await fetch(`/api/feedback/${resultContainer.dataset.imageId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_good: isGood }),
            credentials: 'include'
        });

        if (!response.ok) throw new Error('Ошибка сервера');

        showFeedbackMessage(isGood ? 'Оценка принята' : 'Отзыв учтён', true);

        // Плавное скрытие
        resultContainer.style.opacity = '0';
        setTimeout(() => {
            resultContainer.style.display = 'none';
            fileInput.value = '';
        }, 300);

    } catch (error) {
        showFeedbackMessage(`Ошибка: ${error.message}`, false);
    } finally {
        buttons.forEach(btn => btn.disabled = false);
    }
}

// Функция показа сообщения
function showFeedbackMessage(text, isSuccess) {
    // Удаляем предыдущее сообщение если есть
    const oldMessage = document.getElementById('feedback-message');
    if (oldMessage) oldMessage.remove();

    // Создаем новое сообщение
    const message = document.createElement('div');
    message.id = 'feedback-message';
    message.className = isSuccess ? 'success' : 'error';
    message.textContent = text;
    document.body.appendChild(message);

    setTimeout(() => {
        message.classList.add('fade-out');
        setTimeout(() => message.remove(), 300);
    }, 3000);
}


// Обработчик формы загрузки
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const resultContainer = document.getElementById('resultContainer');
    const fileInput = document.getElementById('imageInput');

    // Сбрасываем состояние контейнера перед новой загрузкой
    resultContainer.style.display = 'block';
    resultContainer.style.opacity = '1';

    try {
        const formData = new FormData(this);
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });

        if (!response.ok) throw new Error('Ошибка загрузки');

        const data = await response.json();

        // Обновляем контейнер с новыми данными
        resultContainer.dataset.imageId = data.id;
        document.getElementById('originalImage').src = `/api/original/${data.id}?t=${Date.now()}`;
        document.getElementById('segmentedImage').src = `/api/segmented/${data.id}?t=${Date.now()}`;
        resultContainer.style.display = 'block';

    } catch (error) {
        console.error('Ошибка:', error);
        showFeedbackMessage(`Ошибка загрузки: ${error.message}`, false);
    }
});

