import uuid
import bcrypt

from api.user.models.user import User
from api.user import service as user_service
from flask_api import status
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, get_jwt_identity, set_access_cookies
from flask_httpauth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone

auth = HTTPBasicAuth()

def refresh_jwt_token(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
            return response

    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

@auth.verify_password
def login_user(
    username,
    password
) -> str:
    user: User = user_service.read_one_user(
        username=username
    )

    if user is None:
        raise Exception("Cannot find user")

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise Exception("Cannot verify user credentials")

    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(minutes=15),
        additional_headers=user.serialize_public()
    )

    return access_token


def register_user(
    username,
    firstname,
    lastname,
    password,
    email,
    address
) -> User:
    id = uuid.uuid4().__str__()
    password_salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), password_salt)

    user = user_service.create_user(
        username=username,
        firstname = firstname,
        lastname = lastname,
        password=password_hash.decode('utf-8'),
        email=email,
        address=address,
        UserID=id
    )

    return user

def get_user(username):
    res =  User.query.filter_by(username=username).first()
    print(res)
    print("\n"*3)
    return res