from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.chat import router as chat_router  # 添加这行
from app.database.mongodb import MongoDB

app = FastAPI(title="Talk to Myself API")

@app.on_event("startup")
async def startup():
    await MongoDB.connect_db()

@app.on_event("shutdown")
async def shutdown():
    await MongoDB.close_db()

app.include_router(user_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")  # 添加这行

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
