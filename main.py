from fastapi import FastAPI
from dotenv import dotenv_values
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions
from routes import router as todo_router

config = dotenv_values(".env")
app = FastAPI()
DATABASE_NAME = "cosmosbookstore"
BOOKS_CONTAINER = "books"
GENRES_CONTAINER = "genres"

app.include_router(todo_router, tags=["todos"], prefix="/todos")

@app.on_event("startup")
async def startup_db_client():
    app.cosmos_client = CosmosClient(config["URI"], credential = config["KEY"])
    await get_or_create_db(DATABASE_NAME)
    print(await get_or_create_container(BOOKS_CONTAINER))


async def get_or_create_db(db_name):
    try:
        app.database  = app.cosmos_client.get_database_client(db_name)
        return await app.database.read()
    except exceptions.CosmosResourceNotFoundError:
        print("Creating database")
        return await app.cosmos_client.create_database(db_name)
     
async def get_or_create_container(BOOKS_CONTAINER):
    try:        
        app.books_container = app.database.get_container_client(BOOKS_CONTAINER)
        return await app.books_container.read()   
    except exceptions.CosmosResourceNotFoundError:
        print("Creating container with id as partition key")
        return await app.database.create_container(id=BOOKS_CONTAINER, partition_key=PartitionKey(path="/_id"))
    except exceptions.CosmosHttpResponseError:
        raise