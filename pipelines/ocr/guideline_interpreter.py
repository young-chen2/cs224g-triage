import re
import json
from typing import Dict, List, Any
from datetime import datetime
import logging

class GuidelineInterpreter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Load schema templates
        self.guidelines_schema = self._load_schema('schemas/Guidelines.json')
        self.triage_schema = self._load_schema('schemas/DataTriage.json')
        
        self.sections = {
            'condition': r'(?i)(condition|disease)[:|\s]*(.*)',
            'recommendation': r'(?i)recommendation[s]?[:|\s]*(.*)',
            'evidence_level': r'(?i)(evidence\s+level|grade|class)[\s:]+([A-D]|I{1,3}|[1-3])',
            'treatment': r'(?i)(treatment|therapy)[:|\s]*(.*)',
            'symptoms': r'(?i)(symptoms|clinical\s+presentation)[:|\s]*(.*)',
            'urgency': r'(?i)(urgency|priority|triage\s+level)[:|\s]*(.*)'
        }

    def process_text(self, text: str) -> Dict[str, Any]:
        """Process OCR text into both guidelines and triage formats"""
        basic_data = self._extract_structured_data(text)
        guideline_format = self._format_as_guideline(basic_data)
        triage_format = self._format_as_triage(basic_data)
        
        return {
            'guideline_data': guideline_format,
            'triage_data': triage_format,
            'raw_structured_data': basic_data
        }

    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from OCR text"""
        structured_data = {
            'title': self._extract_title(text),
            'sections': {},
            'metadata': {
                'confidence_score': self._calculate_confidence(text),
                'processing_date': datetime.now().isoformat(),
                'source_type': 'medical_guideline'
            }
        }

        for section_name, pattern in self.sections.items():
            matches = re.finditer(pattern, text, re.MULTILINE)
            section_content = []
            
            for match in matches:
                if len(match.groups()) > 0:
                    content = match.group(1).strip()
                    if content:
                        section_content.append(content)
            
            if section_content:
                structured_data['sections'][section_name] = section_content

        return structured_data

    def _format_as_guideline(self, data: Dict) -> Dict:
        """Format data according to guidelines.json schema"""
        return {
            "title": data['title'],
            "condition": data['sections'].get('condition', [""])[0],
            "recommendations": data['sections'].get('recommendation', []),
            "evidence_level": data['sections'].get('evidence_level', [""])[0],
            "treatment_options": data['sections'].get('treatment', []),
            "metadata": data['metadata']
        }

    def _format_as_triage(self, data: Dict) -> Dict:
        """Format data according to DataTriage.json schema"""
        urgency_mapping = {'high': 1, 'medium': 2, 'low': 3}
        urgency_text = data['sections'].get('urgency', ["medium"])[0].lower()
        urgency_level = urgency_mapping.get(urgency_text, 2)

        return {
            "condition": data['sections'].get('condition', [""])[0],
            "symptoms": data['sections'].get('symptoms', []),
            "urgency_level": urgency_level,
            "recommended_actions": data['sections'].get('recommendation', []),
            "treatment_path": data['sections'].get('treatment', []),
            "source_guideline": data['title'],
            "triage_timestamp": data['metadata']['processing_date']
        }

    def _extract_title(self, text: str) -> str:
        """Extract the title from the text"""
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                return line.strip()
        return "Untitled Guideline"

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score"""
        matched_sections = sum(1 for pattern in self.sections.values() 
                             if re.search(pattern, text, re.MULTILINE))
        return round(matched_sections / len(self.sections), 2) 