from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, ARRAY, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./simulator.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DBSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    competences = Column(String)  # Stored as comma-separated string
    students_data = Column(Text) # New column to store student names and their selected competencies as JSON
    exercises = relationship("DBExercise", back_populates="session")

class DBExercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    date = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    competences = Column(Text)  # Store selected competencies as JSON string
    session = relationship("DBSession", back_populates="exercises")
    observations = relationship("DBObservation", back_populates="exercise")

class DBObservation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ob_code = Column(String, nullable=True)
    competence = Column(String, nullable=True)
    student_name = Column(String, nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    is_checked = Column(Boolean, default=False)
    exercise = relationship("DBExercise", back_populates="observations")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 