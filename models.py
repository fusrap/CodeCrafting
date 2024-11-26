from typing import List, Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = 'Role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK__Role__3213E83FEB9E9ABD'),
        Index('UQ__Role__863D214802F60D37', 'role', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))

    Account: Mapped[List['Account']] = relationship('Account', back_populates='role')


class Account(Base):
    __tablename__ = 'Account'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['Role.id'], name='FK__Account__role_id__09A971A2'),
        PrimaryKeyConstraint('account_id', name='PK__Account__46A222CD0A2E90A9'),
        Index('UQ__Account__AB6E6164A0619D05', 'email', unique=True),
        Index('ac_email_index', 'email')
    )

    account_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))
    email: Mapped[str] = mapped_column(String(180, 'SQL_Latin1_General_CP1_CI_AS'))
    password: Mapped[str] = mapped_column(String(255, 'SQL_Latin1_General_CP1_CI_AS'))
    role_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('(getdate())'))

    role: Mapped['Role'] = relationship('Role', back_populates='Account')
