# backend/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

# Usaremos la carpeta 'feedback' como pediste
DB_FOLDER = "/app/feedback"
DB_PATH = os.path.join(DB_FOLDER, "feedback.db")

# Asegurarse de que el directorio existe
os.makedirs(DB_FOLDER, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la Tabla para guardar el feedback
class FeedbackLog(Base):
    __tablename__ = "feedback_logs"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    question = Column(Text)
    answer = Column(Text)
    feedback_type = Column(String)
    feedback_details = Column(Text, nullable=True)
    retrieved_chunks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Función para crear la tabla
def init_db():
    Base.metadata.create_all(bind=engine)

# Función para obtener la sesión de la DB en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()