# routers/transactions.py
from fastapi import APIRouter, HTTPException, status
from bson.objectid import ObjectId
from models import TransactionModel
from datetime import datetime
import database

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/borrow/", response_description="Create a checkout record and decrement inventory", status_code=status.HTTP_201_CREATED)
async def borrow_book(transaction: TransactionModel):
    db = database.get_database()
    
    try:
        book_id_obj = ObjectId(transaction.book_id)
        user_id_obj = ObjectId(transaction.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # 1. Check Inventory
    tmp_book = await db["books"].find_one({"_id": book_id_obj})
    if not tmp_book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if tmp_book.get("cnt", 0) <= 0:
        raise HTTPException(status_code=400, detail="Book is currently out of stock")

    # 2. Validate User (stk check across both domains)
    stk_student = await db["students"].find_one({"_id": user_id_obj})
    stk_staff = await db["staff"].find_one({"_id": user_id_obj})
    
    if not stk_student and not stk_staff:
        raise HTTPException(status_code=404, detail="User not found in system")

    # 3. Process Checkout
    new_transaction = await db["transactions"].insert_one(transaction.model_dump())
    
    # 4. Decrement Inventory cnt
    await db["books"].update_one(
        {"_id": book_id_obj},
        {"$inc": {"cnt": -1}}
    )

    res = await db["transactions"].find_one({"_id": new_transaction.inserted_id})
    res["_id"] = str(res["_id"])
    return res

@router.post("/return/{transaction_id}", response_description="Close a checkout record and increment inventory")
async def return_book(transaction_id: str):
    db = database.get_database()
    
    try:
        trans_obj = ObjectId(transaction_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Transaction ID format")

    tmp_trans = await db["transactions"].find_one({"_id": trans_obj})
    if not tmp_trans:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    if tmp_trans.get("status") == "Returned":
        raise HTTPException(status_code=400, detail="Book already returned")

    # 1. Update Transaction Status
    await db["transactions"].update_one(
        {"_id": trans_obj},
        {"$set": {"status": "Returned", "return_date": datetime.utcnow()}}
    )

    # 2. Increment Inventory cnt
    book_id_obj = ObjectId(tmp_trans["book_id"])
    await db["books"].update_one(
        {"_id": book_id_obj},
        {"$inc": {"cnt": 1}}
    )

    return {"message": "Book returned successfully, inventory updated."}