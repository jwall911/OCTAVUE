from urllib.request import urlopen as uReq
from urllib.error import HTTPError
from bs4 import BeautifulSoup as soup
from datetime import date
import re

file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "fight-data-raw.csv"

my_url = 'http://ufcstats.com/statistics/events/completed?page=all'
headers = 'EventID,EventName,Fighter1ID,Fighter1Name,Fighter2ID,Fighter2Name,WinnerID\n'


def fightScrape(url, filename):
    file = open(filename, "w")
    file.write(headers)
    page_soup = soup(uReq(url).read(), 'html.parser')
    events = page_soup.findAll('a', attrs={'href': re.compile("^http://ufcstats.com/event-details")})

    for i in range(1, len(events)):
        current_event = events[i].get('href')
        try:
            event_page = uReq(current_event).read()
            event_soup = soup(event_page, 'html.parser')
        except HTTPError as e:
            e.read()
        event_id = current_event.split('/')[-1]
        event_name = event_soup.findAll('span', {'class': 'b-content__title-highlight'})[0].text.strip()

        fighters = event_soup.findAll('a', attrs={'href': re.compile("^http://ufcstats.com/fighter-details")})

        for i in range(0, len(fighters), 2):
            f1_id = fighters[i].get('href').split("/")[-1]
            f1_name = fighters[i].text.strip()
            f2_id = fighters[i + 1].get('href').split("/")[-1]
            f2_name = fighters[i + 1].text.strip()
            winner_id = f1_id

            file.write(event_id + ',' + event_name + ',' + f1_id + ',' + f1_name
                       + ',' + f2_id + ',' + f2_name + ',' + winner_id + '\n')
            print(f1_name + " vs. " + f2_name)

    file.close()


fightScrape(my_url, file_name)
