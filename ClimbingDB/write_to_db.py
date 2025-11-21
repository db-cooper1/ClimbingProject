from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

engine = create_engine('', echo=True)

with Session(engine) as session:
    session.commit()