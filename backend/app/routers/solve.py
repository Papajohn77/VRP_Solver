import os
import googlemaps
from fastapi import APIRouter, HTTPException
from app.config.database import conn
from app.models.depot import depots
from app.models.vehicle import vehicles
from app.models.customer import customers

solve = APIRouter(
    tags=['solve']
)

class MissingData(Exception):
    pass

class InfeasibleModel(Exception):
    pass

class Depot:
    def __init__(self, id, name, lat, lng, address):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng
        self.address = address

class Vehicle:
    def __init__(self, name, capacity, depot):
        self.name = name
        self.capacity = capacity
        self.route = [depot, depot]

class Customer:
    def __init__(self, id, name, demand, lat, lng, address):
        self.id = id
        self.name = name
        self.demand = demand
        self.lat = lat
        self.lng = lng
        self.address = address

class Solution:
    def __init__(self):
        self.total_distance_meters = 0
        self.routes = []
        self.vehicles = []

def create_vehicles(vehicles_rs, depot):
    vehicles = []
    for vehicle in vehicles_rs:
        # vehicle = (id, name, capacity, model_id)
        vehicles.append(Vehicle(vehicle[1], vehicle[2], depot))
    return vehicles

def create_customers(customers_rs):
    customers = []
    for i, cust in enumerate(customers_rs):
        # cust = (id, name, demand, latitude, longitude, address, model_id)
        customers.append(Customer(i + 1, cust[1], cust[2], cust[3], cust[4], cust[5]))
    return customers

def create_distance_matrix(depot, customers, gmaps):
    origins = [(depot.lat, depot.lng)]
    destinations = [(depot.lat, depot.lng)]

    for cust in customers:
        origins.append((cust.lat, cust.lng))
        destinations.append((cust.lat, cust.lng))
    
    dist_matrix = []

    for i, origin in enumerate(origins):
        dist_matrix.append([])
        for destination in destinations:
            dist = gmaps.distance_matrix(origin, destination)["rows"][0]["elements"][0]["distance"]["value"]
            dist_matrix[i].append(dist)
    
    return dist_matrix

def solver(solution, vehicles, customers, distance_matrix):
    while True:
        min, min_pos, min_cust, min_vehicle = float('inf'), -1, -1, -1

        for vehicle in vehicles:
            for cust in customers:
                for pos in range(1, len(vehicle.route)):
                    prev = vehicle.route[pos - 1]
                    next = vehicle.route[pos]
                    additional_duration = distance_matrix[prev.id][cust.id] + distance_matrix[cust.id][next.id] - distance_matrix[prev.id][next.id]

                    if cust.demand > vehicle.capacity:
                        continue

                    if additional_duration < min:
                        min = additional_duration
                        min_pos = pos
                        min_cust = cust
                        min_vehicle = vehicle

        if min != float('inf'):
            solution.total_distance_meters += min
            min_vehicle.capacity -= min_cust.demand
            min_vehicle.route.insert(min_pos, min_cust)
            customers.remove(min_cust)
        else:
            break
    
    if len(customers) != 0:
        raise InfeasibleModel('Model infeasible! The model could not be solved because we could not serve all of the customers due to capacity constraints.')

    for vehicle in vehicles:
        solution.routes.append(vehicle.route)
        solution.vehicles.append(vehicle.name)

@solve.get('/solve')
def solve_model(model_id: int):
    try:
        depot_rs = conn.execute(depots.select().where(depots.columns.model_id == model_id)).first()

        if not(depot_rs):
            raise MissingData("Failed to solve model! Depot is missing")

        vehicles_rs = conn.execute(vehicles.select().where(vehicles.columns.model_id == model_id)).fetchall()

        if len(vehicles_rs) == 0:
            raise MissingData("Failed to solve model! No customers provided.")

        customers_rs = conn.execute(customers.select().where(customers.columns.model_id == model_id)).fetchall()
        
        if len(customers_rs) == 0:
            raise MissingData("Failed to solve model! No vehicles provided.")

        gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))

        # depot_rs = (id, name, latitude, longitude, address, model_id)
        depot_obj = Depot(0, depot_rs[1], depot_rs[2], depot_rs[3], depot_rs[4])
        customer_objs = create_customers(customers_rs)
        vehicle_objs = create_vehicles(vehicles_rs, depot_obj)
        distance_matrix = create_distance_matrix(depot_obj, customer_objs, gmaps)
        solution = Solution()

        solver(solution, vehicle_objs, customer_objs, distance_matrix)

        return { "solution": solution }
    except InfeasibleModel as error:
        raise HTTPException(400, str(error))
    except Exception:
        raise HTTPException(500, "Failed to solve model.")
