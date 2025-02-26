import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# URL of the webpage
url = "https://www.mayoclinic.org/diseases-conditions/index?letter=A"

# Send a GET request to the URL and check if successful
response = requests.get(url)

if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract conditions and links
    conditions_data = []

    for item in soup.find_all('li'):
        condition = item.text.strip()
        
        # Handle "See" references
        see_match = re.search(r'See (.*)', condition)
        if see_match:
            condition = see_match.group(1)
        
        # Extract hyperlink
        link = item.find('a')
        href = link['href'] if link else ''

        conditions_data.append((condition, href))

    # Create DataFrame and remove duplicates
    df = pd.DataFrame(conditions_data, columns=['Condition', 'Link']).drop_duplicates(subset=['Condition'])

    # Save to CSV
    file_name = "conditions_mayo_clinic.csv"
    df.to_csv(file_name, index=False, encoding="utf-8")

    print(f"Data successfully saved to {file_name}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
