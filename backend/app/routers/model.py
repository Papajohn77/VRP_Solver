from fastapi import APIRouter, HTTPException
from app.config.database import conn
from app.models.model import models
from app.schemas.model import Model

model = APIRouter(
    tags=['models']
)

class ModelNameAlreadyExist(Exception):
    pass

@model.get('/models')
async def get_models():
    try:
        return { "models": conn.execute(models.select()).fetchall() }
    except Exception:
        raise HTTPException(500, "Failed to load models.")

@model.post('/models', status_code=201)
async def create_model(model: Model):
    try:
        existing_model = conn.execute(models.select().where(models.columns.name == model.name)).first()

        if existing_model is not None:
            raise ModelNameAlreadyExist("Failed to create model! There is already a model using that name.")

        conn.execute(models.insert().values(
            name = model.name
        ))

        # Returns the last AUTO_INCREMENT generated id per-connection.
        result = conn.execute('SELECT LAST_INSERT_ID() AS id').fetchone()
        return { "id": result['id'] }
    except ModelNameAlreadyExist as error:
        raise HTTPException(409, str(error))
    except Exception:
        raise HTTPException(500, "Failed to create model.")
