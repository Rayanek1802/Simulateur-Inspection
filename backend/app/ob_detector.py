from typing import Dict, List, Optional
from difflib import SequenceMatcher

# Define OB categories and their descriptions
OB_DEFINITIONS = {
    "KNO": {
        "OB 0.1": "Demonstrates knowledge and understanding of relevant information, operating instructions, aircraft systems and the operating environment",
        "OB 0.2": "Demonstrates practical and applicable knowledge of limitations and systems and their interaction",
        "OB 0.3": "Demonstrates the required knowledge of published operating instructions",
        "OB 0.4": "Demonstrates appropriate knowledge of the air traffic environment and the operational infrastructure (including air traffic routings, weather, and NOTAMs)",
        "OB 0.5": "Demonstrates appropriate knowledge of applicable legislation",
        "OB 0.6": "Knows where to source required information",
        "OB 0.7": "Demonstrates a positive interest in acquiring knowledge",
        "OB 0.8": "Is able to apply knowledge effectively"
    },
    "LTW": {
        "OB 5.1": "Influences others to contribute to a shared purpose. Collaborates to accomplish the goals of the team",
        "OB 5.2": "Encourages team participation and open communication",
        "OB 5.3": "Engages others in planning",
        "OB 5.4": "Demonstrates initiative and provides direction when required",
        "OB 5.5": "Considers inputs from others",
        "OB 5.6": "Gives and receives feedback constructively and admits mistakes",
        "OB 5.7": "Addresses and resolves conflicts and disagreements in a constructive manner",
        "OB 5.8": "Exercises decisive leadership when required",
        "OB 5.9": "Uses initiative, gives direction and takes responsibility when required. Accepts responsibility for decisions and actions",
        "OB 5.10": "Carries out instructions when directed",
        "OB 5.11": "Applies effective intervention strategies to resolve identified deviations",
        "OB 5.12": "Manages cultural and language challenges, as applicable",
        "EY OB 5.13": "Confidently says and does what is important for safety, resolving deviations identified while monitoring using appropriate escalation of communication",
        "EY OB 5.14": "Demonstrates empathy, respect and tolerance for other people"
    },
    "PSD": {
        "OB 6.1": "Identifies, assesses and manages threats and errors in a timely manner",
        "OB 6.2": "Seeks accurate and adequate information from appropriate sources",
        "OB 6.3": "Identifies and verifies what and why things have gone wrong, if appropriate",
        "OB 6.4": "Perseveres in working through problems whilst prioritising safety",
        "OB 6.5": "Identifies and considers appropriate options",
        "OB 6.6": "Applies appropriate and timely decision-making techniques",
        "OB 6.7": "Monitors, reviews and adapts decisions as required",
        "OB 6.8": "Adapts when faced with situations where no guidance or procedure exists",
        "OB 6.9": "Demonstrates resilience when encountering an unexpected event",
        "EY OB 6.10": "Considers risks but does not take unnecessary risks"
    },
    "SAW": {
        "OB 7.1": "Monitors and assesses the state of the aeroplane and its systems",
        "OB 7.2": "Monitors and assesses the aeroplane's energy state, and its anticipated flight path",
        "OB 7.3": "Monitors and assesses the general environment as it may affect the operation",
        "OB 7.4": "Validates the accuracy of information and checks for gross errors",
        "OB 7.5": "Maintains awareness of the people involved in or affected by the operation and their capacity to perform as expected",
        "OB 7.6": "Develops effective contingency plans for threats, associated risks and potential errors",
        "OB 7.7": "Responds to indications of reduced situation awareness",
        "EY OB 7.8": "Keeps track of time and fuel"
    },
    "WLM": {
        "OB 8.1": "Exercises self-control in all situations",
        "OB 8.2": "Plans, prioritises and schedules appropriate tasks effectively",
        "OB 8.3": "Manages time efficiently when carrying out tasks",
        "OB 8.4": "Offers and gives assistance",
        "OB 8.5": "Delegates tasks",
        "OB 8.6": "Seeks and accepts assistance, when appropriate",
        "OB 8.7": "Monitors, reviews and cross-checks actions conscientiously",
        "OB 8.8": "Verifies that tasks are completed to the expected outcome",
        "OB 8.9": "Manages and recovers from interruptions, distractions, variations and failures effectively while performing tasks"
    },
    "PRO": {
        "OB 1.1": "Identifies where to find procedures and regulations",
        "OB 1.2": "Applies relevant operating instructions, procedures and techniques in a timely manner",
        "OB 1.3": "Follows SOPs unless a higher degree of safety dictates an appropriate deviation",
        "OB 1.4": "Operates aircraft systems and associated equipment correctly",
        "OB 1.5": "Monitors aircraft systems status",
        "OB 1.6": "Complies with applicable regulations",
        "OB 1.7": "Applies relevant procedural knowledge",
        "EY OB 1.8": "Safely manages the aircraft to achieve best value for the operation, including fuel, the environment, passenger comfort and punctuality"
    },
    "COM": {
        "OB 2.1": "Determines that the recipient is ready and able to receive information",
        "OB 2.2": "Selects appropriately what, when, how and with whom to communicate",
        "OB 2.3": "Conveys messages clearly, accurately, timely and concisely",
        "OB 2.4": "Confirms that the recipient demonstrates understanding of important information",
        "OB 2.5": "Listens actively and demonstrates understanding when receiving information",
        "OB 2.6": "Asks relevant and effective questions",
        "OB 2.7": "Uses appropriate escalation in communication to resolve identified deviations",
        "OB 2.8": "Uses and interprets non-verbal communication in a manner appropriate to the organisational and social culture",
        "OB 2.9": "Adheres to standard radiotelephony phraseology and procedures",
        "OB 2.10": "Reads, interprets, constructs and responds to datalink messages in English",
        "EY OB 2.11": "Is receptive to other people\'s views and is willing to compromise"
    },
    "FPA": {
        "OB 3.1": "Uses appropriate flight management, guidance systems and automation, as installed and applicable to the conditions",
        "OB 3.4": "Maintains the intended flight path during flight using automation whilst monitoring and managing other tasks and distractions",
        "OB 3.5": "Selects appropriate level and mode of automation in a timely manner considering phase of flight and workload",
        "OB 3.6": "Effectively monitors automation, including engagement and automatic mode transitions"
    },
    "FPM": {
        "OB 4.2": "Monitors and detects deviations from the intended flight path and takes appropriate action",
        "OB 4.4": "Manages the flight path to achieve optimum operational performance",
        "EY OB 4.8": "Contains the aircraft within the normal flight envelope"
    }
}

# Mapping of observations to their OB codes and competencies
OB_MAPPING = {
    # KNO Observations
    "Demonstrates knowledge and understanding of relevant information, operating instructions, aircraft systems and the operating environment": {"ob_code": "OB 0.1", "competence": "KNO"},
    "Demonstrates practical and applicable knowledge of limitations and systems and their interaction": {"ob_code": "OB 0.2", "competence": "KNO"},
    "Demonstrates the required knowledge of published operating instructions": {"ob_code": "OB 0.3", "competence": "KNO"},
    "Demonstrates appropriate knowledge of the air traffic environment and the operational infrastructure (including air traffic routings, weather, and NOTAMs)": {"ob_code": "OB 0.4", "competence": "KNO"},
    "Demonstrates appropriate knowledge of applicable legislation": {"ob_code": "OB 0.5", "competence": "KNO"},
    "Knows where to source required information": {"ob_code": "OB 0.6", "competence": "KNO"},
    "Demonstrates a positive interest in acquiring knowledge": {"ob_code": "OB 0.7", "competence": "KNO"},
    "Is able to apply knowledge effectively": {"ob_code": "OB 0.8", "competence": "KNO"},

    # LTW Observations
    "Influences others to contribute to a shared purpose. Collaborates to accomplish the goals of the team": {"ob_code": "OB 5.1", "competence": "LTW"},
    "Encourages team participation and open communication": {"ob_code": "OB 5.2", "competence": "LTW"},
    "Engages others in planning": {"ob_code": "OB 5.3", "competence": "LTW"},
    "Demonstrates initiative and provides direction when required": {"ob_code": "OB 5.4", "competence": "LTW"},
    "Considers inputs from others": {"ob_code": "OB 5.5", "competence": "LTW"},
    "Gives and receives feedback constructively and admits mistakes": {"ob_code": "OB 5.6", "competence": "LTW"},
    "Addresses and resolves conflicts and disagreements in a constructive manner": {"ob_code": "OB 5.7", "competence": "LTW"},
    "Exercises decisive leadership when required": {"ob_code": "OB 5.8", "competence": "LTW"},
    "Uses initiative, gives direction and takes responsibility when required. Accepts responsibility for decisions and actions": {"ob_code": "OB 5.9", "competence": "LTW"},
    "Carries out instructions when directed": {"ob_code": "OB 5.10", "competence": "LTW"},
    "Applies effective intervention strategies to resolve identified deviations": {"ob_code": "OB 5.11", "competence": "LTW"},
    "Manages cultural and language challenges, as applicable": {"ob_code": "OB 5.12", "competence": "LTW"},
    "Confidently says and does what is important for safety, resolving deviations identified while monitoring using appropriate escalation of communication": {"ob_code": "EY OB 5.13", "competence": "LTW"},
    "Demonstrates empathy, respect and tolerance for other people": {"ob_code": "EY OB 5.14", "competence": "LTW"},

    # PSD Observations
    "Identifies, assesses and manages threats and errors in a timely manner": {"ob_code": "OB 6.1", "competence": "PSD"},
    "Seeks accurate and adequate information from appropriate sources": {"ob_code": "OB 6.2", "competence": "PSD"},
    "Identifies and verifies what and why things have gone wrong, if appropriate": {"ob_code": "OB 6.3", "competence": "PSD"},
    "Perseveres in working through problems whilst prioritising safety": {"ob_code": "OB 6.4", "competence": "PSD"},
    "Identifies and considers appropriate options": {"ob_code": "OB 6.5", "competence": "PSD"},
    "Applies appropriate and timely decision-making techniques": {"ob_code": "OB 6.6", "competence": "PSD"},
    "Monitors, reviews and adapts decisions as required": {"ob_code": "OB 6.7", "competence": "PSD"},
    "Adapts when faced with situations where no guidance or procedure exists": {"ob_code": "OB 6.8", "competence": "PSD"},
    "Demonstrates resilience when encountering an unexpected event": {"ob_code": "OB 6.9", "competence": "PSD"},
    "Considers risks but does not take unnecessary risks": {"ob_code": "EY OB 6.10", "competence": "PSD"},

    # SAW Observations
    "Monitors and assesses the state of the aeroplane and its systems": {"ob_code": "OB 7.1", "competence": "SAW"},
    "Monitors and assesses the aeroplane's energy state, and its anticipated flight path": {"ob_code": "OB 7.2", "competence": "SAW"},
    "Monitors and assesses the general environment as it may affect the operation": {"ob_code": "OB 7.3", "competence": "SAW"},
    "Validates the accuracy of information and checks for gross errors": {"ob_code": "OB 7.4", "competence": "SAW"},
    "Maintains awareness of the people involved in or affected by the operation and their capacity to perform as expected": {"ob_code": "OB 7.5", "competence": "SAW"},
    "Develops effective contingency plans for threats, associated risks and potential errors": {"ob_code": "OB 7.6", "competence": "SAW"},
    "Responds to indications of reduced situation awareness": {"ob_code": "OB 7.7", "competence": "SAW"},
    "Keeps track of time and fuel": {"ob_code": "EY OB 7.8", "competence": "SAW"},

    # WLM Observations
    "Exercises self-control in all situations": {"ob_code": "OB 8.1", "competence": "WLM"},
    "Plans, prioritises and schedules appropriate tasks effectively": {"ob_code": "OB 8.2", "competence": "WLM"},
    "Manages time efficiently when carrying out tasks": {"ob_code": "OB 8.3", "competence": "WLM"},
    "Offers and gives assistance": {"ob_code": "OB 8.4", "competence": "WLM"},
    "Delegates tasks": {"ob_code": "OB 8.5", "competence": "WLM"},
    "Seeks and accepts assistance, when appropriate": {"ob_code": "OB 8.6", "competence": "WLM"},
    "Monitors, reviews and cross-checks actions conscientiously": {"ob_code": "OB 8.7", "competence": "WLM"},
    "Verifies that tasks are completed to the expected outcome": {"ob_code": "OB 8.8", "competence": "WLM"},
    "Manages and recovers from interruptions, distractions, variations and failures effectively while performing tasks": {"ob_code": "OB 8.9", "competence": "WLM"},

    # PRO Observations
    "Identifies where to find procedures and regulations": {"ob_code": "OB 1.1", "competence": "PRO"},
    "Applies relevant operating instructions, procedures and techniques in a timely manner": {"ob_code": "OB 1.2", "competence": "PRO"},
    "Follows SOPs unless a higher degree of safety dictates an appropriate deviation": {"ob_code": "OB 1.3", "competence": "PRO"},
    "Operates aircraft systems and associated equipment correctly": {"ob_code": "OB 1.4", "competence": "PRO"},
    "Monitors aircraft systems status": {"ob_code": "OB 1.5", "competence": "PRO"},
    "Complies with applicable regulations": {"ob_code": "OB 1.6", "competence": "PRO"},
    "Applies relevant procedural knowledge": {"ob_code": "OB 1.7", "competence": "PRO"},
    "Safely manages the aircraft to achieve best value for the operation, including fuel, the environment, passenger comfort and punctuality": {"ob_code": "EY OB 1.8", "competence": "PRO"},

    # COM Observations
    "Determines that the recipient is ready and able to receive information": {"ob_code": "OB 2.1", "competence": "COM"},
    "Selects appropriately what, when, how and with whom to communicate": {"ob_code": "OB 2.2", "competence": "COM"},
    "Conveys messages clearly, accurately, timely and concisely": {"ob_code": "OB 2.3", "competence": "COM"},
    "Confirms that the recipient demonstrates understanding of important information": {"ob_code": "OB 2.4", "competence": "COM"},
    "Listens actively and demonstrates understanding when receiving information": {"ob_code": "OB 2.5", "competence": "COM"},
    "Asks relevant and effective questions": {"ob_code": "OB 2.6", "competence": "COM"},
    "Uses appropriate escalation in communication to resolve identified deviations": {"ob_code": "OB 2.7", "competence": "COM"},
    "Uses and interprets non-verbal communication in a manner appropriate to the organisational and social culture": {"ob_code": "OB 2.8", "competence": "COM"},
    "Adheres to standard radiotelephony phraseology and procedures": {"ob_code": "OB 2.9", "competence": "COM"},
    "Reads, interprets, constructs and responds to datalink messages in English": {"ob_code": "OB 2.10", "competence": "COM"},
    "Is receptive to other people\'s views and is willing to compromise": {"ob_code": "EY OB 2.11", "competence": "COM"},

    # FPA Observations
    "Uses appropriate flight management, guidance systems and automation, as installed and applicable to the conditions": {"ob_code": "OB 3.1", "competence": "FPA"},
    "Maintains the intended flight path during flight using automation whilst monitoring and managing other tasks and distractions": {"ob_code": "OB 3.4", "competence": "FPA"},
    "Selects appropriate level and mode of automation in a timely manner considering phase of flight and workload": {"ob_code": "OB 3.5", "competence": "FPA"},
    "Effectively monitors automation, including engagement and automatic mode transitions": {"ob_code": "OB 3.6", "competence": "FPA"},

    # FPM Observations
    "Monitors and detects deviations from the intended flight path and takes appropriate action": {"ob_code": "OB 4.2", "competence": "FPM"},
    "Manages the flight path to achieve optimum operational performance": {"ob_code": "OB 4.4", "competence": "FPM"},
    "Contains the aircraft within the normal flight envelope": {"ob_code": "EY OB 4.8", "competence": "FPM"}
}

def similar(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def detect_ob(text: str) -> Optional[Dict[str, str]]:
    """
    Detect the OB code and competence for a given observation text.
    Returns None if no match is found.
    """
    return OB_MAPPING.get(text)

def calculate_how_many(observations: list, competence: str) -> int:
    """
    Calculate HOW MANY score for a given competence.
    Returns a score from 1 to 5, where:
    1 = <40% (Ineffective)
    2 = 40-59% (Minimum Acceptable)
    3 = 60-74% (Adequate)
    4 = 75-89% (Effective)
    5 = 90%+ (Exemplary)
    """
    relevant_obs = [obs for obs in observations if obs["competence"] == competence and obs["is_checked"]]
    total_obs = len([obs for obs in observations if obs["competence"] == competence])
    
    if total_obs == 0:
        return 1 # If no observations, it's the lowest score
    
    percentage = len(relevant_obs) / total_obs
    
    if percentage >= 0.9:
        return 5
    elif percentage >= 0.75:
        return 4
    elif percentage >= 0.6:
        return 3
    elif percentage >= 0.4:
        return 2
    else:
        return 1

def calculate_how_often(observations: list, competence: str) -> int:
    """
    Calculate HOW OFTEN score for a given competence.
    Returns a score from 1 to 5, where:
    1 = <40% (Ineffective)
    2 = 40-59% (Minimum Acceptable)
    3 = 60-74% (Adequate)
    4 = 75-89% (Effective)
    5 = 90%+ (Exemplary)
    """
    relevant_obs = [obs for obs in observations if obs["competence"] == competence and obs["is_checked"]]
    total_obs = len([obs for obs in observations if obs["competence"] == competence])
    
    if total_obs == 0:
        return 1 # If no observations, it's the lowest score
    
    percentage = len(relevant_obs) / total_obs
    
    if percentage >= 0.9:
        return 5
    elif percentage >= 0.75:
        return 4
    elif percentage >= 0.6:
        return 3
    elif percentage >= 0.4:
        return 2
    else:
        return 1

def calculate_final_grade(how_many: int, how_often: int) -> int:
    """
    Calculate final grade for a competence (worst of HOW MANY and HOW OFTEN)
    """
    return min(how_many, how_often) 