import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# URL for Stage 1
url = "https://www.espncricinfo.com/records/tournament/team-match-results/icc-men-s-t20-world-cup-2024-15946"

# Send a request to fetch the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')


# Find all match links (links for match summaries)
match_summary_links = []
table = soup.find('table', class_='ds-w-full ds-table ds-table-xs ds-table-auto ds-w-full ds-overflow-scroll '
                                  'ds-scrollbar-hide')
rows = table.find_all('tr')[1:]

for row in rows:
    tds = row.find_all('td')
    row_url = "https://www.espncricinfo.com" + tds[6].find('a')['href']
    match_summary_links.append(row_url)
match_summary_links.pop(46)



# Function to fetch individual match details
def fetch_match_details(url):

    # Step 2: Send an HTTP GET request
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    spans = soup.select('div.ds-bg-fill-canvas span.ds-text-tight-xs')
    # Print the text of each span
    team_1 = spans[0].text.replace("Innings", "").strip()
    team_2 = spans[1].text.replace("Innings", "").strip()
    match_info = f"{team_1} vs {team_2}"

    table = soup.select('table.ci-scorecard-table')
    innings_1 = table[0].select('tbody tr')
    innings_2 = table[1].select('tbody tr')
    batting_summary = []

    def parse_innings_rows(innings_rows, team):
        for index, row_2 in enumerate(innings_rows):
            tds = row_2.find_all('td')
            if len(tds) >= 8:
                batsman_name = tds[0].find('a').get_text(strip=True)
                dismissal = tds[1].get_text(strip=True)
                runs = tds[2].find('strong').get_text(strip=True)
                balls = tds[3].get_text(strip=True)
                fours = tds[5].get_text(strip=True)
                sixes = tds[6].get_text(strip=True)
                strike_rate = tds[7].get_text(strip=True)

                batting_summary.append({
                    "match": match_info,
                    "teamInnings": team,
                    "battingPos": index + 1,
                    "batsmanName": batsman_name,
                    "dismissal": dismissal,
                    "runs": runs,
                    "balls": balls,
                    "4s": fours,
                    "6s": sixes,
                    "SR": strike_rate
                })

    # Parse both innings
    parse_innings_rows(innings_1, team_1)
    parse_innings_rows(innings_2, team_2)

    return batting_summary


# Fetch details for all the matches
all_batting_summary =[]
for match_url in match_summary_links:
    match_details = fetch_match_details(match_url)
    all_batting_summary.extend(match_details)
# Print the resulting batting summary
print(json.dumps(all_batting_summary,indent=4))

df = pd.DataFrame(all_batting_summary)

# Step 8: Save to CSV
df.to_csv('t20_2024_batting_results.csv', index=False)
print("Scraping Complete! Data saved to 't20_worldcup_2024_matches.csv'.")
