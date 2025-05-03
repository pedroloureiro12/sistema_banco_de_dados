from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.settings.config import Settings


settings = Settings()

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqldb://"
    f"{settings.db_user}:"
    f"{settings.db_pass}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


SessionLocal = sessionmaker(autoflush=False, bind=engine)


Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
