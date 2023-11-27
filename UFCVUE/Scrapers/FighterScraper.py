import datetime
from urllib.request import urlopen as uReq
from urllib.error import HTTPError
from bs4 import BeautifulSoup as soup
from datetime import date
import string
import re

file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "fighter-data-raw.csv"

my_url = 'http://ufcstats.com/statistics/fighters?char='


# calculate fighter momentum (based off current win/loss streak) - to be used with fight prediction

def momentum(record):
    confidence = 0.0
    streak = 0

    for i in record:
        if i == "win":
            streak += 1
            if streak > 2:
                confidence *= 1.2
                if confidence > 4:
                    confidence *= 1.4
            else:
                confidence += 1.0
        else:
            break

    if streak == 0 and record[0] == "loss":
        return -1.0
    return confidence


def fighter_scraper(url, filename):
    file = open(filename, "w")
    headers = 'FighterID,Name,Height,Weight,Reach,Age,SSPM,StrkACC,SSAbsPM,StrkDEF,TDAVG,TDACC,TDDEF,SUBAVG,Wins,Losses,WLDiff,Fire\n'
    file.write(headers)
    f_id = ''
    # scrape from page a-z
    for i in string.ascii_lowercase:
        new_url = url + i + '&page=all'
        print('Starting on ' + i + " at " + new_url)
        uClient = uReq(new_url)
        try:
            page_html = uClient.read()
            page_soup = soup(page_html, 'html.parser')
        except HTTPError as e:
            e.read()

        fighter_links = []

        for link in page_soup.findAll('a', attrs={'href': re.compile("^http://ufcstats.com/fighter-details")}):
            fighter_links.append(link.get('href'))

        # eliminate duplicate links
        fighter_links = set(fighter_links)
        print(len(fighter_links))

        for current_fighter in fighter_links:
            try:
                fighter_page = uReq(current_fighter).read()
                fighter_soup = soup(fighter_page, 'html.parser')
            except HTTPError as e:
                e.read()

            # variables
            f_id = current_fighter.split('/')[-1]
            name_elements = fighter_soup.findAll("span", {"class": "b-content__title-highlight"})
            if name_elements:
                name = name_elements[0].text.strip()
            else:
                # handle the case where the name is not found
                print(f"Name not found for URL: {current_fighter}")
                continue  # Skip to the next fighter
            print(name)

            stats = fighter_soup.findAll("li", {'class': 'b-list__box-list-item b-list__box-list-item_type_block'})
            Height = re.sub("[^0-9\'\"]", "", stats[0].text.strip())  # filter out unnecessary headings
            Weight = re.sub("[^0-9]", "", stats[1].text.strip())  # filter out
            Reach = re.sub("[^0-9\^.]", "", stats[2].text.strip())  # filter out
            DOB = stats[4].text.strip()[-4:]
            today = datetime.date.today()
            year = today.year
            if DOB == '  --':
                DOB = 0
            else: DOB = (year - int(DOB))
            # replace all the nonsense with emptiness
            SSPM = re.sub("[^0-9\^.]", "", stats[5].text.strip())
            StrkACC = re.sub("[^0-9]", "", stats[6].text.strip())
            SSAbsPM = re.sub("[^0-9\^.]", "", stats[7].text.strip())
            StrkDEF = re.sub("[^0-9]", "", stats[8].text.strip())
            TDAVG = re.sub("[^0-9\^.]", "", stats[10].text.strip())
            TDACC = re.sub("[^0-9]", "", stats[11].text.strip())
            TDDEF = re.sub("[^0-9]", "", stats[12].text.strip())
            SUBAVG = re.sub("[^0-9\^.]", "", stats[13].text.strip())
            TDAVG = TDAVG.lstrip('.')
            SUBAVG = SUBAVG.lstrip('.')
            StrkACC = int(StrkACC) / 100.0
            StrkDEF = int(StrkDEF) / 100.0
            TDACC = int(TDACC) / 100.0
            TDDEF = int(TDDEF) / 100.0
            record_list = []

            record = fighter_soup.findAll("i", {"class": "b-flag__text"})
            for i in record:
                record_list.append(i.text.strip())


            # get win-loss differential
            wins = record_list.count('win')
            losses = record_list.count('loss')
            WLDiff = wins - losses
            print(record)
            print(record_list)
            # eliminate null records
            if len(record) != 0:
                Fire = momentum(record_list)
            else:
                Fire = 0
            file.write(str(f_id) + "," + name + "," + Height + "," + Weight + "," + Reach + "," + str(DOB) + "," + SSPM + ","
                       + str(StrkACC) + "," + SSAbsPM + "," + str(StrkDEF) + "," + TDAVG + "," + str(TDACC) + "," + str(
                TDDEF) + "," + SUBAVG + "," + str(wins) +
                       "," + str(losses) + "," + str(WLDiff) + "," + str(Fire) + "\n")

    file.close()


fighter_scraper(my_url, file_name)
