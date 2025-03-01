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


def fetch_match_details(url):
    # 2.a Interaction Code (Navigating to the match summary page)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 2.b Parser Code (Extracting match details)
    spans = soup.select('div.ds-bg-fill-canvas span.ds-text-tight-xs')
    # Print the text of each span
    team_1 = spans[0].text.replace("Innings", "").strip()
    team_2 = spans[1].text.replace("Innings", "").strip()
    match_info = f"{team_1} vs {team_2}"

    # Extract innings details (bowling summary)
    tables = soup.select('div > table.ds-table')
    first_innings_rows = tables[1].find_all('tr')
    second_innings_rows = tables[3].find_all('tr')
    bowling_summary = []

    def parse_bowling_rows(rows, bowling_team):
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 11:
                bowler_name = tds[0].find('a').text.strip()
                overs = tds[1].text.strip()
                maiden = tds[2].text.strip()
                runs = tds[3].text.strip()
                wickets = tds[4].text.strip()
                economy = tds[5].text.strip()
                zeroes = tds[6].text.strip()
                fours = tds[7].text.strip()
                sixes = tds[8].text.strip()
                wides = tds[9].text.strip()
                no_balls = tds[10].text.strip()

                bowling_summary.append({
                    "match": match_info,
                    "bowlingTeam": bowling_team,
                    "bowlerName": bowler_name,
                    "overs": overs,
                    "maiden": maiden,
                    "runs": runs,
                    "wickets": wickets,
                    "economy": economy,
                    "0s": zeroes,
                    "4s": fours,
                    "6s": sixes,
                    "wides": wides,
                    "noBalls": no_balls
                })

    # Parse first innings
    parse_bowling_rows(first_innings_rows, team_2)

    # Parse second innings
    parse_bowling_rows(second_innings_rows, team_1)

    return bowling_summary


all_bowling_summary =[]
for match_url in match_summary_links:
    match_details = fetch_match_details(match_url)
    all_bowling_summary.extend(match_details)
# Print the resulting batting summary
print(json.dumps(all_bowling_summary,indent=4))

df = pd.DataFrame(all_bowling_summary)

# Step 8: Save to CSV
df.to_csv('t20_2024_bowling_results.csv', index=False)
print("Scraping Complete! Data saved to 't20_worldcup_2024_matches.csv'.")
