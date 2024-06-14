from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List

class DocumentsUsers(db.Model):
    __tablename__ = 'documents_users'

    document_id: Mapped[int] = mapped_column(
        db.ForeignKey('documents.id'),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey('users.id'),
        primary_key=True,
    )

    document: Mapped['Document'] = relationship(back_populates='user_relations')
    user: Mapped['User'] = relationship(back_populates='document_relations')

class UsersCorpora(db.Model):
    __tablename__ = 'users_corpora'

    corpus_id: Mapped[int] = mapped_column(ForeignKey('corpora.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)

    corpus: Mapped['Corpus'] = relationship(back_populates='user_relations')
    user: Mapped['User'] = relationship(back_populates='corpus_relations')

class CorporaDocuments(db.Model):
    __tablename__ = 'corpora_documents'

    corpus_id: Mapped[int] = mapped_column(ForeignKey('corpora.id'), primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'), primary_key=True)

    corpus: Mapped['Corpus'] = relationship(back_populates='document_relations')
    document: Mapped['Document'] = relationship(back_populates='corpus_relations')

class Corpus(db.Model):
    __tablename__ = 'corpora'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    documents: Mapped[List['Document']] = relationship(
        back_populates='corpora',
        secondary='corpora_documents',
        #lazy='dynamic',
        #cascade='all, delete',
    )

    users: Mapped[List['User']] = relationship(
        back_populates='corpora',
        secondary='users_corpora',
        #lazy='dynamic',
        #cascade='all, delete',
    )

    user_relations: Mapped[List['UsersCorpora']] = relationship(back_populates='corpus')
    document_relations: Mapped[List['CorporaDocuments']] = relationship(back_populates='corpus')

class Document(db.Model):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)

    corpora: Mapped[List['Corpus']] = relationship(
        back_populates='documents', 
        secondary='corpora_documents',
    )

    users: Mapped[List['User']] = relationship(
        back_populates='documents', 
        secondary='documents_users',
    )

    user_relations: Mapped[List['DocumentsUsers']] = relationship(back_populates='document')
    corpus_relations: Mapped[List['CorporaDocuments']] = relationship(back_populates='document')

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    real_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    access_level: Mapped[int] = mapped_column(nullable=False, default=0)

    corpora: Mapped[List['Corpus']] = relationship(
        back_populates='users',
        secondary='users_corpora',
        #lazy='dynamic',
        #cascade='all, delete',
    )

    documents: Mapped[List['Document']] = relationship(
        back_populates='users',
        secondary='documents_users',
        #lazy='dynamic',
        #cascade='all, delete',
    )

    document_relations: Mapped[List['DocumentsUsers']] = relationship(back_populates='user')
    corpus_relations: Mapped[List['UsersCorpora']] = relationship(back_populates='user')

class RevokedJWT(db.Model):
    __tablename__ = 'revoked_jwts'

    jti: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column(nullable=False)
