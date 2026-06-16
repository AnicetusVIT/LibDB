# main.py
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import database
from config import settings
from routers import departments, staff, students, books, transactions

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.client = database.AsyncIOMotorClient(settings.mongodb_url)
    database.db = database.client[settings.database_name]
    print(f"Connected to {settings.database_name}")
    yield
    database.client.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Performance Tracking Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    # Log it to the terminal for debugging
    print(f"Path: {request.url.path} | Time: {process_time:.4f}s")
    return response

# Global Exception Handler for unexpected database/server errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Engine Error", "detail": str(exc)},
    )

# Include Routers
app.include_router(departments.router)
app.include_router(staff.router)
app.include_router(students.router)
app.include_router(books.router)
app.include_router(transactions.router)