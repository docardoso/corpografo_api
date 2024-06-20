from flask_smorest import abort
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from models import RevokedJWT
from db import db
import time
from models import User
import os
import random
import nltk
import smtplib

nltk.download('words')
short_words = [i for i in nltk.corpus.words.words() if len(i) < 7]

def gen_random_passphrase():
    return '-'.join(random.sample(short_words, 3)).lower()

def login_required(min_access_level=0):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt()['access_level'] >= min_access_level:
                return fn(*args, **kwargs)

            abort(403, message='Higher access level required for security clearance.')

        return decorator

    return wrapper

def revoke_jwt():
    revoked_jwt = RevokedJWT(
        jti=get_jwt()['jti'],
        timestamp=time.time(),
    )
    db.session.add(revoked_jwt)

    #return revoked_jwt

def get_current_user():
    return db.session.query(User).get(get_jwt_identity())

def send_email(sender, recipient, subject, body):
    message = f'Subject: {subject}\n\n{body}'

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    print(smtp_server, smtp_port)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(sender, recipient, message.encode('utf-8'))
