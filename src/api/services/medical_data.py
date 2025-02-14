import json
from ..config import TRIAGE_PATH, GUIDELINES_PATH

def load_medical_data():
    """Load and process medical data from JSON files."""
    with open(TRIAGE_PATH, 'r') as f:
        triage_data = json.load(f)
    
    with open(GUIDELINES_PATH, 'r') as f:
        guidelines_data = json.load(f)
    
    medical_texts = []
    
    # Process triage data
    for category in triage_data:
        for case in triage_data[category]:
            text = ""
            text += f"Case category: {category}\n"
            text = f"Condition: {case['condition']}\n"
            text += f"Age Group: {case['age_group']}\n"
            text += f"Symptoms: {', '.join(case['symptoms'])}\n"
            text += f"ESI Level: {case['esi_level']}\n"
            medical_texts.append(text)
    
    # Process guidelines data
    for category in guidelines_data:
        for case in guidelines_data[category]:
            text = ""
            text += f"Case category: {category}\n"
            text = f"Condition: {case['condition']}\n"
            text += f"Age Group: {case['age_group']}\n"
            text += f"ESI Level: {case['esi_level']}\n"
            text += f"Immediate Actions: {', '.join(case['guidelines']['immediate_actions'])}\n"
            text += f"Disposition Criteria: {', '.join(case['guidelines']['disposition_criteria'])}\n"
            medical_texts.append(text)
    
    return medical_texts