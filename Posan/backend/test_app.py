from fastapi import FastAPI

app = FastAPI(title="POSAN Test")

@app.get("/")
def root():
    return {"message": "Hello from POSAN!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
