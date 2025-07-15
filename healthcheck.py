# web.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
