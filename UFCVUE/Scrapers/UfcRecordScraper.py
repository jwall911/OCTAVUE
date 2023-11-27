
from datetime import date
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup
import re

url = 'http://statleaders.ufc.com/en/fight'
response = uReq(url)
html_content=response.read()
response.close()

file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "ufcRecords-data.csv"
file = open(file_name, 'w')
headers = 'RecordType,RecordHolder,Record,Date,Event\n'
file.write(headers)

soup = BeautifulSoup(html_content, 'html.parser')


record_groups = soup.find_all('article', class_='results-group')

for record_group in record_groups:

    record_type_header = record_group.find('h3')
    record_type = record_type_header.text.strip() if record_type_header else 'Unknown Record'

    top_record = record_group.find('div', class_=re.compile('results-table--row-'))
    if not top_record:
        continue

    fighter_a_tag = top_record.find_all('a')[0]
    fighter_name = fighter_a_tag.text.strip()


    time_span = top_record.find_all('span')[-2]
    record_time = time_span.text.strip()

    date_event_span = top_record.find_all('span')[-1]
    date_event = date_event_span.text.strip()
    event_date, event_name = date_event.split('|', 1)
    event_date = event_date.strip()
    event_name = event_name.strip()
    print(record_type + ',' + fighter_name + ',' + record_time + ',' + event_date + ',' + event_name + '\n')
    file.write(record_type + ',' + fighter_name + ',' + record_time + ',' + event_date + ',' + event_name + '\n')
file.close()

