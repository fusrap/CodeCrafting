from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKeyConstraint, Identity, Index, Integer, LargeBinary, PrimaryKeyConstraint, String, Unicode, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = 'Course'
    __table_args__ = (
        PrimaryKeyConstraint('course_id', name='PK__Course__8F1EF7AE546254B9'),
    )

    course_id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    course_title: Mapped[str] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    course_description: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('(getdate())'))

    CourseElement: Mapped[List['CourseElement']] = relationship('CourseElement', back_populates='course')


class InputElement(Base):
    __tablename__ = 'InputElement'
    __table_args__ = (
        PrimaryKeyConstraint('input_element_id', name='PK__InputEle__13DEF51292F88B1C'),
    )

    input_element_id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    label: Mapped[str] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    answer: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))


class Jeopardy(Base):
    __tablename__ = 'Jeopardy'
    __table_args__ = (
        PrimaryKeyConstraint('jeopardy_id', name='PK__Jeopardy__55619D04378367C6'),
    )

    jeopardy_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    jeopardy_title: Mapped[str] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    jeopardy_description: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('(getdate())'))

    JeopardyCells: Mapped[List['JeopardyCells']] = relationship('JeopardyCells', back_populates='jeopardy_cell_jeopardy')
    Subjects: Mapped[List['Subjects']] = relationship('Subjects', back_populates='subject_jeopardy')


class Role(Base):
    __tablename__ = 'Role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK__Role__3213E83FB3B43300'),
        Index('UQ__Role__863D21489C3C2BE9', 'role', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(25, 'SQL_Latin1_General_CP1_CI_AS'))

    Account: Mapped[List['Account']] = relationship('Account', back_populates='role')


class TextElement(Base):
    __tablename__ = 'TextElement'
    __table_args__ = (
        PrimaryKeyConstraint('text_element_id', name='PK__TextElem__69BCDBBC587B2B45'),
    )

    text_element_id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    text_: Mapped[str] = mapped_column('text', Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))


class Sysdiagrams(Base):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (
        PrimaryKeyConstraint('diagram_id', name='PK__sysdiagr__C2B05B6138E4CD67'),
        Index('UK_principal_name', 'principal_id', 'name', unique=True)
    )

    name: Mapped[str] = mapped_column(Unicode(128, 'SQL_Latin1_General_CP1_CI_AS'))
    principal_id: Mapped[int] = mapped_column(Integer)
    diagram_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    version: Mapped[Optional[int]] = mapped_column(Integer)
    definition: Mapped[Optional[bytes]] = mapped_column(LargeBinary)


class Account(Base):
    __tablename__ = 'Account'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['Role.id'], name='FK__Account__role_id__22751F6C'),
        PrimaryKeyConstraint('account_id', name='PK__Account__46A222CD7FEC8314'),
        Index('UQ__Account__AB6E61640D1FAD8E', 'email', unique=True),
        Index('ac_email_index', 'email')
    )

    account_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))
    email: Mapped[str] = mapped_column(String(180, 'SQL_Latin1_General_CP1_CI_AS'))
    password: Mapped[str] = mapped_column(String(255, 'SQL_Latin1_General_CP1_CI_AS'))
    role_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('(getdate())'))

    role: Mapped['Role'] = relationship('Role', back_populates='Account')


class CourseElement(Base):
    __tablename__ = 'CourseElement'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['Course.course_id'], ondelete='CASCADE', name='FK_CourseElement_Course'),
        PrimaryKeyConstraint('course_element_id', name='PK__CourseEl__739140BEFD554611')
    )

    course_element_id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    course_id: Mapped[int] = mapped_column(BigInteger)
    element_id: Mapped[int] = mapped_column(BigInteger)
    element_type: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('(getdate())'))

    course: Mapped['Course'] = relationship('Course', back_populates='CourseElement')


class JeopardyCells(Base):
    __tablename__ = 'JeopardyCells'
    __table_args__ = (
        ForeignKeyConstraint(['jeopardy_cell_jeopardy_id'], ['Jeopardy.jeopardy_id'], ondelete='CASCADE', name='FK__JeopardyC__jeopa__7B264821'),
        PrimaryKeyConstraint('jeopardy_cell_id', name='PK__Jeopardy__FA902A9F3AFEA41E'),
        Index('IDX_JeopardyCells_Jeopardy_Id', 'jeopardy_cell_id')
    )

    jeopardy_cell_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    jeopardy_cell_value: Mapped[int] = mapped_column(Integer)
    jeopardy_cell_question: Mapped[str] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    jeopardy_cell_answer: Mapped[str] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    RowNumber: Mapped[int] = mapped_column(Integer)
    ColumnNumber: Mapped[int] = mapped_column(Integer)
    jeopardy_cell_jeopardy_id: Mapped[int] = mapped_column(Integer)

    jeopardy_cell_jeopardy: Mapped['Jeopardy'] = relationship('Jeopardy', back_populates='JeopardyCells')


class Subjects(Base):
    __tablename__ = 'Subjects'
    __table_args__ = (
        ForeignKeyConstraint(['subject_jeopardy_id'], ['Jeopardy.jeopardy_id'], ondelete='CASCADE', name='FK__Subjects__subjec__7849DB76'),
        PrimaryKeyConstraint('subject_Id', name='PK__Subjects__5007F248494E295F'),
        Index('IDX_Subjects_Jeopardy_Id', 'subject_Id')
    )

    subject_Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    subject_name: Mapped[str] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    subject_jeopardy_id: Mapped[int] = mapped_column(Integer)

    subject_jeopardy: Mapped['Jeopardy'] = relationship('Jeopardy', back_populates='Subjects')
