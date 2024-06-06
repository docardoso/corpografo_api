from db import db

class UserModel(db.Model):
    __tablebname__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    real_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    access_level = db.Column(db.Integer, nullable=False, default=0)

    corpora = db.relationship(
        'CorpusModel',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete',
    )

class CorpusModel(db.Model):
    __tablename__ = 'corpora'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        unique=False,
        nullable=False,
    )

    documents = db.relationship(
        'DocumentModel',
        back_populates='corpus',
        lazy='dynamic',
        cascade='all, delete',
    )

    user = db.relationship('UserModel', back_populates='corpora')

class DocumentModel(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(10**6), nullable=False)

    corpus_id = db.Column(
        db.Integer,
        db.ForeignKey('corpora.id'),
        unique=False,
        nullable=False,
    )

    corpus = db.relationship('CorpusModel', back_populates='documents')

class RevokedJWTModel(db.Model):
    __tablename__ = 'revoked_jwts'

    jti = db.Column(db.String(100), primary_key=True)
