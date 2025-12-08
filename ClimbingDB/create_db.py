from sqlalchemy import create_engine
from models import Base

engine = create_engine("sqlite:///climbing.db", echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)