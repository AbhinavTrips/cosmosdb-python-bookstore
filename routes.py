from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
import database

from models import Book


router = APIRouter()

@router.get("/getAllBooks", response_description="List of all books", response_model=List[Book])
async def list_books(request: Request):
    books = [book async for book in request.app.books_container.read_all_items()]
    return books

@router.get("/getBookById", response_description="Get a book by ID", response_model=Book)
async def get_book_by_id(request: Request, id: str, pk: str):
    book = await request.app.books_container.read_item(id, partition_key=pk)
    return book

@router.post("/removeComment", response_description="Remove a comment from a book", response_model=Book)
async def remove_comment(request: Request, id: str, pk: str, comment_index: int):
    books_container = request.app.books_container
    operations = [
        { "op": 'remove', "path": '/reviewcomments/'+str(comment_index) }
    ]
    response = await books_container.patch_item(item=id, partition_key=pk, patch_operations=operations)
    return response

@router.get("/get20Books", response_description="List of all books")
async def list_books20(request: Request, page_offset: int = 0, limit: int = 20, rating: float = 0.0, genre: str = None, author: str = None, title: str = None, sortby: str = "title"):
    books_container = request.app.books_container
    query_items_response = books_container.query_items(
            query="SELECT c.title, c.author, c.img, c.rating, c.format FROM c  WHERE c.rating > @rating ORDER BY c."+sortby+" OFFSET @offset LIMIT @limit",
            parameters=[
                dict(
                    name="@offset",
                    value=page_offset*limit
                ),
                dict(
                    name="@limit",
                    value=limit
                ),
            dict(
                name="@rating",
                value=rating
                )            
            ]
        )
        
    items = [jsonable_encoder(book) async for book in query_items_response]
    return JSONResponse(content=items)
