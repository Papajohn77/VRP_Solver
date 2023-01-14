from fastapi import APIRouter, HTTPException, Response
from app.config.database import conn
from app.models.vehicle import vehicles
from app.schemas.vehicle import Vehicle

vehicle = APIRouter(
    tags=['vehicles']
)

class VehicleNameAlreadyExistsInTheSelectedModel(Exception):
    pass

class NegativeCapacity(Exception):
    pass

@vehicle.get('/vehicles')
async def get_vehicles(model_id: int):
    try:
        return { "vehicles": conn.execute(vehicles.select().where(vehicles.columns.model_id == model_id)).fetchall() }
    except Exception:
        raise HTTPException(500, "Failed to load vehicles.")


@vehicle.post('/vehicles', status_code=201)
async def create_vehicle(vehicle: Vehicle):
    try:
        existing_vehicle = conn.execute(vehicles.select().where(vehicles.columns.name == vehicle.name).where(vehicles.columns.model_id == vehicle.model_id)).first()

        if existing_vehicle is not None:
            raise VehicleNameAlreadyExistsInTheSelectedModel("Failed to create vehicle! There is already a vehicle with that name in the selected model.")

        if vehicle.capacity <= 0:
            raise NegativeCapacity("Failed to create vehicle! The vehicle's capacity can only be greater than zero.")

        conn.execute(vehicles.insert().values(
            name = vehicle.name,
            capacity = vehicle.capacity,
            model_id = vehicle.model_id
        ))

        # Returns the last AUTO_INCREMENT generated id per-connection.
        result = conn.execute('SELECT LAST_INSERT_ID() AS id').fetchone()
        return { "id": result['id'] }
    except VehicleNameAlreadyExistsInTheSelectedModel as error:
        raise HTTPException(409, str(error))
    except NegativeCapacity as error:
        raise HTTPException(400, str(error))
    except Exception:
        raise HTTPException(500, "Failed to create vehicle.")

@vehicle.delete('/vehicles/{id}', status_code=204)
async def delete_vehicle(id: int):
    try:
        conn.execute(vehicles.delete().where(vehicles.columns.id == id))
        return Response(status_code=204)
    except Exception:
        raise HTTPException(500, "Failed to delete vehicle.")
