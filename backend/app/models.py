from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    TIMESTAMP,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    subscription_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1"),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    server_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    port: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("443"),
    )

    encryption: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("''"),
    )

    flow: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        server_default=text("'xtls-rprx-vision'"),
    )

    transport_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'tcp'"),
    )

    security: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'reality'"),
    )

    sni: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    fingerprint: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        server_default=text("'chrome'"),
    )

    reality_public_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    reality_short_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    alpn: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        server_default=text("'h2'"),
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1"),
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        Index(
            "idx_servers_enabled_sort",
            "enabled",
            "sort_order",
        ),
    )


class ServerUser(Base):
    __tablename__ = "server_users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    server_pk: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "servers.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )

    user_pk: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )

    uuid: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1"),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint(
            "server_pk",
            "user_pk",
            name="uq_server_users_server_user",
        ),
        UniqueConstraint(
            "server_pk",
            "uuid",
            name="uq_server_users_server_uuid",
        ),
        Index(
            "idx_server_users_user",
            "user_pk",
            "enabled",
        ),
    )
