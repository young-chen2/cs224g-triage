from ocr_pipeline import OCRPipeline
from guideline_interpreter import GuidelineInterpreter
import json
from pathlib import Path

def main():
    # Initialize the pipeline
    ocr = OCRPipeline()
    interpreter = GuidelineInterpreter()

    try:
        # Load existing JSON files
        with open('Guidelines.json', 'r') as f:
            guidelines_data = json.load(f)
        
        with open('DataTriage.json', 'r') as f:
            triage_data = json.load(f)

        # Process the medical guideline image
        result = ocr.extract_text('input_images/guideline.png')
        extracted_data = result['structured_data']
        
        # Update Guidelines.json
        for guideline in guidelines_data:
            if guideline['condition'].lower() in extracted_data['condition'].lower():
                # Update guideline fields
                guideline.update({
                    'age_group': extracted_data.get('age_group', guideline['age_group']),
                    'esi_level': extracted_data.get('esi_level', guideline['esi_level']),
                    'guidelines': {
                        'immediate_actions': extracted_data.get('immediate_actions', 
                                           guideline['guidelines']['immediate_actions']),
                        'definitive_management': extracted_data.get('definitive_management',
                                               guideline['guidelines']['definitive_management']),
                        'disposition_criteria': extracted_data.get('disposition_criteria',
                                             guideline['guidelines']['disposition_criteria']),
                        'recommended_poc': extracted_data.get('recommended_poc',
                                         guideline['guidelines']['recommended_poc'])
                    }
                })
                print(f"Updated guidelines for condition: {guideline['condition']}")
        
        # Update DataTriage.json
        for triage in triage_data:
            if triage['condition'].lower() in extracted_data['condition'].lower():
                # Update triage fields
                triage.update({
                    'age_group': extracted_data.get('age_group', triage['age_group']),
                    'symptoms': extracted_data.get('symptoms', triage['symptoms']),
                    'esi_level': extracted_data.get('esi_level', triage['esi_level'])
                })
                print(f"Updated triage data for condition: {triage['condition']}")
                
        # Save updated data
        with open('Guidelines.json', 'w') as f:
            json.dump(guidelines_data, f, indent=2)
            
        with open('DataTriage.json', 'w') as f:
            json.dump(triage_data, f, indent=2)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 