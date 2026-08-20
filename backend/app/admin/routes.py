import re
import secrets

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User


router = APIRouter(
    prefix="/admin/users",
    tags=["admin-users"],
)

templates = Jinja2Templates(
    directory="app/templates",
)


USER_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def generate_subscription_token() -> str:
    return secrets.token_hex(32)


async def get_user(
    db: AsyncSession,
    user_pk: int,
) -> User:
    user = await db.get(User, user_pk)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


def validate_user_id(user_id: str) -> str | None:
    if not USER_ID_RE.fullmatch(user_id):
        return (
            "user_id должен содержать только "
            "a-z, 0-9, точку, '_' или '-'"
        )

    return None


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


@router.get(
    "",
    response_class=HTMLResponse,
)
async def users_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .order_by(User.display_name, User.user_id)
    )

    users = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="users/list.html",
        context={
            "users": users,
            "public_base_url": settings.public_base_url.rstrip("/"),
        },
    )


@router.get(
    "/new",
    response_class=HTMLResponse,
)
async def user_new(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="users/form.html",
        context={
            "user": None,
            "error": None,
        },
    )


@router.post(
    "/new",
    response_class=HTMLResponse,
)
async def user_create(
    request: Request,
    user_id: str = Form(...),
    display_name: str = Form(...),
    email: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user_id = user_id.strip().lower()
    display_name = display_name.strip()
    email = email.strip()

    error = validate_user_id(user_id)

    if not display_name:
        error = "display_name не может быть пустым"

    if not email:
        error = "email не может быть пустым"

    if error:
        return templates.TemplateResponse(
            request=request,
            name="users/form.html",
            context={
                "user": {
                    "user_id": user_id,
                    "display_name": display_name,
                    "email": email,
                    "enabled": True,
                },
                "error": error,
            },
            status_code=400,
        )

    user = User(
        user_id=user_id,
        display_name=display_name,
        email=email,
        subscription_token=generate_subscription_token(),
        enabled=True,
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="users/form.html",
            context={
                "user": {
                    "user_id": user_id,
                    "display_name": display_name,
                    "email": email,
                    "enabled": True,
                },
                "error": (
                    "Пользователь с таким user_id, email "
                    "или subscription token уже существует"
                ),
            },
            status_code=409,
        )

    return RedirectResponse(
        url="/admin/users",
        status_code=303,
    )


@router.get(
    "/{user_pk}/edit",
    response_class=HTMLResponse,
)
async def user_edit(
    request: Request,
    user_pk: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_pk)

    return templates.TemplateResponse(
        request=request,
        name="users/form.html",
        context={
            "user": user,
            "error": None,
        },
    )


@router.post(
    "/{user_pk}/edit",
    response_class=HTMLResponse,
)
async def user_update(
    request: Request,
    user_pk: int,
    user_id: str = Form(...),
    display_name: str = Form(...),
    email: str = Form(...),
    enabled: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_pk)

    user_id = user_id.strip().lower()
    display_name = display_name.strip()
    email = email.strip()

    error = validate_user_id(user_id)

    if not display_name:
        error = "display_name не может быть пустым"

    if not email:
        error = "email не может быть пустым"

    if error:
        return templates.TemplateResponse(
            request=request,
            name="users/form.html",
            context={
                "user": {
                    "id": user_pk,
                    "user_id": user_id,
                    "display_name": display_name,
                    "email": email,
                    "enabled": enabled,
                    "subscription_token": user.subscription_token,
                },
                "error": error,
            },
            status_code=400,
        )

    user.user_id = user_id
    user.display_name = display_name
    user.email = email
    user.enabled = enabled

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="users/form.html",
            context={
                "user": {
                    "id": user_pk,
                    "user_id": user_id,
                    "display_name": display_name,
                    "email": email,
                    "enabled": enabled,
                    "subscription_token": user.subscription_token,
                },
                "error": (
                    "Пользователь с таким user_id "
                    "или email уже существует"
                ),
            },
            status_code=409,
        )

    return RedirectResponse(
        url="/admin/users",
        status_code=303,
    )


@router.post(
    "/{user_pk}/toggle",
)
async def user_toggle(
    request: Request,
    user_pk: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_pk)

    user.enabled = not user.enabled

    await db.commit()
    await db.refresh(user)

    if is_htmx(request):
        return templates.TemplateResponse(
            request=request,
            name="users/_row.html",
            context={
                "user": user,
                "public_base_url": settings.public_base_url.rstrip("/"),
            },
        )

    return RedirectResponse(
        url="/admin/users",
        status_code=303,
    )


@router.post(
    "/{user_pk}/rotate-token",
)
async def user_rotate_token(
    request: Request,
    user_pk: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_pk)

    user.subscription_token = generate_subscription_token()

    await db.commit()
    await db.refresh(user)

    if is_htmx(request):
        return templates.TemplateResponse(
            request=request,
            name="users/_row.html",
            context={
                "user": user,
                "public_base_url": settings.public_base_url.rstrip("/"),
            },
        )

    return RedirectResponse(
        url="/admin/users",
        status_code=303,
    )


@router.post(
    "/{user_pk}/delete",
)
async def user_delete(
    request: Request,
    user_pk: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_pk)

    await db.delete(user)
    await db.commit()

    if is_htmx(request):
        return Response(
            status_code=200,
            content="",
        )

    return RedirectResponse(
        url="/admin/users",
        status_code=303,
    )
