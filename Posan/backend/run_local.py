import uvicorn
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    import fastapi
    print(f"FastAPI version: {fastapi.__version__}")
    print(f"FastAPI file: {fastapi.__file__}")
    print(f"Has HTTPException: {'HTTPException' in dir(fastapi)}")
    from fastapi import HTTPException
    print("Imported HTTPException successfully")
    
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)
