from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://gqlnsnxc:42EpsYIsB9jR77hGDp8FTJSP8fdPSB8I@horton.db.elephantsql.com/gqlnsnxc"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

Base = declarative_base()