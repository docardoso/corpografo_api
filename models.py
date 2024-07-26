from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import List
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

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

    #document: Mapped['Document'] = relationship(back_populates='user_relations', lazy='joined')
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
    name: Mapped[str] = mapped_column()

    user_relations: Mapped[List['UsersCorpora']] = relationship(back_populates='corpus')
    document_relations: Mapped[List['CorporaDocuments']] = relationship(back_populates='corpus')

    users: AssociationProxy[List['User']] = association_proxy('user_relations', 'user', creator=lambda user: UsersCorpora(user=user))
    documents: AssociationProxy[List['Document']] = association_proxy('document_relations', 'document')

class AuthorsDocuments(db.Model):
    __tablename__ = 'authors_documents'

    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'), primary_key=True)

class Author(db.Model):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), )
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), nullable=True)

    documents: Mapped[List['Document']] = relationship(secondary='authors_documents', back_populates='authors')

    __table_args__ = (UniqueConstraint('user_id', 'name'),)

class Document(db.Model):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column(nullable=True)
    input_file: Mapped[str] = mapped_column()

    citation: Mapped[str] = mapped_column(nullable=True)

    language_id: Mapped[int] = mapped_column(ForeignKey('languages.id'), nullable=True)
    source_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), nullable=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), nullable=True)

    authors: Mapped[List['Author']] = relationship(secondary='authors_documents', back_populates='documents')

    source: Mapped['Organization'] = relationship(foreign_keys=[source_id])
    publisher: Mapped['Organization'] = relationship(foreign_keys=[publisher_id])

    language: Mapped['Language'] = relationship(back_populates='documents')

    user_relations: Mapped[List['DocumentsUsers']] = relationship(back_populates='document')
    corpus_relations: Mapped[List['CorporaDocuments']] = relationship(back_populates='document')

    users: AssociationProxy[List['User']] = association_proxy('user_relations', 'user', creator=lambda user: DocumentsUsers(user=user))
    corpora: AssociationProxy[List['Corpus']] = association_proxy('corpus_relations', 'corpus')

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    access_level: Mapped[int] = mapped_column(default=0)

    languages: Mapped[List['Language']] = relationship()
    organizations: Mapped[List['Organization']] = relationship()
    authors: Mapped[List['Author']] = relationship()

    document_relations: Mapped[List['DocumentsUsers']] = relationship(back_populates='user')
    corpus_relations: Mapped[List['UsersCorpora']] = relationship(back_populates='user')

    documents: AssociationProxy[List['Document']] = association_proxy('document_relations', 'document')
    corpora: AssociationProxy[List['Corpus']] = association_proxy('corpus_relations', 'corpus')

class RevokedJWT(db.Model):
    __tablename__ = 'revoked_jwts'

    jti: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column()

class Language(db.Model):
    __tablename__ = 'languages'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column()

    documents: Mapped[List['Document']] = relationship(back_populates='language')

    __table_args__ = (UniqueConstraint('user_id', 'name'),)

class Organization(db.Model):
    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)

    documents: Mapped[List['Document']] = relationship(
        primaryjoin="or_(Document.source_id == Organization.id, Document.publisher_id == Organization.id)"
    )

    __table_args__ = (UniqueConstraint('user_id', 'name'),)