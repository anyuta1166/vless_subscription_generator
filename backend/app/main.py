from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.responses import PlainTextResponse
from fastapi.responses import RedirectResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Server, ServerUser, User
from app.vless import build_vless_url
from app.admin.assignments import router as admin_assignments_router
from app.admin.routes import router as admin_users_router
from app.admin.servers import router as admin_servers_router

app = FastAPI(
    title="VLESS Subscription Backend",
    docs_url=None,
    redoc_url=None,
)


app.include_router(admin_users_router)
app.include_router(admin_servers_router)
app.include_router(admin_assignments_router)

@app.get("/admin/", include_in_schema=False)
async def admin_root():
    return RedirectResponse(
        url="/admin/users",
        status_code=302,
    )


SubscriptionToken = Annotated[
    str,
    Path(
        pattern=r"^[0-9a-f]{64}$",
        description="64-character hexadecimal subscription token",
    ),
]


@app.get("/health")
async def health(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await db.execute(text("SELECT 1"))

    return {
        "status": "ok",
    }


@app.get(
    "/sub/{token}",
    response_class=PlainTextResponse,
)
async def subscription(
    token: SubscriptionToken,
    db: AsyncSession = Depends(get_db),
) -> PlainTextResponse:
    stmt = (
        select(
            User,
            Server,
            ServerUser.uuid,
            ServerUser.custom_name,
        )
        .join(
            ServerUser,
            ServerUser.user_pk == User.id,
        )
        .join(
            Server,
            Server.id == ServerUser.server_pk,
        )
        .where(
            User.subscription_token == token,
            User.enabled.is_(True),
            ServerUser.enabled.is_(True),
            Server.enabled.is_(True),
        )
        .order_by(
            Server.sort_order,
            Server.server_id,
        )
    )

    result = await db.execute(stmt)

    rows = result.all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    links = [
        build_vless_url(
            user=user,
            server=server,
            uuid=uuid,
            custom_name=custom_name,
        )
        for user, server, uuid, custom_name in rows
    ]

    body = "\n".join(links) + "\n"

    return PlainTextResponse(
        content=body,
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-store",
        },
    )
