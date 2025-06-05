import time
import jwt
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token:str):
    return {
        "access_token":token
    }

def signJwt(userID: str):
    payload={
        "userID": userID,
        "expiry":time.time()+500 
    }   
    token=jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJwt(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expiry"] >= time.time() else None
    except jwt.ExpiredSignatureError:
        return None
   