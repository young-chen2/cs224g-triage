import os
import json
import time
import requests
from bs4 import BeautifulSoup
from utils import sanitize_filename, create_directory

class PennMedicineScraper:
    def __init__(self):
        self.base_url = "https://www.pennmedicine.org/for-patients-and-visitors/patient-information/conditions-treated-a-to-z"
        self.output_dir = "data/conditions"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Predefined list of conditions by category
        self.conditions = {
            "Trauma Cases": [
                "Achilles Tendonitis",
                "Anterior Cruciate Ligament Injury",
                "Anterior Knee Pain",
                "Bone Fracture",
                "Broken Nose",
                "Burn Injury",
                "Concussion",
                "Crush Injuries",
                "Facial Trauma",
                "Joint Dislocation",
                "Knee MCL Injury",
                "Kneecap Dislocation",
                "Shin Splints",
                "Spinal Cord Injury",
                "Sprains",
                "Strains",
                "Tennis Elbow",
                "Ulnar Collateral Ligament Injury",
                "Volkmann's Ischemic Contracture",
                "Wrist Pain"
            ],
            "Cardiology Cases": [
                "Aneurysms",
                "Aortic Coarctation",
                "Aortic Dissection",
                "Aortic Ulcer",
                "Aortic Valve Regurgitation",
                "Aortic Valve Stenosis",
                "Arrhythmia",
                "Arrhythmogenic Cardiomyopathy",
                "Arterial Embolism",
                "Arterial Insufficiency",
                "Arteriovenous Malformations",
                "Atherosclerosis",
                "Atrial Fibrillation",
                "Atrial Septal Defect",
                "Bicuspid Aortic Valve Disease",
                "Cardiac Amyloidosis",
                "Cardiac Tamponade",
                "Cardiogenic Shock",
                "Cardiomyopathy",
                "Coronary Artery Disease",
                "Coronary Artery Spasm",
                "Cyanotic Heart Disease",
                "Dilated Cardiomyopathy",
                "Heart Attack",
                "Heart Block",
                "Heart Disease in Women",
                "Heart Failure",
                "Hypertension",
                "Hypertensive Heart Disease",
                "Hypertrophic Cardiomyopathy",
                "Long QT Syndrome",
                "Low Blood Pressure",
                "Mitral Stenosis",
                "Mitral Valve Prolapse",
                "Mitral Valve Regurgitation",
                "Myocarditis",
                "Patent Foramen Ovale",
                "Peripartum Cardiomyopathy",
                "Peripheral Artery Disease",
                "Pulmonary Embolism",
                "Pulmonary Hypertension",
                "Pulmonary Valve Stenosis",
                "Pulmonary Veno-Occlusive Disease",
                "Restrictive Cardiomyopathy",
                "Stroke",
                "Supraventricular Tachycardia",
                "Tricuspid Valve Regurgitation",
                "Ventricular Septal Defect",
                "Ventricular Tachycardia",
                "Wolff-Parkinson-White Syndrome"
            ],
            "Infectious Disease Cases": [
                "Acute Kidney Injury",
                "Aspergillosis",
                "Blastomycosis",
                "Cellulitis",
                "Chickenpox",
                "Cholera",
                "Coronavirus",
                "Diphtheria",
                "Ear Infection",
                "Empyema",
                "Endocarditis",
                "Epididymitis",
                "Hepatitis A",
                "Hepatitis B",
                "Hepatitis C",
                "HIV",
                "Influenza",
                "Lyme Disease",
                "Malaria",
                "Meningitis",
                "Mpox",
                "MRSA",
                "Pneumonia",
                "Sepsis",
                "Shingles",
                "Syphilis",
                "Tuberculosis",
                "Typhoid Fever",
                "Urinary Tract Infection",
                "West Nile Virus",
                "Yellow Fever"
            ],
            "Surgical Abdominal Cases": [
                "Abdominal Aortic Aneurysm",
                "Acute Appendicitis",
                "Ascites",
                "Bile Duct Cancer",
                "Colon Cancer",
                "Colon Polyps",
                "Diaphragmatic Hernia",
                "Diverticulitis",
                "Gallbladder Cancer",
                "Gallstones",
                "Herniated Disc",
                "Hiatal Hernia",
                "Liver Cancer",
                "Liver Cirrhosis",
                "Liver Disease",
                "Pancreatic Cancer",
                "Pancreatic Neuroendocrine Tumors",
                "Pancreatitis",
                "Peptic Ulcer Disease",
                "Primary Biliary Cirrhosis",
                "Stomach Cancer",
                "Ulcerative Colitis"
            ],
            "Urology Cases": [
                "Bladder Cancer",
                "Bladder Stones",
                "Blood in Urine",
                "End-Stage Kidney Disease",
                "Kidney Cancer",
                "Kidney Stones",
                "Nephrotic Syndrome",
                "Peyronie's Disease",
                "Protein-Losing Enteropathy",
                "Urge Incontinence",
                "Urinary Incontinence",
                "Urethral Cancer",
                "Urethritis"
            ],
            "Neurology Cases": [
                "Acoustic Neuroma",
                "Alzheimer's Disease",
                "Amyotrophic Lateral Sclerosis",
                "Aneurysm",
                "Ataxia",
                "Brain Metastasis",
                "Brain Tumor",
                "Cerebral Palsy",
                "Chronic Inflammatory Demyelinating Polyneuropathy",
                "Cranial Base Disorders",
                "Dementia",
                "Dementia with Lewy Bodies",
                "Epilepsy",
                "Guillain-Barré Syndrome",
                "Huntington's Disease",
                "Hydrocephalus",
                "Idiopathic Intracranial Hypertension",
                "Memory Loss",
                "Meniere's Disease",
                "Multiple Sclerosis",
                "Multiple System Atrophy",
                "Narcolepsy",
                "Neuromyelitis Optica",
                "Neuropathy",
                "Parkinson's Disease",
                "Pick's Disease",
                "Progressive Supranuclear Palsy",
                "Spinal Cord Diseases",
                "Spinal Muscular Atrophy",
                "Trigeminal Neuralgia"
            ]
        }

    def clean_condition_name(self, name):
        """Remove parentheses and clean the condition name"""
        cleaned = name.split('(')[0].strip()
        return cleaned.lower().replace(' ', '-')

    def scrape_condition_content(self, condition_name):
        """Scrape the text content for a condition"""
        try:
            formatted_name = self.clean_condition_name(condition_name)
            url = f"https://www.pennmedicine.org/for-patients-and-visitors/patient-information/conditions-treated-a-to-z/{formatted_name}"
            
            print(f"Scraping: {condition_name}")
            print(f"URL: {url}")
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the main content area
                main_content = soup.find('main', class_='content-primary')
                if main_content:
                    # Get all text content, excluding References and Version Info
                    content = []
                    
                    # Get the title
                    title = main_content.find('h1')
                    if title:
                        content.append(title.get_text(strip=True))
                        content.append("-" * 80)  # Separator
                    
                    # Get all paragraphs and lists
                    for element in main_content.find_all(['p', 'ul', 'h2']):
                        if element.name == 'h2':
                            section_title = element.get_text(strip=True)
                            if section_title not in ["References", "Version Info"]:
                                content.append("\n" + section_title.upper() + "\n")
                        elif element.name == 'p':
                            text = element.get_text(strip=True)
                            if text:
                                content.append(text)
                        elif element.name == 'ul':
                            for li in element.find_all('li'):
                                text = li.get_text(strip=True)
                                if text:
                                    content.append(f"• {text}")
                    
                    if content:
                        # Save as text file
                        filename = sanitize_filename(condition_name) + ".txt"
                        filepath = os.path.join(self.output_dir, filename)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write('\n\n'.join(content))
                        
                        print(f"Saved text content for: {condition_name}")
                        return True
                    else:
                        print("No content found")
                else:
                    print("Could not find main content area")
            else:
                print(f"Failed to access {condition_name}: Status code {response.status_code}")
            return False
            
        except Exception as e:
            print(f"Error scraping {condition_name}: {str(e)}")
            return False

    def scrape_all_conditions(self):
        """Scrape content for all conditions"""
        create_directory(self.output_dir)
        
        total_conditions = sum(len(conditions) for conditions in self.conditions.values())
        processed = 0
        
        for category, conditions in self.conditions.items():
            print(f"\nProcessing {category}...")
            
            for condition in conditions:
                processed += 1
                print(f"\nProgress: {processed}/{total_conditions}")
                
                success = self.scrape_condition_content(condition)
                if success:
                    time.sleep(2)  # Be polite to the server

def scrape_aaa_content():
    """Scrape the text content for Abdominal Aortic Aneurysm"""
    url = "https://www.pennmedicine.org/for-patients-and-visitors/patient-information/conditions-treated-a-to-z/abdominal-aortic-aneurysm"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping AAA content...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = []
            
            # Get the title
            title = soup.find('span', class_='h1-main__title')
            if title:
                content.append(title.get_text(strip=True))
                content.append("-" * 80)
            
            # Find the main content div
            content_div = soup.find('div', class_='rtf u-cf mb-2')
            if content_div:
                # Get all paragraphs and lists
                for element in content_div.find_all(['p', 'ul', 'h2', 'h3']):
                    if element.name in ['h2', 'h3']:
                        section_title = element.get_text(strip=True)
                        if section_title not in ["References", "Version Info"]:
                            content.append("\n" + section_title.upper() + "\n")
                    elif element.name == 'p':
                        text = element.get_text(strip=True)
                        if text:
                            content.append(text)
                    elif element.name == 'ul':
                        for li in element.find_all('li'):
                            text = li.get_text(strip=True)
                            if text:
                                content.append(f"• {text}")
                
                if content:
                    # Save as text file
                    with open('aaa_content.txt', 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(content))
                    print("Content saved to aaa_content.txt")
                else:
                    print("No content found")
            else:
                print("Could not find content div")
        else:
            print(f"Failed to access URL: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    scraper = PennMedicineScraper()
    
    # Test with one condition first
    test_conditions = [
        "Achilles Tendonitis"
    ]
    
    print("Testing scraper with sample conditions...")
    for condition in test_conditions:
        print(f"\nTesting: {condition}")
        success = scraper.scrape_condition_content(condition)
        if success:
            time.sleep(8)  # Be polite to the server

    scrape_aaa_content()