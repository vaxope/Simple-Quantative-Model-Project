from src.db.session import engine
from src.db.models import Base

def main():
    Base.metadata.create_all(engine)
    print("Tables Created: ", list(Base.metadata.tables.keys()))

if __name__ == "__main__":
    main()