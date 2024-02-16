from fastapi import FastAPI

from .router import router

app = FastAPI(title="Auth App")

app.include_router(router)