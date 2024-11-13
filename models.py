from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, Identity, Index, Integer, LargeBinary, PrimaryKeyConstraint, TEXT, Table, Unicode
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class KanbanBoards(Base):
    __tablename__ = 'Kanban_Boards'
    __table_args__ = (
        PrimaryKeyConstraint('board_id', name='PK__Kanban_B__FB1C96E9B9F469A1'),
    )

    board_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    title: Mapped[str] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    description: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))

    Kanban_Columns: Mapped[List['KanbanColumns']] = relationship('KanbanColumns', back_populates='board')


class KanbanCardTypes(Base):
    __tablename__ = 'Kanban_Card_Types'
    __table_args__ = (
        PrimaryKeyConstraint('card_type_id', name='PK__Kanban_C__58E28D4CD28F6C46'),
        Index('UQ__Kanban_C__E3F852487BCE862D', 'type', unique=True)
    )

    card_type_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    type: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))

    Kanban_Cards: Mapped[List['KanbanCards']] = relationship('KanbanCards', back_populates='card_type')


class Sysdiagrams(Base):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (
        PrimaryKeyConstraint('diagram_id', name='PK__sysdiagr__C2B05B61D0FA91E4'),
        Index('UK_principal_name', 'principal_id', 'name', unique=True)
    )

    name: Mapped[str] = mapped_column(Unicode(128, 'SQL_Latin1_General_CP1_CI_AS'))
    principal_id: Mapped[int] = mapped_column(Integer)
    diagram_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    version: Mapped[Optional[int]] = mapped_column(Integer)
    definition: Mapped[Optional[bytes]] = mapped_column(LargeBinary)


class KanbanColumns(Base):
    __tablename__ = 'Kanban_Columns'
    __table_args__ = (
        ForeignKeyConstraint(['board_id'], ['Kanban_Boards.board_id'], ondelete='CASCADE', name='FK__Kanban_Co__board__505BE5AD'),
        PrimaryKeyConstraint('column_id', name='PK__Kanban_C__E301851F6F715F2C')
    )

    column_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    title: Mapped[str] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    board_id: Mapped[Optional[int]] = mapped_column(Integer)
    position: Mapped[Optional[int]] = mapped_column(Integer)

    board: Mapped['KanbanBoards'] = relationship('KanbanBoards', back_populates='Kanban_Columns')
    Kanban_Cards: Mapped[List['KanbanCards']] = relationship('KanbanCards', back_populates='column')


class KanbanCards(Base):
    __tablename__ = 'Kanban_Cards'
    __table_args__ = (
        ForeignKeyConstraint(['card_type_id'], ['Kanban_Card_Types.card_type_id'], name='FK__Kanban_Ca__card___5708E33C'),
        ForeignKeyConstraint(['column_id'], ['Kanban_Columns.column_id'], ondelete='CASCADE', name='FK__Kanban_Ca__colum__5614BF03'),
        PrimaryKeyConstraint('card_id', name='PK__Kanban_C__BDF201DD2CD4B06B')
    )

    card_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    column_id: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(TEXT(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    card_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    position: Mapped[Optional[int]] = mapped_column(Integer)
    estimate: Mapped[Optional[int]] = mapped_column(Integer)

    card_type: Mapped['KanbanCardTypes'] = relationship('KanbanCardTypes', back_populates='Kanban_Cards')
    column: Mapped['KanbanColumns'] = relationship('KanbanColumns', back_populates='Kanban_Cards')
    card_parent: Mapped[List['KanbanCards']] = relationship('KanbanCards', secondary='Kanban_Card_Relations', primaryjoin=lambda: KanbanCards.card_id == t_Kanban_Card_Relations.c.card_child_id, secondaryjoin=lambda: KanbanCards.card_id == t_Kanban_Card_Relations.c.card_parent_id, back_populates='card_child')
    card_child: Mapped[List['KanbanCards']] = relationship('KanbanCards', secondary='Kanban_Card_Relations', primaryjoin=lambda: KanbanCards.card_id == t_Kanban_Card_Relations.c.card_parent_id, secondaryjoin=lambda: KanbanCards.card_id == t_Kanban_Card_Relations.c.card_child_id, back_populates='card_parent')
    Kanban_Subtasks: Mapped[List['KanbanSubtasks']] = relationship('KanbanSubtasks', back_populates='parent_card')


t_Kanban_Card_Relations = Table(
    'Kanban_Card_Relations', Base.metadata,
    Column('card_parent_id', Integer, primary_key=True, nullable=False),
    Column('card_child_id', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['card_child_id'], ['Kanban_Cards.card_id'], name='FK__Kanban_Ca__card___5EAA0504'),
    ForeignKeyConstraint(['card_parent_id'], ['Kanban_Cards.card_id'], name='FK__Kanban_Ca__card___5DB5E0CB'),
    PrimaryKeyConstraint('card_parent_id', 'card_child_id', name='PK__Kanban_C__BEFAE2D135AB1205')
)


class KanbanSubtasks(Base):
    __tablename__ = 'Kanban_Subtasks'
    __table_args__ = (
        ForeignKeyConstraint(['parent_card_id'], ['Kanban_Cards.card_id'], ondelete='CASCADE', name='FK__Kanban_Su__paren__59E54FE7'),
        PrimaryKeyConstraint('subtask_id', name='PK__Kanban_S__C2AC5F05AEB1592C')
    )

    subtask_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    completed: Mapped[bool] = mapped_column(Boolean)
    parent_card_id: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(TEXT(2147483647, 'SQL_Latin1_General_CP1_CI_AS'))
    position: Mapped[Optional[int]] = mapped_column(Integer)
    due_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    parent_card: Mapped['KanbanCards'] = relationship('KanbanCards', back_populates='Kanban_Subtasks')
