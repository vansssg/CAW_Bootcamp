"""init_schema

Revision ID: 6c0d96e3d69b
Revises:
Create Date: 2026-08-07 22:23:49.061727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision: str = "6c0d96e3d69b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("short_code", sa.String(), nullable=False),
        sa.Column("original_url", sa.String(), nullable=False),
        sa.Column("created_by", sa.String(), nullable=False),
    )

    op.create_index(
        "ix_links_short_code",
        "links",
        ["short_code"],
        unique=True,
    )

    op.create_index(
        "ix_links_created_by",
        "links",
        ["created_by"],
    )

    op.create_table(
        "click_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "link_id",
            sa.Integer(),
            sa.ForeignKey("links.id"),
            nullable=False,
        ),
        sa.Column(
            "clicked_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_click_events_link_id_clicked_at",
        "click_events",
        ["link_id", "clicked_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_click_events_link_id_clicked_at",
        table_name="click_events",
    )
    op.drop_table("click_events")

    op.drop_index(
        "ix_links_created_by",
        table_name="links",
    )
    op.drop_index(
        "ix_links_short_code",
        table_name="links",
    )
    op.drop_table("links")