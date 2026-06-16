# routers/departments.py
from fastapi import APIRouter, HTTPException, status
from models import DepartmentModel
import database

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_description="Create a new academic department", status_code=status.HTTP_201_CREATED)
async def create_department(department: DepartmentModel):
    db = database.get_database()
    # model_dump() serializes the Pydantic model to a standard dictionary
    new_dept = await db["departments"].insert_one(department.model_dump())
    
    # Fetch the created document to return it
    created_dept = await db["departments"].find_one({"_id": new_dept.inserted_id})
    created_dept["_id"] = str(created_dept["_id"]) # Cast BSON ObjectId to string for JSON
    
    return created_dept

@router.get("/", response_description="Retrieve all departments")
async def get_departments():
    db = database.get_database()
    # to_list(length) fetches multiple documents asynchronously
    departments = await db["departments"].find().to_list(1000)
    
    for dept in departments:
        dept["_id"] = str(dept["_id"])
        
    return departments