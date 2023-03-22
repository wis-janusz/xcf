from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def create_url(
    username: str = "postgres",
    password: str = "12345",
    host: str = "localhost",
    port: str = "5433",
    db_name="xcf_db",
    driver: str = "postgresql+psycopg2",
):

    url_string = f"{driver}://{username}:{password}@{host}:{port}/{db_name}"
    return url_string

def create_db_connection(name: str = "xcf_db"):
    db_url = create_url()
    engine = create_engine(db_url, echo=False, future=True)
    return engine
