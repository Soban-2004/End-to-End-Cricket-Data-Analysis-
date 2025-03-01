import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Step 1: URL to scrape
url = "https://www.espncricinfo.com/records/tournament/team-match-results/icc-men-s-t20-world-cup-2024-15946"

# Step 2: Send HTTP request to the URL
response = requests.get(url)

# Step 3: Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')


# Step 4: Initialize an empty list to store match data
match_summary = []

# Step 5: Locate the target table
table = soup.find('table', class_='ds-w-full ds-table ds-table-xs ds-table-auto ds-w-full ds-overflow-scroll '
                                  'ds-scrollbar-hide')
rows = table.find_all('tr')[1:]  # Select all rows with class 'data1'

# Step 6: Loop through each row and extract data
for row in rows:
    cols = row.find_all('td')  # Find all cells in the row

    match_summary.append({
        'team1': cols[0].text.strip(),
        'team2': cols[1].text.strip(),
        'winner': cols[2].text.strip(),
        'margin': cols[3].text.strip(),
        'ground': cols[4].text.strip(),
        'matchDate': cols[5].text.strip(),
        'scorecard': cols[6].text.strip()
    })

# Step 7: Convert the data into a DataFrame
df = pd.DataFrame(match_summary)

# Step 8: Save to CSV
df.to_csv('t20_2024_match_results.csv', index=False)
print("Scraping Complete! Data saved to 't20_worldcup_2024_matches.csv'.")
