"""add team invitations (memory-first; not applied while Postgres is down)

Revision ID: a1b2c3d4e5f6
Revises: 6c0d96e3d69b
Create Date: 2026-08-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "6c0d96e3d69b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner", sa.String(), nullable=False),
    )
    op.create_table(
        "team_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("principal_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
    )
    op.create_index(
        "uq_team_memberships_team_principal",
        "team_memberships",
        ["team_id", "principal_id"],
        unique=True,
    )
    op.create_table(
        "team_invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("invited_email", sa.String(), nullable=False),
        sa.Column("invited_email_normalized", sa.String(), nullable=False),
        sa.Column("invited_by", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("uq_team_invitations_token", "team_invitations", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_team_invitations_token", table_name="team_invitations")
    op.drop_table("team_invitations")
    op.drop_index("uq_team_memberships_team_principal", table_name="team_memberships")
    op.drop_table("team_memberships")
    op.drop_table("teams")
