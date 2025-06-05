from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials   
from .jwt_handler import decodeJwt

class jwtBearer(HTTPBearer):
    def _init__(self,auto_error: bool = True):
      super(jwtBearer,self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials= await super(jwtBearer,self).__call__(request)
        if credentials:
           if not credentials.scheme == "Bearer":
              raise HTTPException(status_code=403,details="Invalid or expired token") 
           return credentials.credentials
        else:
           raise HTTPException(status_code=403,details="Invalid or expired token")
        
    def verify_jwt(self, token: str):
       isTokenvalid:bool=False
       payload=decodeJwt(token)
       if payload:
           isTokenvalid=True
       return isTokenvalid