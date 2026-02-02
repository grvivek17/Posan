import fastapi
print(f"FastAPI: {fastapi}")
from fastapi import HTTPException
print("HTTPException imported")
import fastapi.security
print(f"fastapi.security contents: {dir(fastapi.security)}")
