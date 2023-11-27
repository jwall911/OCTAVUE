from datetime import date
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup

url = 'http://ufcstats.com/statistics/events/completed?page=all'
response = uReq(url)
html_content = response.read()
response.close()

file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "CompletedEvents-data.csv"
file = open(file_name, 'w')
headers = 'EventID,Name,Date,Location\n'
file.write(headers)

soup = BeautifulSoup(html_content, 'html.parser')

# extract all event rows
upcoming_events = soup.find_all('tr',
                                class_='b-statistics__table-row')  # this expects that every event is within this type of row

for event in upcoming_events:
    # extract event name and ID
    event_a_tag = event.find('a', class_='b-link b-link_style_black')
    if event_a_tag:  # check if event tag exists
        current_event = event_a_tag.get('href')
        EventID = current_event.split('/')[-1]
        Name = event_a_tag.text.strip()

    # extract event date
    Date_tag = event.find('span', class_='b-statistics__date')
    if Date_tag:  # check if date tag exists
        Date = Date_tag.text.strip().replace(',', '')

    # extract event location
    Location_tag = event.find('td', class_='b-statistics__table-col b-statistics__table-col_style_big-top-padding')
    if Location_tag:  # check if location tag exists
        Location = Location_tag.text.strip().replace(',','')

        print(EventID, Name, Date, Location, sep=", ")
        file.write(EventID + ',' + Name + ',' + Date + ',' + Location + '\n')

file.close()


