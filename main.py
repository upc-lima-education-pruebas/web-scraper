from fastapi import FastAPI
from src.interfaces.api import job_controller

app = FastAPI()

app.include_router(job_controller.router)