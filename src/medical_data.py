import json
import os
import logging
from src.api.config import TRIAGE_PATH, GUIDELINES_PATH

logger = logging.getLogger(__name__)

def load_medical_data():
    """
    Load and process medical data from various sources including:
    1. Original triage data from TRIAGE_PATH
    2. Original guidelines data from GUIDELINES_PATH
    3. Medical condition data from JSON files in the medical_data folder
    
    Returns:
        list: A list of formatted text strings for FAISS indexing
    """
    medical_texts = []
    
    # Process original triage and guidelines data
    medical_texts.extend(load_original_data())
    
    # Process medical condition data from JSON files
    medical_texts.extend(load_condition_json_files())
    
    logger.info(f"Loaded {len(medical_texts)} total medical texts for FAISS indexing")
    return medical_texts

def load_original_data():
    """
    Load and process the original triage and guidelines data.
    
    Returns:
        list: Formatted text strings from triage and guidelines data
    """
    texts = []
    
    try:
        # Load triage data
        with open(TRIAGE_PATH, 'r') as f:
            triage_data = json.load(f)
        
        # Load guidelines data
        with open(GUIDELINES_PATH, 'r') as f:
            guidelines_data = json.load(f)
        
        logger.info("Successfully loaded triage and guidelines data")
        
        # Process triage data
        for category in triage_data:
            for case in triage_data[category]:
                text = ""
                text += f"Source: DataTriage.json\n"
                text += f"Case category: {category}\n"
                text += f"Condition: {case['condition']}\n"
                text += f"Age Group: {case['age_group']}\n"
                text += f"Symptoms: {', '.join(case['symptoms'])}\n"
                text += f"ESI Level: {case['esi_level']}\n"
                texts.append(text)
        
        # Process guidelines data
        for category in guidelines_data:
            for case in guidelines_data[category]:
                text = ""
                text += f"Source: Guidelines.json\n"
                text += f"Case category: {category}\n"
                text += f"Condition: {case['condition']}\n"
                text += f"Age Group: {case['age_group']}\n"
                text += f"ESI Level: {case['esi_level']}\n"
                text += f"Immediate Actions: {', '.join(case['guidelines']['immediate_actions'])}\n"
                text += f"Disposition Criteria: {', '.join(case['guidelines']['disposition_criteria'])}\n"
                texts.append(text)
                
    except FileNotFoundError:
        logger.warning("Original triage/guidelines files not found. Continuing with other data sources.")
    except Exception as e:
        logger.error(f"Error loading original triage/guidelines data: {e}")
    
    return texts

def load_condition_json_files():
    """
    Load and process medical condition data from JSON files in the medical_data folder.
    Assumes all files have the same structure - a list of condition objects.
    
    Returns:
        list: A list of formatted text strings containing medical condition data
    """
    condition_texts = []
    
    # Get path to the medical_data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    medical_data_dir = os.path.join(project_root, "medical_data")
    
    logger.info(f"Looking for condition JSON files in: {medical_data_dir}")
    
    # Find all JSON files in the medical_data directory
    try:
        json_files = [
            os.path.join(medical_data_dir, filename)
            for filename in os.listdir(medical_data_dir)
            if filename.lower().endswith('.json')
        ]
        logger.info(f"Found {len(json_files)} JSON files in medical_data directory")
    except Exception as e:
        logger.warning(f"Error accessing medical_data directory: {e}")
        return condition_texts
    
    # Process each JSON file
    for json_file in sorted(json_files):
        filename = os.path.basename(json_file)
        try:
            # Load the JSON file as a list of condition objects
            with open(json_file, 'r') as f:
                conditions = json.load(f)
            
            if not isinstance(conditions, list):
                logger.warning(f"Expected list format in {filename}, but got {type(conditions).__name__}")
                continue
                
            logger.info(f"Processing {len(conditions)} conditions from {filename}")
            
            # Process each condition in the file
            for condition in conditions:
                condition_texts.append(format_condition(condition, filename))
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {filename}: {e}")
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
    
    logger.info(f"Processed {len(condition_texts)} total conditions from JSON files")
    return condition_texts

def format_condition(condition, source_file):
    """
    Format a condition object into a text string for FAISS indexing.
    
    Args:
        condition (dict): The condition object
        source_file (str): The filename where this condition was found
        
    Returns:
        str: Formatted text representation of the condition
    """
    # Start with condition name
    text = f"Condition: {condition['condition']}\n"
    
    # Add metadata
    text += f"Source: {source_file}\n"
    if 'last_scraped' in condition:
        text += f"Last Updated: {condition['last_scraped']}\n"
    
    # Process sections
    if 'sections' in condition and isinstance(condition['sections'], dict):
        section_order = [
            "Definition", "Alternative Names", "Causes", 
            "Symptoms", "Diagnosis", "Treatment"
        ]
        
        for section_name in section_order:
            if section_name in condition['sections']:
                section_content = condition['sections'][section_name]
                if isinstance(section_content, list):
                    text += f"{section_name}: {', '.join(section_content)}\n"
                else:
                    text += f"{section_name}: {section_content}\n"
    
    return text