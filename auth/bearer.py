from fastapi import Depends, Request, HTTPException,status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials   
from .jwt_handler import decodeJwt

class jwtBearer(HTTPBearer):
    def __init__(self,auto_error: bool = True):
      super(jwtBearer,self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials= await super(jwtBearer,self).__call__(request)
        if credentials:
           if not credentials.scheme == "Bearer":
              raise HTTPException(status_code=403,details="Invalid or expired token") 
           payload = decodeJwt(credentials.credentials)
           if not payload:
                  raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token")
           return payload  # Return decoded payload
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token")
        
    def verify_jwt(self, token: str):
       isTokenvalid:bool=False
       payload=decodeJwt(token)
       if payload:
           isTokenvalid=True
       return isTokenvalid


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, payload: dict = Depends(jwtBearer())):
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        if payload.get("role") not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
        return payload

user_access = RoleChecker(["user", "writer", "admin"])
writer_access = RoleChecker(["writer", "admin"])
admin_access = RoleChecker(["admin"])