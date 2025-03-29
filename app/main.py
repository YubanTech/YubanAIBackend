from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import sys
import os
from datetime import datetime

# 配置根日志器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from app.api.user import router as user_router
# from app.api.chat import router as chat_router  # 添加这行
from app.api.tarot import router as tarot_router  # 添加这行
from app.database.mongodb import MongoDB

app = FastAPI(title="Talk to Myself API")

@app.on_event("startup")
async def startup():
    mongo_uri = os.getenv("MONGODB_URL", "mongodb://mongo:27017")
    await MongoDB.connect_db(mongo_uri)

@app.on_event("shutdown")
async def shutdown():
    logging.info("Shutting down application")
    await MongoDB.close_db()

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {str(exc)}")
    import traceback
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

app.include_router(user_router, prefix="/api/v1")
# app.include_router(chat_router, prefix="/api/v1")  # 添加这行
app.include_router(tarot_router, prefix="/api/v1")  # 添加这行

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
