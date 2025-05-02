from fastapi import FastAPI
from routers import notion

app = FastAPI()

# 라우터 등록
app.include_router(notion.router)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}