# models.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# ---------------------------------------------------------
# 1. Department & Staff (1:N Relationship via Referencing)
# ---------------------------------------------------------

class DepartmentModel(BaseModel):
    name: str
    
    model_config = ConfigDict(populate_by_name=True)

class StaffModel(BaseModel):
    name: str
    department_id: str # References Department._id
    
    model_config = ConfigDict(populate_by_name=True)

# ---------------------------------------------------------
# 2. Student & Library Profile (1:1 Relationship via Embedding)
# ---------------------------------------------------------

class LibraryProfile(BaseModel):
    account_status: str = Field(default="Active")
    fines_due: float = Field(default=0.0)
    card_issue_date: datetime = Field(default_factory=datetime.utcnow)

class StudentModel(BaseModel):
    name: str
    profile: LibraryProfile # Embedded sub-document
    
    model_config = ConfigDict(populate_by_name=True)

# ---------------------------------------------------------
# 3. Books & Transactions (N:M Relationship via Junction)
# ---------------------------------------------------------

class BookModel(BaseModel):
    title: str
    author: str
    cnt: int = Field(default=1, ge=0, description="Total inventory count") 
    
    model_config = ConfigDict(populate_by_name=True)

class TransactionModel(BaseModel):
    book_id: str # References Book._id
    user_id: str # References Student._id or Staff._id
    checkout_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    status: str = Field(default="Borrowed") # e.g., Borrowed, Returned
    
    model_config = ConfigDict(populate_by_name=True)