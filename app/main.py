"""Основной модуль FastAPI приложения для обработки изображений.

Содержит:
- Маршруты для аутентификации и работы с пользователями
- API для загрузки и обработки изображений
- Middleware для проверки авторизации
"""

from fastapi import (Depends, FastAPI, File, Form, HTTPException, Request,
                     Response, UploadFile, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .config import settings
from .database import SessionLocal, engine, get_db
from .segmentation import segment_image

# Инициализация базы данных
models.Base.metadata.create_all(bind=engine)

# Создание приложения FastAPI
app = FastAPI()

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware для проверки аутентификации пользователя.

    Обрабатывает:
    - Проверку токена в куках или заголовках
    - Перенаправление неавторизованных пользователей
    - Валидацию JWT токена
    """
    if request.method == "OPTIONS" or request.url.path.startswith(
            ("/static", "/login", "/register")
    ):
        return await call_next(request)

    is_api_request = request.url.path.startswith('/api/')

    try:
        token = None
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            token = token_cookie.strip('"').replace("Bearer ", "")

        if not token:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1].strip('"')

        if not token:
            if is_api_request:
                return JSONResponse(
                    content={"detail": "Not authenticated"},
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            return RedirectResponse(url="/login")

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            username = payload.get("sub")
            if not username:
                raise JWTError("Invalid token payload")

            database_session = SessionLocal()
            try:
                user = crud.get_user(database_session, username=username)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )

                request.state.user = user
            finally:
                database_session.close()

        except JWTError as jwt_error:
            response = (
                RedirectResponse(url="/login")
                if not is_api_request
                else JSONResponse(
                    content={"detail": "Invalid token"},
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            )
            response.delete_cookie("access_token")
            return response

        return await call_next(request)

    except Exception as error:
        if is_api_request:
            return JSONResponse(
                content={"detail": "Internal server error"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return RedirectResponse(url="/login")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница приложения."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: int = 0):
    """Страница входа в систему."""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Неверный логин или пароль" if error else None
    })


@app.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        database_session: Session = Depends(get_db)
):
    """Обработка входа пользователя."""
    user = auth.authenticate_user(database_session, form_data.username,
                                  form_data.password)
    if not user:
        return RedirectResponse(
            url="/login?error=1",
            status_code=status.HTTP_302_FOUND
        )

    access_token = auth.create_access_token(data={"sub": user.username})

    response = RedirectResponse(
        url="/profile",
        status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600,
        secure=False,
        samesite="lax",
        path="/"
    )
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации нового пользователя."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        database_session: Session = Depends(get_db)
):
    """Обработка регистрации нового пользователя."""
    try:
        user_data = schemas.UserCreate(
            username=username,
            email=email,
            password=password,
            password_confirm=password_confirm
        )

        crud.create_user(database_session=database_session, user=user_data)
        return RedirectResponse(url="/login", status_code=303)

    except ValidationError as validation_error:
        error_msg = validation_error.errors()[0]['msg']
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error_msg.split(', ')[-1],
            "username": username,
            "email": email
        })

    except IntegrityError as integrity_error:
        error_msg = (
            "Пользователь с такими данными уже существует"
            if "username" in str(integrity_error) or "email" in str(integrity_error)
            else "Ошибка при регистрации"
        )

        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error_msg,
            "username": username,
            "email": email
        })

    except Exception as registration_error:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": f"Ошибка сервера: {str(registration_error)}",
            "username": username,
            "email": email
        })


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """Страница профиля пользователя."""
    if not hasattr(request.state, 'user'):
        response = RedirectResponse(
            url="/login",
            status_code=status.HTTP_302_FOUND
        )
        response.delete_cookie("access_token")
        return response

    user = request.state.user
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": {"username": user.username, "email": user.email}
    })


@app.post("/logout")
async def logout():
    """Выход пользователя из системы."""
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie("access_token")
    return response


@app.post("/api/upload")
async def upload_image(
        request: Request,
        file: UploadFile = File(...),
        database_session: Session = Depends(get_db)
):
    """Загрузка и обработка изображения."""
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Only images are allowed")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(413, "File too large")

    try:
        segmented_img = segment_image(contents)
        db_image = models.Segmentation(
            user_id=request.state.user.id,
            original_image=contents,
            segmented_image=segmented_img
        )
        database_session.add(db_image)
        database_session.commit()

        return {
            "id": db_image.id,
            "original_id": db_image.id,
            "segmented_id": db_image.id,
            "message": "File uploaded successfully"
        }

    except Exception as upload_error:
        database_session.rollback()
        raise HTTPException(500, f"Internal error: {str(upload_error)}") from upload_error


@app.get("/api/segmented/{image_id}")
async def get_segmented_image(
        image_id: int,
        database_session: Session = Depends(get_db)
):
    """Получение сегментированного изображения по ID."""
    image = database_session.query(models.Segmentation).filter(
        models.Segmentation.id == image_id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(content=image.segmented_image, media_type="image/jpeg")


@app.get("/api/original/{image_id}")
async def get_original_image(
        image_id: int,
        database_session: Session = Depends(get_db)
):
    """Получение оригинального изображения по ID."""
    image = database_session.query(models.Segmentation).filter(
        models.Segmentation.id == image_id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image.original_image, media_type="image/jpeg")


@app.post("/api/feedback/{image_id}")
async def save_feedback(
        image_id: int,
        feedback: schemas.FeedbackRequest,
        database_session: Session = Depends(get_db)
):
    """Сохранение оценки качества сегментации."""
    image = database_session.query(models.Segmentation).filter(
        models.Segmentation.id == image_id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image.is_good = feedback.is_good
    database_session.commit()

    return {"status": "success", "image_id": image_id}


@app.delete("/api/user/by-username/{username}")
async def delete_user_by_username(
        username: str,
        request: Request,
        database_session: Session = Depends(get_db)
):
    """Удаление пользователя по username."""
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="Not authenticated")

    current_user = request.state.user

    if current_user.username != username and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No permission to delete")

    db_user = crud.get_user(database_session, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        database_session.query(models.Segmentation).filter(
            models.Segmentation.user_id == db_user.id
        ).delete()
        database_session.delete(db_user)
        database_session.commit()

        if current_user.username == username:
            response = JSONResponse(
                content={"message": "User deleted successfully"},
                status_code=200
            )
            response.delete_cookie("access_token")
            return response

        return db_user

    except Exception as delete_error:
        database_session.rollback()
        raise HTTPException(status_code=500, detail=str(delete_error)) from delete_error
