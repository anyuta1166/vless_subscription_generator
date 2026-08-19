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

from app.database import get_db
from app.models import Server


router = APIRouter(
    prefix="/admin/servers",
    tags=["admin-servers"],
)

templates = Jinja2Templates(
    directory="app/templates",
)


async def get_server(
    db: AsyncSession,
    server_pk: int,
) -> Server:
    server = await db.get(Server, server_pk)

    if server is None:
        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )

    return server


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


@router.get(
    "",
    response_class=HTMLResponse,
)
async def servers_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Server)
        .order_by(
            Server.sort_order,
            Server.server_id,
        )
    )

    servers = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="servers/list.html",
        context={
            "servers": servers,
        },
    )


@router.get(
    "/new",
    response_class=HTMLResponse,
)
async def server_new(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="servers/form.html",
        context={
            "server": None,
            "error": None,
        },
    )


@router.post(
    "/new",
    response_class=HTMLResponse,
)
async def server_create(
    request: Request,

    server_id: str = Form(...),
    host: str = Form(...),
    port: int = Form(443),

    encryption: str = Form(""),
    flow: str = Form("xtls-rprx-vision"),
    transport_type: str = Form("tcp"),

    security: str = Form("reality"),
    sni: str = Form(""),
    fingerprint: str = Form("chrome"),

    reality_public_key: str = Form(""),
    reality_short_id: str = Form(""),

    alpn: str = Form("h2"),

    sort_order: int = Form(0),

    db: AsyncSession = Depends(get_db),
):
    server_id = server_id.strip().lower()
    host = host.strip()

    encryption = encryption.strip()
    flow = flow.strip()
    transport_type = transport_type.strip()

    security = security.strip()
    sni = sni.strip()
    fingerprint = fingerprint.strip()

    reality_public_key = reality_public_key.strip()
    reality_short_id = reality_short_id.strip()

    alpn = alpn.strip()

    error = None

    if not server_id:
        error = "server_id не может быть пустым"

    if not host:
        error = "host не может быть пустым"

    if port < 1 or port > 65535:
        error = "port должен быть в диапазоне 1–65535"

    if error:
        return templates.TemplateResponse(
            request=request,
            name="servers/form.html",
            context={
                "server": {
                    "server_id": server_id,
                    "host": host,
                    "port": port,
                    "encryption": encryption,
                    "flow": flow,
                    "transport_type": transport_type,
                    "security": security,
                    "sni": sni,
                    "fingerprint": fingerprint,
                    "reality_public_key": reality_public_key,
                    "reality_short_id": reality_short_id,
                    "alpn": alpn,
                    "sort_order": sort_order,
                    "enabled": True,
                },
                "error": error,
            },
            status_code=400,
        )

    server = Server(
        server_id=server_id,
        host=host,
        port=port,
        encryption=encryption,
        flow=flow or None,
        transport_type=transport_type,
        security=security,
        sni=sni or None,
        fingerprint=fingerprint or None,
        reality_public_key=reality_public_key or None,
        reality_short_id=reality_short_id or None,
        alpn=alpn or None,
        sort_order=sort_order,
        enabled=True,
    )

    db.add(server)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="servers/form.html",
            context={
                "server": {
                    "server_id": server_id,
                    "host": host,
                    "port": port,
                    "encryption": encryption,
                    "flow": flow,
                    "transport_type": transport_type,
                    "security": security,
                    "sni": sni,
                    "fingerprint": fingerprint,
                    "reality_public_key": reality_public_key,
                    "reality_short_id": reality_short_id,
                    "alpn": alpn,
                    "sort_order": sort_order,
                    "enabled": True,
                },
                "error": "Сервер с таким server_id уже существует",
            },
            status_code=409,
        )

    return RedirectResponse(
        url="/admin/servers",
        status_code=303,
    )


@router.get(
    "/{server_pk}/edit",
    response_class=HTMLResponse,
)
async def server_edit(
    request: Request,
    server_pk: int,
    db: AsyncSession = Depends(get_db),
):
    server = await get_server(
        db,
        server_pk,
    )

    return templates.TemplateResponse(
        request=request,
        name="servers/form.html",
        context={
            "server": server,
            "error": None,
        },
    )


@router.post(
    "/{server_pk}/edit",
    response_class=HTMLResponse,
)
async def server_update(
    request: Request,
    server_pk: int,

    server_id: str = Form(...),
    host: str = Form(...),
    port: int = Form(443),

    encryption: str = Form(""),
    flow: str = Form("xtls-rprx-vision"),
    transport_type: str = Form("tcp"),

    security: str = Form("reality"),
    sni: str = Form(""),
    fingerprint: str = Form("chrome"),

    reality_public_key: str = Form(""),
    reality_short_id: str = Form(""),

    alpn: str = Form("h2"),

    sort_order: int = Form(0),
    enabled: bool = Form(False),

    db: AsyncSession = Depends(get_db),
):
    server = await get_server(
        db,
        server_pk,
    )

    server_id = server_id.strip().lower()
    host = host.strip()

    encryption = encryption.strip()
    flow = flow.strip()
    transport_type = transport_type.strip()

    security = security.strip()
    sni = sni.strip()
    fingerprint = fingerprint.strip()

    reality_public_key = reality_public_key.strip()
    reality_short_id = reality_short_id.strip()

    alpn = alpn.strip()

    error = None

    if not server_id:
        error = "server_id не может быть пустым"

    if not host:
        error = "host не может быть пустым"

    if port < 1 or port > 65535:
        error = "port должен быть в диапазоне 1–65535"

    if error:
        return templates.TemplateResponse(
            request=request,
            name="servers/form.html",
            context={
                "server": {
                    "id": server_pk,
                    "server_id": server_id,
                    "host": host,
                    "port": port,
                    "encryption": encryption,
                    "flow": flow,
                    "transport_type": transport_type,
                    "security": security,
                    "sni": sni,
                    "fingerprint": fingerprint,
                    "reality_public_key": reality_public_key,
                    "reality_short_id": reality_short_id,
                    "alpn": alpn,
                    "sort_order": sort_order,
                    "enabled": enabled,
                },
                "error": error,
            },
            status_code=400,
        )

    server.server_id = server_id
    server.host = host
    server.port = port

    server.encryption = encryption
    server.flow = flow or None
    server.transport_type = transport_type

    server.security = security
    server.sni = sni or None
    server.fingerprint = fingerprint or None

    server.reality_public_key = reality_public_key or None
    server.reality_short_id = reality_short_id or None

    server.alpn = alpn or None

    server.sort_order = sort_order
    server.enabled = enabled

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="servers/form.html",
            context={
                "server": {
                    "id": server_pk,
                    "server_id": server_id,
                    "host": host,
                    "port": port,
                    "encryption": encryption,
                    "flow": flow,
                    "transport_type": transport_type,
                    "security": security,
                    "sni": sni,
                    "fingerprint": fingerprint,
                    "reality_public_key": reality_public_key,
                    "reality_short_id": reality_short_id,
                    "alpn": alpn,
                    "sort_order": sort_order,
                    "enabled": enabled,
                },
                "error": "Сервер с таким server_id уже существует",
            },
            status_code=409,
        )

    return RedirectResponse(
        url="/admin/servers",
        status_code=303,
    )


@router.post(
    "/{server_pk}/toggle",
)
async def server_toggle(
    request: Request,
    server_pk: int,
    db: AsyncSession = Depends(get_db),
):
    server = await get_server(
        db,
        server_pk,
    )

    server.enabled = not server.enabled

    await db.commit()
    await db.refresh(server)

    if is_htmx(request):
        return templates.TemplateResponse(
            request=request,
            name="servers/_row.html",
            context={
                "server": server,
            },
        )

    return RedirectResponse(
        url="/admin/servers",
        status_code=303,
    )


@router.post(
    "/{server_pk}/delete",
)
async def server_delete(
    request: Request,
    server_pk: int,
    db: AsyncSession = Depends(get_db),
):
    server = await get_server(
        db,
        server_pk,
    )

    await db.delete(server)
    await db.commit()

    if is_htmx(request):
        return Response(
            status_code=200,
            content="",
        )

    return RedirectResponse(
        url="/admin/servers",
        status_code=303,
    )
