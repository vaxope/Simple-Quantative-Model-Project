from src.db.session import engine
from src.db.models import Base

# Drops existing tables and creates fresh ones matching your SQLAlchemy models
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)