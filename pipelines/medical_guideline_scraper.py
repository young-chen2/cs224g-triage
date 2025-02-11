import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import json
import re
from urllib.parse import urljoin
import requests
import PyPDF2
import io
import pandas as pd
from urllib.request import urlopen
import asyncio

class MedicalGuidelineScraper:
    async def search_pubmed(self, condition):
        try:
            # ... existing code ...
            if not results or 'esearchresult' not in results:
                self.logger.warning(f"No results found for {condition}")
                return []  # Return empty list instead of None
            
            pubmed_ids = results['esearchresult'].get('idlist', [])
            if not pubmed_ids:
                self.logger.warning(f"No PubMed IDs found for {condition}")
                return []  # Return empty list instead of None
            
            # ... rest of existing code ...
        except Exception as e:
            self.logger.error(f"Error searching PubMed for {condition}: {str(e)}")
            return []  # Return empty list on error

    async def run(self):
        try:
            all_guidelines = []
            for category, conditions in self.conditions.items():
                self.logger.info(f"Processing {category}...")
                for condition in conditions:
                    self.logger.info(f"Searching guidelines for: {condition}")
                    pubmed_guidelines = await self.search_pubmed(condition)
                    if pubmed_guidelines:  # Check if list is not empty
                        all_guidelines.extend(pubmed_guidelines)
                    await asyncio.sleep(1)  # Rate limiting
            
            return all_guidelines
        except Exception as e:
            self.logger.error(f"Error in run method: {str(e)}")
            return [] 
        
class MedicalGuidelineScraper:
    def __init__(self):
        self.setup_logging()
        self.setup_sources()
        self.guidelines_data = []
        self.pdf_data = []

    def setup_sources(self):
        """Initialize source URLs"""
        self.sources = {
            'penn_medicine': {
                'base_url': 'https://www.pennmedicine.org/for-patients-and-visitors/patient-information/conditions-treated-a-to-z',
                'type': 'conditions'
            },
            'pubmed': {
                'base_url': 'https://pubmed.ncbi.nlm.nih.gov',
                'type': 'guidelines'
            },
            'pmc': {
                'base_url': 'https://www.ncbi.nlm.nih.gov/pmc',
                'type': 'articles'
            },
            'clinical_compass': {
                'base_url': 'https://clinicalcompass.org',
                'type': 'guidelines'
            },
            'asahq': {
                'base_url': 'https://www.asahq.org',
                'type': 'guidelines'
            },
            'jospt': {
                'base_url': 'https://www.jospt.org',
                'type': 'guidelines'
            },
            'aafp': {
                'base_url': 'https://www.aafp.org',
                'type': 'guidelines'
            },
            'acpjournals': {
                'base_url': 'https://www.acpjournals.org',
                'type': 'guidelines'
            },
            'neurology': {
                'base_url': 'https://n.neurology.org',
                'type': 'guidelines'
            },
            'aaos': {
                'base_url': 'https://www.aaos.org',
                'type': 'guidelines'
            },
            'orthoguidelines': {
                'base_url': 'https://www.orthoguidelines.org',
                'type': 'guidelines'
            },
            'lww': {
                'base_url': 'https://journals.lww.com',
                'type': 'guidelines'
            },
            'aua': {
                'base_url': 'https://www.auanet.org',
                'type': 'guidelines'
            },
            'cdc': {
                'base_url': 'https://www.cdc.gov',
                'type': 'guidelines'
            },
            'wiley': {
                'base_url': 'https://acsjournals.onlinelibrary.wiley.com',
                'type': 'guidelines'
            },
            'aasm': {
                'base_url': 'https://aasm.org',
                'type': 'guidelines'
            },
            'nhlbi': {
                'base_url': 'https://www.nhlbi.nih.gov',
                'type': 'guidelines'
            },
            'jacionline': {
                'base_url': 'https://www.jacionline.org',
                'type': 'guidelines'
            },
            'sage': {
                'base_url': 'https://journals.sagepub.com',
                'type': 'guidelines'
            },
            'uspstf': {
                'base_url': 'https://www.uspreventiveservicestaskforce.org',
                'type': 'guidelines'
            },
            'ahajournals': {
                'base_url': 'https://www.ahajournals.org',
                'type': 'guidelines'
            }
        }
        
        # Define target conditions by category
        self.target_conditions = {
            'Trauma': [
                'Cervical Spine Fractures',
                'Cervical Spine Fractures in Children',
                'Cervical Spine Fractures in Older Adults',
                'Blunt Abdominal Trauma',
                'Acute Knee Injuries',
                'Acute Ankle and Foot Injuries',
                'Blunt Head Injury in Children',
                'Blunt Chest Trauma'
            ],
            'Cardiology': [
                'Heart Failure',
                'Syncope',
                'Acute Coronary Syndrome',
                'Palpitations'
            ],
            'Infectious Disease': [
                'Bacterial Meningitis in Children',
                'Sepsis',
                'Serious Bacterial Infections in Children',
                'Necrotizing Fasciitis',
                'Infective Endocarditis',
                'Pharyngitis',
                'Rhinosinusitis'
            ],
            'Surgical Abdominal': [
                'Acute Appendicitis',
                'Acute Abdominal Pain',
                'Small Bowel Obstruction',
                'Acute Pancreatitis',
                'Acute Cholecystitis',
                'Aortic Emergencies',
                'Ovarian Torsion'
            ],
            'Urology': [
                'Testicular Torsion',
                'Nephrolithiasis'
            ],
            'Neurology': [
                'Acute Stroke',
                'Subarachnoid Hemorrhage',
                'Transient Ischemic Attack',
                'Seizure',
                'Blunt Head Injury',
                'Occult Hip Fracture',
                'Blunt Soft Tissue Neck Trauma',
                'Occult Scaphoid Fractures'
            ],
            'Additional Trauma': [
                'Penetrating Abdominal Trauma',
                'Penetrating Trauma Extremities',
                'Vascular Injuries'
            ]
        }

    def setup_logging(self):
        """Configure logging"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/guideline_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def fetch_page(self, session, url):
        """Fetch page content with error handling"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                self.logger.error(f"Error fetching {url}: Status {response.status}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    async def process_penn_medicine(self, session):
        """Process Penn Medicine conditions"""
        content = await self.fetch_page(session, self.sources['penn_medicine']['base_url'])
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        conditions = []
        
        for condition in soup.find_all('a', class_='condition-link'):
            try:
                conditions.append({
                    'name': condition.text.strip(),
                    'url': urljoin(self.sources['penn_medicine']['base_url'], condition['href']),
                    'source': 'Penn Medicine',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error processing condition: {str(e)}")

        return conditions

    async def search_pubmed_guidelines(self, session, condition, category):
        """Search PubMed for guidelines with category"""
        base_url = f"{self.sources['pubmed']['base_url']}/search"
        search_term = f'"{condition}"[Title/Abstract] AND "guideline"[Publication Type]'
        params = {
            'term': search_term,
            'sort': 'date'
        }
        
        try:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    results = []
                    
                    for article in soup.find_all('article', class_='full-docsum'):
                        try:
                            title = article.find('a', class_='docsum-title')
                            authors = article.find('span', class_='docsum-authors')
                            date = article.find('span', class_='docsum-journal-citation')
                            
                            results.append({
                                'title': title.text.strip() if title else 'No title',
                                'authors': authors.text.strip() if authors else 'No authors',
                                'date': date.text.strip() if date else 'No date',
                                'url': urljoin(self.sources['pubmed']['base_url'], 
                                            title['href']) if title else None,
                                'source': 'PubMed',
                                'category': category,
                                'condition': condition,
                                'timestamp': datetime.now().isoformat()
                            })
                        except Exception as e:
                            self.logger.error(f"Error processing PubMed result: {str(e)}")
                    
                    return results
                    
        except Exception as e:
            self.logger.error(f"Error searching PubMed: {str(e)}")
            return []

    async def process_pmc_article(self, session, pmcid):
        """Process a specific PMC article"""
        url = f"{self.sources['pmc']['base_url']}/articles/{pmcid}/"
        content = await self.fetch_page(session, url)
        if not content:
            return None

        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract article title
            title = soup.find('h1', {'class': 'content-title'})
            title_text = title.text.strip() if title else "No title available"
            
            # Extract authors
            authors = soup.find_all('a', {'class': 'contrib-author'})
            author_list = [author.text.strip() for author in authors] if authors else []
            
            # Extract abstract
            abstract = soup.find('div', {'class': 'abstract'})
            abstract_text = abstract.text.strip() if abstract else ""
            
            # Extract recommendations sections
            recommendations = []
            for section in soup.find_all(['h2', 'h3', 'h4']):
                if 'recommendation' in section.text.lower():
                    content = []
                    for sibling in section.find_next_siblings():
                        if sibling.name in ['h2', 'h3', 'h4']:
                            break
                        content.append(sibling.text.strip())
                    recommendations.append({
                        'heading': section.text.strip(),
                        'content': ' '.join(content)
                    })

            article_data = {
                'title': title_text,
                'authors': author_list,
                'abstract': abstract_text,
                'recommendations': recommendations,
                'url': url,
                'source': 'PMC',
                'pmcid': pmcid,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed PMC article {pmcid}")
            return article_data

        except Exception as e:
            self.logger.error(f"Error processing PMC article {pmcid}: {str(e)}")
            return None

    async def save_guidelines(self, guidelines):
        """Save extracted guidelines to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'guidelines_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(guidelines, f, indent=2)
            self.logger.info(f"Guidelines saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving guidelines: {str(e)}")

    async def search_additional_sources(self, session, condition, category):
        """Search additional guideline sources"""
        guidelines = []
        
        for source_name, source_info in self.sources.items():
            if source_name not in ['pubmed', 'pmc']:  # Skip already handled sources
                try:
                    search_url = f"{source_info['base_url']}/search"
                    params = {
                        'q': condition,
                        'type': 'guideline'
                    }
                    
                    async with session.get(search_url, params=params) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract results (implementation will vary by source)
                            results = self.extract_guidelines(soup, source_name)
                            
                            for result in results:
                                guidelines.append({
                                    'title': result.get('title'),
                                    'url': result.get('url'),
                                    'source': source_name,
                                    'category': category,
                                    'condition': condition,
                                    'timestamp': datetime.now().isoformat()
                                })
                
                    # Add delay between requests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error searching {source_name}: {str(e)}")
                    continue
        
        return guidelines

    async def process_pdf_url(self, url):
        """Process PDF from URL and extract structured information"""
        try:
            # Download PDF
            response = urlopen(url)
            pdf_content = io.BytesIO(response.read())
            
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(pdf_content)
            text_content = ""
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            
            # Extract structured information using regex patterns
            structured_data = self.extract_structured_data(text_content)
            
            return structured_data
            
        except Exception as e:
            self.logger.error(f"Error processing PDF from {url}: {str(e)}")
            return None
    
    def extract_structured_data(self, text):
        """Extract structured data from text content"""
        data = {
            'symptoms': [],
            'immediate_actions': [],
            'definitive_management': [],
            'disposition_criteria': []
        }
        
        # Define regex patterns for each section
        patterns = {
            'symptoms': r'(?:symptoms?|clinical presentation|signs)[:]\s*(.*?)(?=\n\n|\Z)',
            'immediate_actions': r'(?:immediate actions?|initial management|emergency measures)[:]\s*(.*?)(?=\n\n|\Z)',
            'definitive_management': r'(?:definitive management|treatment plan|management strategy)[:]\s*(.*?)(?=\n\n|\Z)',
            'disposition_criteria': r'(?:disposition|discharge criteria|admission criteria)[:]\s*(.*?)(?=\n\n|\Z)'
        }
        
        # Extract data using patterns
        for key, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                if match.group(1):
                    data[key].append(match.group(1).strip())
        
        return data

    async def export_to_excel(self, guidelines):
        """Export guidelines data to Excel"""
        excel_data = []
        
        for guideline in guidelines:
            # Process PDF if URL ends with .pdf
            pdf_data = None
            if guideline['url'] and guideline['url'].lower().endswith('.pdf'):
                pdf_data = await self.process_pdf_url(guideline['url'])
            
            row = {
                'Condition': guideline.get('condition', ''),
                'Category': guideline.get('category', ''),
                'Source': guideline.get('source', ''),
                'URL': guideline.get('url', ''),
                'Symptoms': '; '.join(pdf_data['symptoms']) if pdf_data else '',
                'Immediate Actions': '; '.join(pdf_data['immediate_actions']) if pdf_data else '',
                'Definitive Management': '; '.join(pdf_data['definitive_management']) if pdf_data else '',
                'Disposition Criteria': '; '.join(pdf_data['disposition_criteria']) if pdf_data else ''
            }
            excel_data.append(row)
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(excel_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_filename = f'medical_guidelines_{timestamp}.xlsx'
        
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        self.logger.info(f"Guidelines exported to Excel: {excel_filename}")

    async def process_source_url(self, session, url, condition, category):
        """Process source URL and extract data"""
        try:
            if url.lower().endswith('.pdf'):
                # Handle PDF
                pdf_data = await self.process_pdf_url(url)
                if pdf_data:
                    return {
                        'url': url,
                        'condition': condition,
                        'category': category,
                        **pdf_data
                    }
            else:
                # Handle HTML
                content = await self.fetch_page(session, url)
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    text_content = soup.get_text()
                    structured_data = self.extract_structured_data(text_content)
                    return {
                        'url': url,
                        'condition': condition,
                        'category': category,
                        **structured_data
                    }
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {str(e)}")
        return None

    async def run(self):
        """Main execution method"""
        async with aiohttp.ClientSession() as session:
            all_guidelines = []
            
            # Process each condition by category
            for category, conditions in self.target_conditions.items():
                self.logger.info(f"Processing {category} conditions...")
                for condition in conditions:
                    self.logger.info(f"Searching guidelines for: {condition}")
                    
                    # Search PubMed
                    pubmed_guidelines = await self.search_pubmed_guidelines(session, condition, category)
                    all_guidelines.extend(pubmed_guidelines)
                    
                    # Search additional sources
                    additional_guidelines = await self.search_additional_sources(session, condition, category)
                    all_guidelines.extend(additional_guidelines)
                    
                    # Process each guideline URL
                    for guideline in all_guidelines:
                        if guideline.get('url'):
                            processed_data = await self.process_source_url(
                                session, 
                                guideline['url'], 
                                guideline['condition'], 
                                guideline['category']
                            )
                            if processed_data:
                                guideline.update(processed_data)
                    
                    # Add delay to avoid overwhelming servers
                    await asyncio.sleep(2)
            
            # Save results to JSON
            await self.save_guidelines(all_guidelines)
            
            # Export to Excel
            await self.export_to_excel(all_guidelines)

async def main():
    scraper = MedicalGuidelineScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main()) 