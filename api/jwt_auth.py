from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

app = FastAPI()

# JWT 验证函数
def verify_jwt(authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="JWT token missing or invalid")

    jwt_token = authorization.split(" ")[1]
    secret_key = 'adahudhaohdoahf'  # 更改为你的密钥

    try:
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

    return decoded_token

@app.get("/protected")
def protected_route(decoded_token: dict = Depends(verify_jwt)):
    return {"message": "This is a protected route", "user": decoded_token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)