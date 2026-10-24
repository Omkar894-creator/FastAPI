from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres.cfzjamkyqqgzivfrylil:Emma16stone%231234@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres"
# "sqlite:///./todosapp.db"
# "postgresql://postgres:emma16stone@localhost/TodoApplicationDatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()