from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from database import engine, Base, SessionLocal
from programmes import preload_programmes
import auth, programmes, reports

load_dotenv()

app = FastAPI(title="Digital Monitoring Tool API")

# include routers
app.include_router(auth.router)
app.include_router(programmes.router)
app.include_router(reports.router)

# global exception handlers
@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    # In production, you would log the exception details
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.on_event("startup")
def on_startup():
    # create DB and tables
    Base.metadata.create_all(bind=engine)
    # preload sample programmes
    db = SessionLocal()
    try:
        preload_programmes(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
