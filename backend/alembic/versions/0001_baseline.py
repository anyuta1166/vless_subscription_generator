"""Create the initial database schema.

Revision ID: 0001_baseline
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "subscription_token",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_users_user_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint(
            "subscription_token",
            name="uq_users_subscription_token",
        ),
        mysql_engine="InnoDB",
    )

    op.create_table(
        "servers",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("server_id", sa.String(length=64), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.Column(
            "port",
            mysql.SMALLINT(unsigned=True),
            server_default=sa.text("443"),
            nullable=False,
        ),
        sa.Column(
            "encryption",
            sa.String(length=32),
            server_default=sa.text("''"),
            nullable=False,
        ),
        sa.Column(
            "flow",
            sa.String(length=64),
            server_default=sa.text("'xtls-rprx-vision'"),
            nullable=True,
        ),
        sa.Column(
            "transport_type",
            sa.String(length=32),
            server_default=sa.text("'tcp'"),
            nullable=False,
        ),
        sa.Column(
            "security",
            sa.String(length=32),
            server_default=sa.text("'reality'"),
            nullable=False,
        ),
        sa.Column("sni", sa.String(length=255), nullable=True),
        sa.Column(
            "fingerprint",
            sa.String(length=64),
            server_default=sa.text("'chrome'"),
            nullable=True,
        ),
        sa.Column(
            "reality_public_key",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "reality_short_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "alpn",
            sa.String(length=255),
            server_default=sa.text("'h2'"),
            nullable=True,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", name="uq_servers_server_id"),
        mysql_engine="InnoDB",
    )
    op.create_index(
        "idx_servers_enabled_sort",
        "servers",
        ["enabled", "sort_order"],
        unique=False,
    )

    op.create_table(
        "server_users",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "server_pk",
            mysql.BIGINT(unsigned=True),
            nullable=False,
        ),
        sa.Column(
            "user_pk",
            mysql.BIGINT(unsigned=True),
            nullable=False,
        ),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column(
            "enabled",
            sa.Boolean(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["server_pk"],
            ["servers.id"],
            name="fk_server_users_server",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_pk"],
            ["users.id"],
            name="fk_server_users_user",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "server_pk",
            "user_pk",
            name="uq_server_users_server_user",
        ),
        sa.UniqueConstraint(
            "server_pk",
            "uuid",
            name="uq_server_users_server_uuid",
        ),
        mysql_engine="InnoDB",
    )
    op.create_index(
        "idx_server_users_user",
        "server_users",
        ["user_pk", "enabled"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_server_users_user",
        table_name="server_users",
    )
    op.drop_table("server_users")

    op.drop_index(
        "idx_servers_enabled_sort",
        table_name="servers",
    )
    op.drop_table("servers")

    op.drop_table("users")
