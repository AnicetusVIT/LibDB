# routers/students.py
from fastapi import APIRouter, HTTPException, status
from bson.objectid import ObjectId
from models import StudentModel
import database

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_description="Insert a new student with their embedded 1:1 library profile", status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentModel):
    db = database.get_database()
    
    # The embedded profile is already validated and structured by Pydantic
    new_student = await db["students"].insert_one(student.model_dump())
    created_student = await db["students"].find_one({"_id": new_student.inserted_id})
    created_student["_id"] = str(created_student["_id"])
    
    return created_student

@router.get("/{student_id}", response_description="Retrieve student data")
async def get_student(student_id: str):
    db = database.get_database()
    try:
        student_doc = await db["students"].find_one({"_id": ObjectId(student_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid Student ID format")
        
    if student_doc:
        student_doc["_id"] = str(student_doc["_id"])
        return student_doc
    raise HTTPException(status_code=404, detail="Student not found")