from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    short_code = Column(String, nullable=False)
    original_url = Column(String, nullable=False)
    created_by = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_links_short_code", "short_code", unique=True),
        Index("ix_links_created_by", "created_by"),
    )


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False)
    clicked_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index(
            "ix_click_events_link_id_clicked_at",
            "link_id",
            "clicked_at",
        ),
    )


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)


class TeamMembership(Base):
    __tablename__ = "team_memberships"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    principal_id = Column(String, nullable=False)
    role = Column(String, nullable=False)

    __table_args__ = (Index("uq_team_memberships_team_principal", "team_id", "principal_id", unique=True),)


class TeamInvitation(Base):
    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    invited_email = Column(String, nullable=False)
    invited_email_normalized = Column(String, nullable=False)
    invited_by = Column(String, nullable=False)
    role = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (Index("uq_team_invitations_token", "token", unique=True),)