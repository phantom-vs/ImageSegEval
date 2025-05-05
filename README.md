# ImageSegEval

# FastAPI Image Segmentation Service

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4.0-red.svg)

Сервис для обработки изображений с возможностью:
- Загрузки и сегментации изображений
- Хранения результатов в базе данных
- Оценки качества сегментации
- Управления пользователями

### Установка
```bash
mkdir imageSeg
cd imageSeg
git clone https://github.com/phantom-vs/ImageSegEval.git
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Запуск
```bash
uvicorn app.main:app --reload
```

### Структура проекта
```
app/
├── database.py        # Настройки базы данных
├── models.py          # SQLAlchemy модели
├── schemas.py         # Pydantic схемы
├── crud.py            # Операции с БД
├── auth.py            # Аутентификация
├── main.py            # Основное приложение
├── segmentation.py    # Логика обработки изображений
├── config.py          # Конфигурация
├── static/            # Статические файлы
└── templates/         # HTML
```

### API Endpoints
#### Аутентификация:
- POST /login - Вход в систему
- POST /register - Регистрация
- POST /logout - Выход

#### Работа с изображениями:
- POST /api/upload - Загрузка изображения
- GET /api/original/{image_id} - Получение оригинала
- GET /api/segmented/{image_id} - Получение сегментированного изображения
- POST /api/feedback/{image_id} - Оценка качества

#### Управление пользователями:
- DELETE /api/user/by-username/{username} - Удаление пользователя

