from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.model import model
from app.routers.depot import depot
from app.routers.vehicle import vehicle
from app.routers.customer import customer
from app.routers.solve import solve

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True,
)

app.include_router(model)
app.include_router(depot)
app.include_router(vehicle)
app.include_router(customer)
app.include_router(solve)
