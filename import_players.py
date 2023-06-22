#this code piece gatehrs the players from the 2012 Global Starcraft 2 League

import requests
from bs4 import BeautifulSoup
import pycountry
import config
import pandas as pd
# URL of the Liquipedia page for the 2012 GSL Code S

url = input("Enter liquipedia url: ")

# Send a GET request to the URL
response = requests.get(url)

# Use BeautifulSoup to parse the HTML content of the response
soup = BeautifulSoup(response.content, "html.parser")

# Find the table of players
table = soup.find("table", {"class": "wikitable"})

# Loop through the rows of the table and extract the names of the players
players =[]
try:
    for row in table.find_all("tr")[1:]: # Skip the header row
        cells = row.find_all("td")
        if len (cells) >= 2:
            for column in range(3):
                if len(cells[column].get_text().strip()) > 0:
                    player = cells[column].get_text().strip()
                    images = cells[column].find_all('img')
                    try:
                        country = images[2]['alt']
                        country = pycountry.countries.search_fuzzy(country)[0]
                        country = country.alpha_2
                    except:
                        pass
                    if column == 0:
                        chara = "P"
                    elif column == 1:
                        chara = "T"
                    else:
                        chara = "Z"
                    players.append(player + " " + country + " " + chara)
except:
    pass

# Print the list of players
players = [player for player in players if player]

player_ids = []
player_names = []
for player in players:
    player = player.replace("*", "")
    url = f"http://aligulac.com/search/json/?q={player}"
    response = requests.get(f"{url}")
    data = response.json()
    player_ids.append(data["players"][0]["id"])
    player_names.append(player.split()[0])

if player_ids:
    pass
else:
    soupdiv = soup.find_all("div", {"class": "participant-table-entry opponent-list-cell brkts-opponent-hover"})

    players = []
    race = 1
    for soupname in soupdiv:
        singleplayerlist = soupname.find("div", {"class": "block-player starcraft-block-player"})
        span_elements = singleplayerlist.find_all("span")
        for i in range(0, len(span_elements), 2):
            player_name = span_elements[i+1].find('a').get_text()
            country = span_elements[i].find('img').get('alt')
            try:
                country = pycountry.countries.search_fuzzy(country)[0]
                country = country.alpha_2
            except:
                pass

            if race % 3 == 1:
                chara = "P"
            elif race % 3 == 2:
                chara = "T"
            else:
                chara = "Z"
            race += 1

            players.append(player_name + " " + country + " " + chara)
    
    player_ids = []
    player_names = []
    for player in players:
        player = player.replace("*", "")
        url = f"http://aligulac.com/search/json/?q={player}"
        response = requests.get(f"{url}")
        data = response.json()
        try:
            player_ids.append(data["players"][0]["id"])
            player_names.append(player.split()[0])
        except:
            player = player.split()[0] + " " + player.split()[1]
            url = f"http://aligulac.com/search/json/?q={player}"
            response = requests.get(f"{url}")
            data = response.json()
            player_ids.append(data["players"][0]["id"])
            player_names.append(player.split()[0])



zipped = list(zip(player_ids, player_names))
players_df = pd.DataFrame(zipped, columns = ['IDs','Names'])

# Set up the API endpoint and your API key
api_key = config.API_KEY
searchablestring = ";".join([str(player_id) for player_id in player_ids])


api_url = f"http://aligulac.com/api/v1/player/set/{searchablestring}/?apikey={api_key}"


# Set up the headers to include your API key
headers = {
    "Authorization": f"Bearer {api_key}"
}


# Make a request to the API endpoint
response = requests.get(f"{api_url}")

data = response.json()

try:
    ratings = []
    deviation = []
    for id in range(len(data["objects"])):
        ratings.append(data["objects"][id]["current_rating"]["rating"])
        deviation.append(data["objects"][id]["current_rating"]["dev"])

    players_df["ratings"] = ratings
    players_df['deviation'] = deviation

    players_df = players_df.sort_values(by = "ratings", ascending=False)
    players_df.loc[:, "Pre-Rank"] = players_df['ratings'].rank(ascending=False, method="dense")
    file_name = input("Enter file name: ")
    players_df.to_csv(f"Data\{file_name}.csv")
except:
    print("The API doesn't seem to like us very much today. It gave an error. Try again later")