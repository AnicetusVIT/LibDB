# routers/books.py
from fastapi import APIRouter, HTTPException, status
from bson.objectid import ObjectId
from models import BookModel
import database

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_description="Add a new book title and inventory count", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookModel):
    db = database.get_database()
    new_book = await db["books"].insert_one(book.model_dump())
    created_book = await db["books"].find_one({"_id": new_book.inserted_id})
    created_book["_id"] = str(created_book["_id"])
    
    return created_book

@router.put("/{book_id}", response_description="Update book details or total quantity")
async def update_book(book_id: str, book: BookModel):
    db = database.get_database()
    try:
        obj_id = ObjectId(book_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Book ID format")
        
    # $set operator updates fields without overwriting the entire document blindly
    update_result = await db["books"].update_one(
        {"_id": obj_id}, 
        {"$set": book.model_dump()}
    )
    
    if update_result.modified_count == 1:
        updated_book = await db["books"].find_one({"_id": obj_id})
        updated_book["_id"] = str(updated_book["_id"])
        return updated_book
        
    existing_book = await db["books"].find_one({"_id": obj_id})
    if existing_book:
        existing_book["_id"] = str(existing_book["_id"])
        return existing_book
        
    raise HTTPException(status_code=404, detail="Book not found")