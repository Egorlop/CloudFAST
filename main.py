from datetime import datetime, timedelta
from secrets import token_urlsafe
import clickhouse_connect
import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from psycopg2 import connect, DatabaseError
templates = Jinja2Templates(directory="templates")

def start():
    client = clickhouse_connect.get_client(host='localhost')
    client.command('CREATE DATABASE IF NOT EXISTS admin_db')
    client.command('USE admin_db')
    client.command('''create table if not exists users
    (
        username Nullable(VARCHAR2),
        password Nullable(VARCHAR2)
    )
        engine = Memory''')

app = FastAPI()
auth = HTTPBasic()

def create_jwt_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        username = payload["sub"]
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user(credentials: HTTPBasicCredentials = Depends(auth)):
    client = clickhouse_connect.get_client(host='localhost')
    client.command('USE admin_db')
    user = client.command(f"SELECT * FROM users where username = '{credentials.username}'")
    print(user)
    if type(user) is not list or user[1] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def create_database(user):
    dbname = f"db_{user[0]}_{token_urlsafe(8)}"
    dbpass = token_urlsafe(16)
    client = clickhouse_connect.get_client(host='localhost')

    try:
        client.command(f"CREATE DATABASE {dbname}")
        client.command(f"CREATE USER {dbname} IDENTIFIED BY '{dbpass}'")
        client.command(f"GRANT ALL ON {dbname} TO {dbname}")
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database creation failed: {e}",
        )

    return dbname, dbname, dbpass


@app.post("/register")
def register(credentials: HTTPBasicCredentials = Depends(auth)):
    client = clickhouse_connect.get_client(host='localhost')
    client.command('USE admin_db')
    user = client.command(f"SELECT * FROM users where username = '{credentials.username}'")
    print(user)
    if type(user) is list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    client.command('USE admin_db')
    user = client.command(f'''insert into users values('{credentials.username}','{credentials.password}')''')
    return {"message": "User registered successfully"}


@app.post("/authorize")
def authorize(user=Depends(verify_user)):
    token = create_jwt_token(user[0])
    return {"message": "User authorized successfully", "username": user[0], "token": token}


@app.get("/create_database")
def create_database_for_user(token: str = Header(None)):
    username = verify_jwt_token(token)
    client = clickhouse_connect.get_client(host='localhost')
    client.command('USE admin_db')
    user = client.command(f"SELECT * FROM users where username = '{username}'")
    if type(user) is not list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    dbname, dbuser, dbpass = create_database(user)
    return {"message": "Database created successfully", "database": dbname, "user": dbuser, "password": dbpass}


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})