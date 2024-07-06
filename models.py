from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
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

    user_relations: Mapped[List['UsersCorpora']] = relationship(back_populates='corpus')
    document_relations: Mapped[List['CorporaDocuments']] = relationship(back_populates='corpus')

    users: AssociationProxy[List['User']] = association_proxy('user_relations', 'user', creator=lambda user: UsersCorpora(user=user))
    documents: AssociationProxy[List['Document']] = association_proxy('document_relations', 'document')

class Document(db.Model):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    content: Mapped[str] = mapped_column(nullable=False)

    user_relations: Mapped[List['DocumentsUsers']] = relationship(back_populates='document')
    corpus_relations: Mapped[List['CorporaDocuments']] = relationship(back_populates='document')

    users: AssociationProxy[List['User']] = association_proxy('user_relations', 'user', creator=lambda user: DocumentsUsers(user=user))
    corpora: AssociationProxy[List['Corpus']] = association_proxy('corpus_relations', 'corpus')

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    access_level: Mapped[int] = mapped_column(nullable=False, default=0)

    document_relations: Mapped[List['DocumentsUsers']] = relationship(back_populates='user')
    corpus_relations: Mapped[List['UsersCorpora']] = relationship(back_populates='user')

    documents: AssociationProxy[List['Document']] = association_proxy('document_relations', 'document')
    corpora: AssociationProxy[List['Corpus']] = association_proxy('corpus_relations', 'corpus')

class RevokedJWT(db.Model):
    __tablename__ = 'revoked_jwts'

    jti: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column(nullable=False)
