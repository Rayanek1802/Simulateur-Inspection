from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import json
from pydantic import BaseModel

from .database import SessionLocal, DBSession, DBExercise, DBObservation
from .ob_detector import detect_ob, calculate_how_many, calculate_how_often

# Predefined observations with their competencies
OBSERVATIONS_BY_COMPETENCY: Dict[str, List[str]] = {
    "KNO": [
        "Demonstrates knowledge and understanding of relevant information, operating instructions, aircraft systems and the operating environment",  # OB 0.1
        "Demonstrates practical and applicable knowledge of limitations and systems and their interaction",  # OB 0.2
        "Demonstrates the required knowledge of published operating instructions",  # OB 0.3
        "Demonstrates appropriate knowledge of the air traffic environment and the operational infrastructure (including air traffic routings, weather, and NOTAMs)",  # OB 0.4
        "Demonstrates appropriate knowledge of applicable legislation",  # OB 0.5
        "Knows where to source required information",  # OB 0.6
        "Demonstrates a positive interest in acquiring knowledge",  # OB 0.7
        "Is able to apply knowledge effectively"  # OB 0.8
    ],
    "LTW": [
        "Influences others to contribute to a shared purpose. Collaborates to accomplish the goals of the team",  # OB 5.1
        "Encourages team participation and open communication",  # OB 5.2
        "Engages others in planning",  # OB 5.3
        "Demonstrates initiative and provides direction when required",  # OB 5.4
        "Considers inputs from others",  # OB 5.5
        "Gives and receives feedback constructively and admits mistakes",  # OB 5.6
        "Addresses and resolves conflicts and disagreements in a constructive manner",  # OB 5.7
        "Exercises decisive leadership when required",  # OB 5.8
        "Uses initiative, gives direction and takes responsibility when required. Accepts responsibility for decisions and actions",  # OB 5.9
        "Carries out instructions when directed",  # OB 5.10
        "Applies effective intervention strategies to resolve identified deviations",  # OB 5.11
        "Manages cultural and language challenges, as applicable",  # OB 5.12
        "Confidently says and does what is important for safety, resolving deviations identified while monitoring using appropriate escalation of communication",  # EY OB 5.13
        "Demonstrates empathy, respect and tolerance for other people"  # EY OB 5.14
    ],
    "PSD": [
        "Identifies, assesses and manages threats and errors in a timely manner",  # OB 6.1
        "Seeks accurate and adequate information from appropriate sources",  # OB 6.2
        "Identifies and verifies what and why things have gone wrong, if appropriate",  # OB 6.3
        "Perseveres in working through problems whilst prioritising safety",  # OB 6.4
        "Identifies and considers appropriate options",  # OB 6.5
        "Applies appropriate and timely decision-making techniques",  # OB 6.6
        "Monitors, reviews and adapts decisions as required",  # OB 6.7
        "Adapts when faced with situations where no guidance or procedure exists",  # OB 6.8
        "Demonstrates resilience when encountering an unexpected event",  # OB 6.9
        "Considers risks but does not take unnecessary risks"  # EY OB 6.10
    ],
    "SAW": [
        "Monitors and assesses the state of the aeroplane and its systems",  # OB 7.1
        "Monitors and assesses the aeroplane's energy state, and its anticipated flight path",  # OB 7.2
        "Monitors and assesses the general environment as it may affect the operation",  # OB 7.3
        "Validates the accuracy of information and checks for gross errors",  # OB 7.4
        "Maintains awareness of the people involved in or affected by the operation and their capacity to perform as expected",  # OB 7.5
        "Develops effective contingency plans for threats, associated risks and potential errors",  # OB 7.6
        "Responds to indications of reduced situation awareness",  # OB 7.7
        "Keeps track of time and fuel"  # EY OB 7.8
    ],
    "WLM": [
        "Exercises self-control in all situations",  # OB 8.1
        "Plans, prioritises and schedules appropriate tasks effectively",  # OB 8.2
        "Manages time efficiently when carrying out tasks",  # OB 8.3
        "Offers and gives assistance",  # OB 8.4
        "Delegates tasks",  # OB 8.5
        "Seeks and accepts assistance, when appropriate",  # OB 8.6
        "Monitors, reviews and cross-checks actions conscientiously",  # OB 8.7
        "Verifies that tasks are completed to the expected outcome",  # OB 8.8
        "Manages and recovers from interruptions, distractions, variations and failures effectively while performing tasks"  # OB 8.9
    ],
    "PRO": [
        "Identifies where to find procedures and regulations",  # OB 1.1
        "Applies relevant operating instructions, procedures and techniques in a timely manner",  # OB 1.2
        "Follows SOPs unless a higher degree of safety dictates an appropriate deviation",  # OB 1.3
        "Operates aircraft systems and associated equipment correctly",  # OB 1.4
        "Monitors aircraft systems status",  # OB 1.5
        "Complies with applicable regulations",  # OB 1.6
        "Applies relevant procedural knowledge",  # OB 1.7
        "Safely manages the aircraft to achieve best value for the operation, including fuel, the environment, passenger comfort and punctuality"  # EY OB 1.8
    ],
    "COM": [
        "Determines that the recipient is ready and able to receive information",  # OB 2.1
        "Selects appropriately what, when, how and with whom to communicate",  # OB 2.2
        "Conveys messages clearly, accurately, timely and concisely",  # OB 2.3
        "Confirms that the recipient demonstrates understanding of important information",  # OB 2.4
        "Listens actively and demonstrates understanding when receiving information",  # OB 2.5
        "Asks relevant and effective questions",  # OB 2.6
        "Uses appropriate escalation in communication to resolve identified deviations",  # OB 2.7
        "Uses and interprets non-verbal communication in a manner appropriate to the organisational and social culture",  # OB 2.8
        "Adheres to standard radiotelephony phraseology and procedures",  # OB 2.9
        "Reads, interprets, constructs and responds to datalink messages in English",  # OB 2.10
        "Is receptive to other people\'s views and is willing to compromise"  # EY OB 2.11
    ],
    "FPA": [
        "Uses appropriate flight management, guidance systems and automation, as installed and applicable to the conditions",  # OB 3.1
        "Monitors and detects deviations from the intended flight path and takes appropriate action",  # OB 3.2
        "Manages the flight path to achieve optimum operational performance",  # OB 3.3
        "Maintains the intended flight path during flight using automation whilst monitoring and managing other tasks and distractions",  # OB 3.4
        "Selects appropriate level and mode of automation in a timely manner considering phase of flight and workload",  # OB 3.5
        "Effectively monitors automation, including engagement and automatic mode transitions",  # OB 3.6
        "Contains the aircraft within the normal flight envelope"  # EY OB 3.7
    ],
    "FPM": [
        "Controls the aircraft manually with accuracy and smoothness as appropriate to the situation",  # OB 4.1
        "Monitors and detects deviations from the intended flight path and takes appropriate action",  # OB 4.2
        "Manually controls the aeroplane using the relationship between aeroplane attitude, speed and thrust, and navigation signals or visual information",  # OB 4.3
        "Manages the flight path to achieve optimum operational performance",  # OB 4.4
        "Maintains the intended flight path during manual flight whilst monitoring and managing other tasks and distractions",  # OB 4.5
        "Uses appropriate flight management and guidance systems, as installed and applicable to the conditions",  # OB 4.6
        "Effectively monitors flight guidance systems including engaging and automatic mode transitions",  # OB 4.7
        "Contains the aircraft within the normal flight envelope"  # EY OB 4.8
    ]
}

# New Pydantic model for a student
class StudentInput(BaseModel):
    name: str
    # competences: List[str]

# Updated Pydantic models for request validation
class SessionCreate(BaseModel):
    students: List[StudentInput]

class ExerciseCreate(BaseModel):
    name: str
    student_name: str
    competences: List[str]

class ObservationUpdate(BaseModel):
    is_checked: bool

class Exercise(BaseModel):
    id: int
    name: str
    is_completed: bool
    date: datetime

class Observation(BaseModel):
    id: int
    text: str
    timestamp: datetime
    ob_code: Optional[str]
    competence: Optional[str]
    is_checked: bool

app = FastAPI(title="Flight Instructor Evaluation API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Flight Instructor Evaluation API"}

@app.get("/sessions/")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(DBSession).all()
    return [{
        "id": session.id,
        "date": session.date,
        "competences": session.competences.split(",") if session.competences else [],
        "students": json.loads(session.students_data) if session.students_data else []
    } for session in sessions]

@app.get("/sessions/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    exercises = [{
        "id": ex.id,
        "name": ex.name,
        "date": ex.date,
        "is_completed": ex.is_completed,
        "competences": json.loads(ex.competences) if ex.competences else [],
        "observations": [{
            "id": obs.id,
            "text": obs.text,
            "timestamp": obs.timestamp,
            "ob_code": obs.ob_code,
            "competence": obs.competence,
            "is_checked": obs.is_checked,
            "student_name": obs.student_name
        } for obs in ex.observations]
    } for ex in session.exercises]
    
    return {
        "id": session.id,
        "date": session.date,
        "students": json.loads(session.students_data) if session.students_data else [],
        "exercises": exercises
    }

@app.post("/sessions/")
async def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    db_session = DBSession(
        date=datetime.utcnow(),
        students_data=json.dumps([s.dict() for s in session.students]) # Store student data as JSON string
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return {
        "id": db_session.id,
        "date": db_session.date,
        "students": session.students,
        "exercises": []
    }

@app.post("/sessions/{session_id}/exercises/")
async def create_exercise(
    session_id: int,
    exercise: ExerciseCreate,
    db: Session = Depends(get_db)
):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify student exists in session
    students_data = json.loads(session.students_data)
    student_exists = any(student["name"] == exercise.student_name for student in students_data)
    if not student_exists:
        raise HTTPException(status_code=400, detail=f"Student {exercise.student_name} not found in this session.")

    db_exercise = DBExercise(
        name=exercise.name,
        session_id=session_id,
        date=datetime.utcnow(),
        competences=json.dumps(exercise.competences)  # Store selected competencies
    )
    
    # Create observations only for the selected competencies
    for competency in exercise.competences:
        if competency in OBSERVATIONS_BY_COMPETENCY:
            for obs_text in OBSERVATIONS_BY_COMPETENCY[competency]:
                ob_result = detect_ob(obs_text)
                db_observation = DBObservation(
                    text=obs_text,
                    timestamp=datetime.utcnow(),
                    ob_code=ob_result["ob_code"] if ob_result else None,
                    competence=competency,
                    student_name=exercise.student_name,
                    exercise=db_exercise
                )
                db.add(db_observation)
    
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return {
        "id": db_exercise.id,
        "name": db_exercise.name,
        "date": db_exercise.date,
        "is_completed": db_exercise.is_completed,
        "competences": exercise.competences,
        "observations": [{
            "id": obs.id,
            "text": obs.text,
            "timestamp": obs.timestamp,
            "ob_code": obs.ob_code,
            "competence": obs.competence,
            "is_checked": obs.is_checked,
            "student_name": obs.student_name
        } for obs in db_exercise.observations]
    }

@app.put("/exercises/{exercise_id}/observations/{observation_id}")
async def update_observation(
    exercise_id: int,
    observation_id: int,
    observation: ObservationUpdate,
    db: Session = Depends(get_db)
):
    db_observation = db.query(DBObservation).filter(
        DBObservation.id == observation_id,
        DBObservation.exercise_id == exercise_id
    ).first()
    
    if not db_observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    db_observation.is_checked = observation.is_checked
    db.commit()
    db.refresh(db_observation)
    
    return {
        "id": db_observation.id,
        "text": db_observation.text,
        "timestamp": db_observation.timestamp,
        "ob_code": db_observation.ob_code,
        "competence": db_observation.competence,
        "is_checked": db_observation.is_checked
    }

@app.put("/exercises/{exercise_id}/complete")
async def complete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    exercise = db.query(DBExercise).filter(DBExercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise.is_completed = True
    db.commit()
    db.refresh(exercise)
    
    return {
        "id": exercise.id,
        "name": exercise.name,
        "date": exercise.date,
        "is_completed": exercise.is_completed
    }

@app.get("/sessions/{session_id}/report/")
async def generate_report(
    session_id: int, 
    safety_scores: str = Query(..., description="""JSON string of safety scores per student, e.g., '{"Student A": 4, "Student B": 5}'"""),
    db: Session = Depends(get_db)
):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    safety_scores_dict = json.loads(safety_scores)
    
    students_data = json.loads(session.students_data)
    
    full_report = {}
    
    for student in students_data:
        student_name = student["name"]
        student_safety_score = safety_scores_dict.get(student_name, 5) # Default to 5 if not provided

        # Collect observations relevant to this student from all exercises
        student_observations = []
        student_competences_evaluated = set() # Collect unique competences evaluated for this student
        unchecked_observations = [] # Liste des observations non cochées
        for exercise in session.exercises:
            # Only consider exercises that the current student participated in
            if any(obs.student_name == student_name for obs in exercise.observations):
                for obs in exercise.observations:
                    if obs.student_name == student_name:
                        obs_dict = {
                            "text": obs.text,
                            "ob_code": obs.ob_code,
                            "competence": obs.competence,
                            "is_checked": obs.is_checked
                        }
                        student_observations.append(obs_dict)
                        if obs.competence: # Add competence from observation if it exists
                            student_competences_evaluated.add(obs.competence)
                        if not obs.is_checked:
                            unchecked_observations.append({
                                "text": obs.text,
                                "ob_code": obs.ob_code,
                                "competence": obs.competence
                            })
        
        student_report = {}
        for comp in sorted(list(student_competences_evaluated)):
            how_many = calculate_how_many(student_observations, comp)
            how_often = calculate_how_often(student_observations, comp)
            final_grade = min(how_many, how_often, student_safety_score)
            # Liste des observations pour cette compétence, sans doublon mais seulement pour cette compétence
            seen_obs = set()
            comp_observations = []
            for obs in student_observations:
                if obs["competence"] == comp:
                    key = (obs["text"], obs["ob_code"], obs["competence"])
                    if key not in seen_obs:
                        comp_observations.append({"text": obs["text"], "ob_code": obs["ob_code"]})
                        seen_obs.add(key)
            student_report[comp] = {
                "how_many": how_many,
                "how_often": how_often,
                "safety_score": student_safety_score,
                "final_grade": final_grade,
                "observations": comp_observations
            }
        full_report[student_name] = {
            "report": student_report,
            "unchecked_observations": unchecked_observations
        }
    
    return full_report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 