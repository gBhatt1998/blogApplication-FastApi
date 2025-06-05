import time
import jwt
from decouple import config

from models import Role

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token:str):
    return {
        "access_token":token
    }

def signJwt(userID: str, role:str):
    payload={
        "userID": userID,
        "role":role,
        "expiry":time.time()+1000 
    }   
    token=jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJwt(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expiry"] >= time.time() else None
    except jwt.ExpiredSignatureError:
        return None
   