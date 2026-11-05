from urllib.parse import quote, urlencode

from app.models import Server, User


def build_vless_url(
    *,
    server: Server,
    user: User,
    uuid: str,
    custom_name: str | None = None,
) -> str:
    params: list[tuple[str, str]] = []

    if server.alpn is not None:
        params.append(("alpn", server.alpn))

    params.append(("encryption", server.encryption or "none"))

    if server.flow is not None:
        params.append(("flow", server.flow))

    if server.fingerprint is not None:
        params.append(("fp", server.fingerprint))

    if server.reality_public_key is not None:
        params.append(("pbk", server.reality_public_key))

    params.append(("security", server.security))

    if server.reality_short_id is not None:
        params.append(("sid", server.reality_short_id))

    if server.sni is not None:
        params.append(("sni", server.sni))

    params.append(("type", server.transport_type))

    query = urlencode(params)

    node_name = custom_name or f"{server.server_id}-{user.user_id}"

    fragment = quote(
        node_name,
        safe="",
    )

    return (
        f"vless://{uuid}@{server.host}:{server.port}"
        f"?{query}"
        f"#{fragment}"
    )
