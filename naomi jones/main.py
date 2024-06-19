from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import databases
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Mount static directory for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates environment
templates = Jinja2Templates(directory="templates")

# SQLite database connection
DATABASE_URL = "sqlite:///./form_data.db"
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy models
Base = declarative_base()

class ContactForm(Base):
    __tablename__ = "contact_form"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    subject = Column(String)
    message = Column(Text)

# Dependency to get SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model for form submission
class ContactFormRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

# Route to render the homepage
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route to handle form submission
@app.post("/submit-form/", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    form_data = ContactFormRequest(name=name, email=email, subject=subject, message=message)
    
    # Save form data to the database
    db = SessionLocal()
    db_form = ContactForm(**form_data.dict())
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    db.close()

    # Render thank you page with Jinja2
    return templates.TemplateResponse("thankyou.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)



















