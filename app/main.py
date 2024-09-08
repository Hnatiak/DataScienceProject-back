import os
import signal
import traceback
import logging
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
import redis.asyncio as redis
from pytest import Session
from sqlalchemy import text
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings
from src.database.db import engine, SessionLocal, redis_client_async, get_db
from src.routes import auth
from src.routes.document_routes import router as document_router
# from src.routes.question_routes import router as question_router
# from src.routes.history_routes import router as history_router


# logger = logging.getLogger(uvicorn.logging.__name__)
logger = logging.getLogger("uvicorn")

origins = settings.cors_origins.split('|')


@asynccontextmanager
async def lifespan(test: FastAPI):
    #startup initialization goes here    
    logger.info("Knock-knock...")
    logger.info("Uvicorn has you...")
    await FastAPILimiter.init(redis_client_async)
    yield
    #shutdown logic goes here    
    SessionLocal.close_all()
    engine.dispose()
    await redis_client_async.close(True)
    await FastAPILimiter.close()
    logger.info("Good bye, Mr. Anderson")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(document_router, prefix="/documents", tags=["documents"])        #VY
# app.include_router(question_router, prefix="/questions", tags=["questions"])        #VY
# app.include_router(history_router, prefix="/history", tags=["history"])     #VY


@app.get("/")
def read_root():
    return {"message": "Wake up!"}

@app.get('/api/healthcheck')
def healthchecker(db: Session = Depends(get_db)) -> dict:
    try:
        # Make request
        result = db.execute(text('SELECT 1')).fetchone()
        if result is None:
            function_name = traceback.extract_stack(None, 2)[1][2]
            add_log = f'\n500:\t{datetime.now()}\tError connecting to the database.\t{function_name}'
            logger.error(add_log)
            raise HTTPException(status_code=500, detail="Database is not configured properly.")

        function_name = traceback.extract_stack(None, 2)[1][2]
        add_log = f'\n000:\t{datetime.now()}\tService is healthy and running\t{function_name}'
        logger.info(add_log)

        return {'message': "Service is healthy and running"}

    except Exception as e:
        function_name = traceback.extract_stack(None, 2)[1][2]
        add_log = f'\n000:\t{datetime.now()}\tError connecting to the database.: {e}\t{function_name}'
        logger.error(add_log)
        raise HTTPException(status_code=500, detail="Database is not configured properly.")
    

if __name__ == '__main__':
    try:
        uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGBREAK)
        os.kill(os.getpid(), signal.SIGTERM) 
