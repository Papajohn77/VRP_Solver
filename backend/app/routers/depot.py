from fastapi import APIRouter, HTTPException, Response
from app.config.database import conn
from app.models.depot import depots
from app.schemas.depot import Depot

depot = APIRouter(
    tags=['depots']
)

class DepotAlreadyExistForTheSelectedModel(Exception):
    pass

class DepotNameAlreadyExistsInTheSelectedModel(Exception):
    pass

@depot.get('/depot')
async def get_depot(model_id: int):
    try:
        return { "depot": conn.execute(depots.select().where(depots.columns.model_id == model_id)).first() }
    except Exception:
        raise HTTPException(500, "Failed to load depot.")

@depot.post('/depot')
async def create_depot(depot: Depot, status_code=201):
    try:
        existing_depot = conn.execute(depots.select().where(depots.columns.model_id == depot.model_id)).first()

        if existing_depot is not None:
            raise DepotAlreadyExistForTheSelectedModel("Failed to create depot! There is already a depot for the selected model.")

        conn.execute(depots.insert().values(
            name = depot.name,
            latitude = depot.latitude,
            longitude = depot.longitude,
            address = depot.address,
            model_id = depot.model_id
        ))
        
        # Returns the last AUTO_INCREMENT generated id per-connection.
        result = conn.execute('SELECT LAST_INSERT_ID() AS id').fetchone()
        return { "id": result['id'] }
    except DepotAlreadyExistForTheSelectedModel as error:
        raise HTTPException(409, str(error))
    except Exception:
        raise HTTPException(500, "Failed to create depot.")

@depot.delete('/depot/{id}', status_code=204)
async def delete_depot(id: int):
    try:
        conn.execute(depots.delete().where(depots.columns.id == id))
        return Response(status_code=204)
    except Exception:
        raise HTTPException(500, "Failed to delete depot.")
