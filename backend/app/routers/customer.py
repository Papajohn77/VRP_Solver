from fastapi import APIRouter, HTTPException, Response
from app.config.database import conn
from app.models.customer import customers
from app.schemas.customer import Customer

customer = APIRouter(
    tags=['customers']
)

class CustomerNameAlreadyExistsInTheSelectedModel(Exception):
    pass

class NegativeDemand(Exception):
    pass

@customer.get('/customers')
async def get_customers(model_id: int):
    try:
        return { "customers": conn.execute(customers.select().where(customers.columns.model_id == model_id)).fetchall() }
    except Exception:
        raise HTTPException(500, "Failed to load customers.")

@customer.post('/customers', status_code=201)
async def create_customer(customer: Customer):
    try:
        existing_customer = conn.execute(customers.select().where(customers.columns.name == customer.name).where(customers.columns.model_id == customer.model_id)).first()

        if existing_customer is not None:
            raise CustomerNameAlreadyExistsInTheSelectedModel("Failed to create customer! There is already a customer with that name in the selected model.")
        
        if customer.demand <= 0:
            raise NegativeDemand("Failed to create customer! The customer's demand can only be greater than zero.")

        conn.execute(customers.insert().values(
            name = customer.name,
            demand = customer.demand,
            latitude = customer.latitude,
            longitude = customer.longitude,
            address = customer.address,
            model_id = customer.model_id
        ))

        # Returns the last AUTO_INCREMENT generated id per-connection.
        result = conn.execute('SELECT LAST_INSERT_ID() AS id').fetchone()
        return { "id": result['id'] }
    except CustomerNameAlreadyExistsInTheSelectedModel as error:
        raise HTTPException(409, str(error))
    except NegativeDemand as error:
        raise HTTPException(400, str(error))
    except Exception:
        raise HTTPException(500, "Failed to create customer.")

@customer.delete('/customers/{id}', status_code=204)
async def delete_customer(id: int):
    try:
        conn.execute(customers.delete().where(customers.columns.id == id))
        return Response(status_code=204)
    except Exception:
        raise HTTPException(500, "Failed to delete customer.")
