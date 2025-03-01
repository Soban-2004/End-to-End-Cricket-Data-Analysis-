import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

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


players_data = []

for match_link in match_summary_links:
    # Fetch match details page
    match_response = requests.get(match_link)
    match_soup = BeautifulSoup(match_response.text, 'html.parser')

    # Get team names
    spans = match_soup.select('div.ds-bg-fill-canvas span.ds-text-tight-xs')
    # Print the text of each span
    team_1 = spans[0].text.replace("Innings", "").strip()
    team_2 = spans[1].text.replace("Innings", "").strip()
    # Extract player links from batting tables

    tables = match_soup.select('div > table.ci-scorecard-table')

    # Function to extract players from a table
    def extract_players(rows, team):
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 8:  # Ensure it is a player row
                player_link = cols[0].select_one('a')['href']
                player_name = cols[0].text.strip()
                full_player_link = "https://www.espncricinfo.com" + player_link
                players_data.append({"name": player_name, "team": team, "link": full_player_link})

    # Extract batting players
    first_inning_rows = tables[0].select('tbody > tr')
    second_inning_rows = tables[1].select('tbody > tr')

    extract_players(first_inning_rows, team_1)
    extract_players(second_inning_rows, team_2)

    # Extract bowling players from other tables
    bowling_tables = match_soup.select('div > table.ds-table')

    first_bowling_rows = bowling_tables[1].select('tbody > tr')
    second_bowling_rows = bowling_tables[3].select('tbody > tr')

    extract_players(first_bowling_rows, team_2)
    extract_players(second_bowling_rows, team_1)


# print(players_data[0]['link'])
final_data = []
# URL for Stage 1
for i in range(len(players_data)):
    if i % 10 == 0:
        print(f"{i} Players Completed.")
    player_link = players_data[i]['link']
    response = requests.get(player_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_desc = soup.select('div.ci-player-bio-content p')
    if all_desc and len(all_desc) > 1:
        description_text = all_desc[1].text.strip()  # Use the second paragraph
    else:
        description_text = ""


    def extract_info(label):
        element = soup.find('p', string=label)
        if element:
            return element.find_next('span').text.strip()
        return "N/A"


    batting_style = extract_info('Batting Style')
    bowling_style = extract_info('Bowling Style')
    playing_role = extract_info('Playing Role')

    final_data.append({
        "name": players_data[i]['name'],
        "description": description_text,
        "team": players_data[i]['team'],
        "battingStyle": batting_style,
        "bowlingStyle": bowling_style,
        "playingRole": playing_role
    })

print(json.dumps(final_data, indent=4))
with open('player_info.json', 'w') as file:
    json.dump(final_data, file, indent=4)
