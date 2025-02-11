import schedule
import time
from datetime import datetime
import logging
import asyncio
from ...medical_guideline_scraper import GuidelineScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scraper():
    logger.info(f"Starting scheduled scraper run at {datetime.now()}")
    scraper = GuidelineScraper()
    asyncio.run(scraper.run())
    logger.info(f"Completed scraper run at {datetime.now()}")

def main():
    # Schedule to run every 3 months
    schedule.every(3).months.do(run_scraper)
    
    # Run immediately on startup
    run_scraper()
    
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour for pending tasks

if __name__ == "__main__":
    main() 