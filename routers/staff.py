# routers/staff.py
from fastapi import APIRouter, HTTPException, status
from bson.objectid import ObjectId
from models import StaffModel
import database

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.post("/", response_description="Insert a new staff member", status_code=status.HTTP_201_CREATED)
async def create_staff(staff: StaffModel):
    db = database.get_database()
    
    # 1:N Validation: Ensure the referenced department actually exists
    try:
        dept_id = ObjectId(staff.department_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Department ID format")
        
    department = await db["departments"].find_one({"_id": dept_id})
    if not department:
        raise HTTPException(status_code=404, detail="Referenced Department not found")

    new_staff = await db["staff"].insert_one(staff.model_dump())
    created_staff = await db["staff"].find_one({"_id": new_staff.inserted_id})
    created_staff["_id"] = str(created_staff["_id"])
    
    return created_staff

@router.get("/{staff_id}", response_description="Fetch staff details")
async def get_staff(staff_id: str):
    db = database.get_database()
    try:
        staff_doc = await db["staff"].find_one({"_id": ObjectId(staff_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid Staff ID format")
        
    if staff_doc:
        staff_doc["_id"] = str(staff_doc["_id"])
        return staff_doc
    raise HTTPException(status_code=404, detail="Staff member not found")

@router.delete("/{staff_id}", response_description="Drop a staff record")
async def delete_staff(staff_id: str):
    db = database.get_database()
    delete_result = await db["staff"].delete_one({"_id": ObjectId(staff_id)})
    
    if delete_result.deleted_count == 1:
        return {"message": "Staff record deleted successfully"}
    raise HTTPException(status_code=404, detail="Staff member not found")