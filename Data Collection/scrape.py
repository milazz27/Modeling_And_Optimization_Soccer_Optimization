'''
This file will scrape data from online to build datasets for the project.
'''
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from pathlib import Path
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO

load_dotenv()

"""PROJECT PATHS"""
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = PROJECT_ROOT / "Data" / "raw" / "liga_primera.html"

"""LINKS FOR SCRAPING"""
# general league info (teams, stadiums, capacity, past rankings)
WIKI_LINK = "https://en.wikipedia.org/wiki/Liga_de_Primera"

"""GLOBALS"""
EMAIL = os.environ["WIKI_EMAIL"]
TEAM_DICT = dict()
SCRAPING_HEADER = {
    "User-Agent": (
        f"RPIScraper/1.0 "
        f"(https://github.com/milazz27/Modeling_And_Optimization_Soccer_Optimization; {EMAIL})"
    )
}
SESSION = None

# class to structure scraped data from the page for team basic info
class Team:
    stadium_coords = None
    def __init__(self, name, city, stadium, capacity):
        self.name = name
        self.city = city
        self.stadium = stadium
        self.capacity = capacity

    def add_coords(self, coords):
        self.stadium_coords = coords

def scrape_past_champions(table):
    """
    @brief: scrapes info on past champions and updates dictionary to add winning details
    @returns: None
    """
    print(table.columns)
    print(table.head())

    table = table.rename(columns={"Unnamed: 7_level_0": "drop_id"})
    mask = table.iloc[:, -1].isna()
    table = table.loc[mask].copy()

    for index, row in table.iterrows():
        print(index)
        print("Champion=",row["Champion (title count)"])
        print("Runner-Up=",row["Runner-up"])
        print("Year=",row["Season"])
        print("-----------------")



def scrape_team_info():
    """
    @brief: reads tables from the loaded html page and scrapes data for team information
    @effects: populates the TEAM_DICT
    @returns: None
    """
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        page = file.read()

    tables = pd.read_html(StringIO(page))
    team_table = tables[3]

    #print(f"Found {len(tables)} tables")

    #print(team_table.columns)
    #print(team_table.head())

    # handling populating the dict
    team_names = team_table["Team"].tolist()
    for team in team_names:
        lam_clean = lambda x: None if not x else x
        city = str(team_table.loc[team_table["Team"] == team, "City"].iloc[0])
        stadium = str(team_table.loc[team_table["Team"] == team, "Stadium"].iloc[0])
        capacity = int(team_table.loc[team_table["Team"] == team, "Capacity"].iloc[0])
        team_obj = Team(team, lam_clean(city), lam_clean(stadium), lam_clean(capacity))
        TEAM_DICT[team] = team_obj

    scrape_past_champions(tables[4])

def request_handler():
    """
    @brief: handles request for page for league wikipedia page
    @effects: saves page to HTML_FILE for caching
    @returns: None
    """
    try:
        page = SESSION.get(WIKI_LINK, timeout=30)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, "html.parser")
    except Exception as e:
        print("Error requesting file", WIKI_LINK)
        print(e)
        exit()

    with open(HTML_PATH, "w", encoding="utf-8") as file:
        file.write(page.text)

if __name__ == "__main__":
    # setting up the session with the headers for requesting page
    SESSION = requests.Session()
    SESSION.headers.update({    
        "User-Agent": (
        f"RPIScraper/1.0 "
        f"(https://github.com/milazz27/Modeling_And_Optimization_Soccer_Optimization; {EMAIL})"
    )})
    if HTML_PATH.exists():
        print("Cached File Exists")
    else:
        print("File does not exist, scraping now!")
        request_handler()

    # call scraping function
    scrape_team_info()