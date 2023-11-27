import datetime
from datetime import date
import subprocess
import webbrowser
import tkinter as tk
from tkinter import PhotoImage, INSERT, END, Text, ttk, WORD, font as tkfont
from PIL import Image, ImageTk
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import os

'''
=================================================================
                        AUTOMATING FUNCTIONS
=================================================================
'''


# script to run ufc record scraper, then imports the csv file to sql server using pandas and sqlalchemy to set datatypes
def update_records():
    subprocess.run(['python', 'UfcRecordScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "ufcRecords-data.csv"
    data = pd.read_csv(file_name)
    dtype_dict = {
        'RecordType': sqlalchemy.String(255), # varchar(255)
        'RecordHolder': sqlalchemy.String(255),
        'Record': sqlalchemy.String(255),
        'Date': sqlalchemy.Date(),  # (mm-dd-yyy)
        'Event': sqlalchemy.String(255)
    }
    engine = get_db_connection_auto()
    data.to_sql('RecordBook', engine, if_exists='replace', index=False, dtype=dtype_dict)


# script to run upcoming fight scraper, then imports the csv file to sql server using pandas and sqlalchemy to set datatypes
def update_upcoming():
    results_text.delete(1.0, END)
    results_text.insert(END, "\t\t\tUpcoming fights have been updated to to the latest posted on http://ufcstats.com",
                        "large_font")
    subprocess.run(['python', 'UpcomingFightsScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "UpcomingEvents-data.csv"
    data = pd.read_csv(file_name)
    dtype_dict = {
        'EventID': sqlalchemy.String(255),
        'Name': sqlalchemy.String(255),
        'Date': sqlalchemy.Date(),
        'Location': sqlalchemy.String(255)
    }
    engine = get_db_connection_auto()
    data.to_sql('UpcomingEvents', engine, if_exists='replace', index=False, dtype=dtype_dict)


# script to run completed event scraper, then imports the csv file to sql server using pandas and sqlalchemy to set datatypes
def update_past_events():
    subprocess.run(['python', 'CompletedEventScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "CompletedEvents-data.csv"
    data = pd.read_csv(file_name, encoding='ISO-8859-1') # had to use encoding to avoid csv reading errors?
    dtype_dict = {
        'EventID': sqlalchemy.String(255),
        'Name': sqlalchemy.String(255),
        'Date': sqlalchemy.Date(),
        'Location': sqlalchemy.String(255)
    }
    engine = get_db_connection_auto()
    data.to_sql('CompletedEvents', engine, if_exists='replace', index=False, dtype=dtype_dict)


# script to run fight scraper, then imports the csv file to sql server using pandas and sqlalchemy to set datatypes
def update_fights():
    subprocess.run(['python', 'FightScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "fight-data-raw.csv"
    data = pd.read_csv(file_name, encoding='ISO-8859-1')
    dtype_dict = {
        'EventID': sqlalchemy.String(255),
        'EventName': sqlalchemy.String(255),
        'Fighter1ID': sqlalchemy.String(255),
        'Fighter1Name': sqlalchemy.String(255),
        'Fighter2ID': sqlalchemy.String(255),
        'Fighter2Name': sqlalchemy.String(255),
        'WinnerID': sqlalchemy.String(255)
    }
    engine = get_db_connection_auto()
    data.to_sql('AllFights', engine, if_exists='replace', index=False, dtype=dtype_dict)


'''
=================================================================
                        QUERY FUNCTIONS
=================================================================
'''


def open_link(url):
    webbrowser.open_new(url)

# this db connection function is for querying the db
def get_db_connection():
    server = os.environ.get('DB_SERVER', 'DESKTOP-671S80O\SQLEXPRESS')
    database = os.environ.get('DB_DATABASE', 'UFCVUE')
    conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_string)


# this db connection function is for the automated updating of the db
def get_db_connection_auto():
    server = os.environ.get('DB_SERVER', 'DESKTOP-671S80O\\SQLEXPRESS')
    database = os.environ.get('DB_DATABASE', 'UFCVUE')
    conn_string = f'mssql+pyodbc://{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server' # 17 driver was the only one that worked
    return create_engine(conn_string)


'''
------------------------------------------------------------------
The `queryUpcoming` function connects to the UFC VUE DB and pulls all the upcoming fights
that were listed on ufcstats.com and displays to the text widget
------------------------------------------------------------------
'''


def query_upcoming():
    try:
        conn = get_db_connection()
        print("Connection Successful")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM [UFCVUE].[dbo].[UpcomingEvents] ORDER BY Date asc")
        records = cursor.fetchall()

        results_text.delete(1.0, tk.END) # delete anything in text box before inserting

        if records:
            for i, record in enumerate(records):
                # set the main link
                hyperlink = "http://ufcstats.com/event-details/" + str(record[0])
                hyperlink_tag = f"hyperlink{i}"

                # format the date to word form
                datestring = record[2]
                dateobject = datetime.datetime.strptime(datestring, "%Y-%m-%d") # had to import datetime separately and then reference it twice to get it to work
                longdate = dateobject.strftime("%B %d, %Y") # convert old format to new format with words

                # insert the name as clickable text
                start_index = results_text.index(INSERT) # start must be before the insert
                eventname = str(record[1])
                # sometimes the event's name isn't up to date, looks terrible if only UFC xxx is displayed
                if len(str(record[1])) < 10:
                    eventname += ": Main Event Not Determined"

                results_text.insert(END, "\t\t\t\t\t" + f"{eventname:^10}" + "\n") # some formatting to help center the text
                end_index = results_text.index(END) # end must be directly after the insert
                results_text.tag_add(hyperlink_tag, start_index, end_index)  # add the tag that holds the link to the text
                results_text.tag_config(hyperlink_tag, font=large_font, foreground="#C10021", underline=True) # make it look like a link w/ same theme

                results_text.insert(END, "\t\t\t\t\t\t" + f"{longdate:^30}" + "\n", "medium_font")

                results_text.tag_bind(hyperlink_tag, "<Button-1>", lambda e, url=hyperlink: open_link(url))  # had to use lambda to attach the openlink function to the event of
                                                                                                                      # "clicking" associated with the <Button-1> sq

                results_text.insert(END, "\t\t\t\t\t\t" + f"{str(record[3]):^20}" + "\n\n", "small_font")

        else:
            results_text.insert(INSERT, "No records found.") # if for some reason the table exists but no data in table
    except Exception as e:
        print("Failed to query the database", e)
        results_text.insert(INSERT, "Failed to query the database: {}".format(e)) # if we were unable to connect to the table or db


'''
------------------------------------------------------------------
The `queryPastEvents` function connects to the UFC VUE DB and pulls all the previous
 FC Event data there were listed on ufcstats.com and displays to the text widget
------------------------------------------------------------------
'''


def query_past_events():
    try:
        conn = get_db_connection()
        print("Connection Successful")
        cursor = conn.cursor()
        cursor.execute(
            # built this query to avoid random order of fights per event, whenever location was added it changed the order of the fights
            # implemented a row counter in the original query prior to location, hence the OVER clause, to keep original order of fights
            "WITH OrderedFights AS (SELECT A.*, C.Date as Date, C.Location as Location,ROW_NUMBER() OVER (ORDER BY C.Date DESC) as RowPosition "
            "FROM [UFCVUE].[dbo].[AllFights] A join CompletedEvents C ON A.EventID = C.EventID ) "
            "SELECT O.*, F.Name as Winner FROM OrderedFights O join FighterBaseStats F on O.WinnerID = F.FighterID order by O.RowPosition asc")
        records = cursor.fetchall()
        results_text.delete(1.0, END)
        if records:
            last_record = None  # keep track of lack record to avoid spamming the event name see below
            for i, record in enumerate(records):
                current_record = str(record[1])  # current record being checked

                datestring = record[7]
                dateobject = datetime.datetime.strptime(datestring, "%Y-%m-%d")
                longdate = dateobject.strftime("%B %d, %Y")

                hyperlink = "http://ufcstats.com/event-details/" + str(record[0])
                hyperlink_tag = f"hyperlink{i}"  # unique tag for each hyperlink, or else the same hyperlink gets applied to each individual tag

                # if the current record is not a duplicate, it gets added, cuz we don't like spam
                if current_record != last_record:
                    results_text.insert(END, "\t\t\t\t\t     ")

                    start_index = results_text.index(INSERT)
                    # center aligning the text with a WIDTH of 30
                    print_records = f"{current_record:^30}\n"
                    # insert the new event
                    results_text.insert(END, print_records, "large_font")
                    end_index = results_text.index(END)
                    results_text.tag_add(hyperlink_tag, start_index, end_index)
                    results_text.tag_config(hyperlink_tag, font=large_font, foreground="#C10021", underline=True)
                    results_text.tag_bind(hyperlink_tag, "<Button-1>", lambda e, url=hyperlink: open_link(url))
                    # insert the date
                    results_text.insert(END, "\t\t\t\t\t\t           " + longdate, "medium_font")
                    # insert the location
                    location_text = record[8]
                    results_text.insert(END, "\n\t\t\t\t\t\t  " + location_text, "small_font")
                # insert the fights after the event name has been inserted
                print_records = "\n\t\t\t\t\t\t" + str(record[3]) + " vs. " + str(record[5]) + "\n"
                last_record = current_record  # update the last record inserted, so we don't spam
                results_text.insert(END, print_records, "medium_font")
                # insert the winner
                winner_record = "\t\t\t\t\t\t     Winner - " + str(record[10]) + "\n"
                results_text.insert(END, winner_record, "medium_font2")
        else:
            results_text.delete(1.0, END)
            results_text.insert(INSERT, "No records found.")
    except Exception as e:
        print("Failed to query the database", e)
        results_text.insert(INSERT, "Failed to query the database: {}".format(e))


'''
------------------------------------------------------------------
The `queryRecords` function connects to the UFC VUE DB and pulls a short sample of UFC Records data
from the first page of ufc.com/records and displays to the text widget
------------------------------------------------------------------
'''


def query_records():
    try:
        conn = get_db_connection()
        print("Connection Successful")

        cursor = conn.cursor()
        # this query connects the record table to the event and fighter table, that way the EventIDs and FighterIDs can populate
        # to allow the user to click and see the event where the record was broken and see the fighter's record/stats
        cursor.execute("SELECT TOP (1000) R.*, F.FighterID, C.EventID FROM [UFCVUE].[dbo].[RecordBook] R "
                       "join CompletedEvents C on R.Event = C.Name join FighterBaseStats F on R.RecordHolder = F.Name order by Date desc")
        records = cursor.fetchall()

        results_text.delete(1.0, END)

        if records:

            for i, record in enumerate(records):
                # for fighter
                hyperlink = "http://ufcstats.com/fighter-details/" + str(record[5])
                hyperlink_tag = f"hyperlink{i}"  # set the format for the link
                # for fighter
                results_text.tag_config(hyperlink_tag, font=large_font, foreground="#659FA3", underline=True)
                results_text.tag_bind(hyperlink_tag, "<Button-1>", lambda e, url=hyperlink: open_link(url))
                # for event
                hyperlink2 = "http://ufcstats.com/event-details/" + str(record[6])
                hyperlink2_tag = f"hyperlink2{record}"  # had to set as record to ensure different/unique link
                # for event
                results_text.tag_config(hyperlink2_tag, font=extralarge_font, foreground="#C10021", underline=True)
                results_text.tag_bind(hyperlink2_tag, "<Button-1>", lambda e, url=hyperlink2: open_link(url))
                # setting links
                format_element = "\t\t\t\t\t          "
                results_text.insert(END, format_element)
                first_element = f"{str(record[0]):^10}" + "\n"
                start_index2 = results_text.index(INSERT)
                results_text.insert(END, first_element, "extralarge_font")
                end_index2 = results_text.index(END)
                results_text.tag_add(hyperlink2_tag, start_index2, end_index2)

                # convert sql date format to words
                datestring = record[3]
                dateobject = datetime.datetime.strptime(datestring, "%Y-%m-%d")
                longdate = dateobject.strftime("%B %d, %Y")

                # formatting the text for userfriendliness
                holder_text = "\t\t\t\t\t\t        "
                name_text = f"{str(record[1]):^10}"
                date_text = "\t\t\t\t\t\t            " + f"{longdate:^30}" + "\n"

                results_text.insert(END, date_text, "medium_font")
                results_text.insert(END, holder_text)
                start_index = results_text.index(INSERT)
                results_text.insert(END, name_text, "medium_font")
                end_index = results_text.index(END)
                results_text.tag_add(hyperlink_tag, start_index, end_index)

                remaining_text = "\n\t\t\t\t\t\t\t      Record: " + str(record[2]) + "\n\n"
                results_text.insert(END, remaining_text, "medium_font")
        else:
            results_text.delete(1.0, END)
            results_text.insert(INSERT, "No records found.")
    except Exception as e:
        print("Failed to query the database", e)
        results_text.insert(INSERT, "Failed to query the database: {}".format(e))


'''
------------------------------------------------------------------
The `queryFighters` function connects to the UFC VUE DB and pulls all fighter data from ufcstats.com 
and displays to the text widget, since it pulls all fighters - THIS DOES TAKE TIME TO LOAD ONCE BUTTON IS PRESSED
------------------------------------------------------------------
'''


def query_fighters():
    try:
        conn = get_db_connection()
        print("Connection Successful")

        cursor = conn.cursor()
        # this query was built to only select the top 400 fighters that have won recently from all the fights
        # the purpose of that is to limit the number of fighters that get populated
        # need to limit the # of fighters because the action of adding the hyperlink tag to the text and formatting the text takes time when
        # it's spanned over thousands of rows (7k+ total fighters in the DB)
        cursor.execute("WITH RecentFighters AS "
                       "(SELECT TOP(400) A.WinnerID, MAX(C.Date) as MostRecentDate FROM dbo.AllFights A "
                       "JOIN dbo.CompletedEvents C ON A.EventID = C.EventID GROUP BY A.WinnerID "
                       "ORDER BY MostRecentDate DESC) SELECT F.*, RF.NameCount FROM dbo.FighterBaseStats F JOIN("
                       "SELECT WinnerID, COUNT(*) AS NameCount FROM RecentFighters GROUP BY WinnerID ) RF "
                       "ON F.FighterID = RF.WinnerID order by Name asc ")
        records = cursor.fetchall()
        results_text.delete(1.0, END)
        # using column so that we don't have to hard code the stat names
        if records:
            columns = [column[0] for column in cursor.description]

            for i, record in enumerate(records):
                # link for the fighter
                hyperlink = "http://ufcstats.com/fighter-details/" + str(record[0])
                hyperlink_tag = f"hyperlink{i}"  # Unique tag for each hyperlink

                format_text = "\t\t\t\t\t\t     "
                results_text.insert(END, format_text)
                start_index = results_text.index(INSERT)
                name_record = f"{str(record[1]):^10}" + '\n'
                results_text.insert(END, name_record, "large_font")
                end_index = results_text.index(END)

                results_text.tag_add(hyperlink_tag, start_index, end_index)
                results_text.tag_config(hyperlink_tag, font=large_font, foreground="#C10021", underline=True)
                results_text.tag_bind(hyperlink_tag, "<Button-1>", lambda e, url=hyperlink: open_link(url))

                # creating a two column output of the fighter stats for userfriendliness
                column_data = ''
                for i, (col, rec) in enumerate(zip(columns[2:-2], record[2:-2])):
                    if i % 2 == 0:
                        column_data += f"\t\t\t\t\t\t        {col}: {rec}".ljust(30)  # left column
                    else:
                        column_data += f"{col}: {rec}\n".rjust(-20)  # right column

                column_data += "\n"
                results_text.insert(END, column_data, "medium_font")

        else:
            results_text.delete(1.0, END)
            results_text.insert(INSERT, "No records found.")
    except Exception as e:
        print("Failed to query the database", e)
        results_text.insert(INSERT, "Failed to query the database: {}".format(e))


'''
=================================================================
                        AESTHETIC AND BUTTON FUNCTIONS
=================================================================
'''


def center_window(w, h):
    # screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # x and y coordinates for window to open
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    # dimensions of the screen and place that baby in the center!
    root.geometry(
        '%dx%d+%d+%d' % (w, h, x, y - 50))  # -50 so its higher, that way user can see entire image (hopefully)


def resize_background(event):
    # extract window size
    width = root.winfo_width()
    height = root.winfo_height()

    # change the size of the original image when the image is resized by user
    resized_img = original_img.resize((width, height))
    resized_imgtk = ImageTk.PhotoImage(image=resized_img)

    # assign background label to use the new resized image
    background_label.config(image=resized_imgtk)
    background_label.image = resized_imgtk


def custom_scrollbar(root):
    # style using Ttk to customize the scrollbar
    style = ttk.Style(root)
    style.theme_use('clam')  # clam allows for the most customization of all ttk themes
    style.configure("Custom.Vertical.TScrollbar", gripcount=0,
                    background='#C10021', arrowcolor='black', troughcolor='black', bordercolor='black',
                    darkcolor='black',
                    lightcolor='grey')

    scrollbar = ttk.Scrollbar(root, style="Custom.Vertical.TScrollbar", orient='vertical')
    scrollbar.grid(row=3, column=1, sticky='ns')
    return scrollbar


'''
------------------------------------------------------------------
-0------0---------0--------  BUTTON FUNCTIONS!  -0------0---------0--------
------------------------------------------------------------------
'''


def on_record_button_click():
    query_records()


def on_fight_button_click():
    results_text.delete(1.0, END)
    results_text.insert(INSERT, "\t\t\t     LOADING... Please wait up to 6 seconds for data to load", "large_font")
    results_text.after(200, query_past_events)


def on_fighter_button_click():
    query_fighters()


def on_upcoming_button_click():
    query_upcoming()

# had to use the after function in order to stagger the functions. if the functions aren't staggered in this way
# the app will freeze
def on_update_button_click():
    results_text.delete(1.0, END)
    results_text.insert(INSERT, "\t\t\t\tLOADING... Please wait for 5 minutes for data to fully update", "large_font")
    results_text.after(200, update_records)
    results_text.after(400, update_past_events)
    results_text.after(600, update_fights)
    results_text.after(800, update_upcoming)


def on_update_upcoming_button_click():
    results_text.delete(1.0, END)
    results_text.insert(END, "\t\t\t\tLOADING... Please wait up to 10 seconds for data to update", "large_font")
    results_text.after(1000, update_upcoming)
    results_text.after(5000, query_upcoming)


'''
==============================================================================
                                FRONT END
==============================================================================
'''

root = tk.Tk()
root.title("OCTA VUE")
icon = PhotoImage(file='icon1.png') # sets the icon in the upper left hand corner
root.iconphoto(False, icon)
root.geometry("1124x968")
window_width = 1124
window_height = 968
center_window(window_width, window_height) # put the window in the center of the screen

# load the original background image
original_img = Image.open("background4 (2).png")

# create a label to display the background image
background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# bind the resize function to window resize event
root.bind("<Configure>", resize_background)

# configure the row and column to make sure the image is centered
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# creating a Frame to hold the Text widget and the Scrollbar
frame_results = tk.Frame(root, bg='black')
frame_results.grid(row=3, column=0, columnspan=4, sticky='nsew', padx=20, pady=60)
frame_results.grid_columnconfigure(0, weight=1)

# assign scrollbar to Custom Scrollbar
scrollbar = custom_scrollbar(frame_results)
scrollbar.grid(row=0, column=1, sticky='ns')

# configuring the Text widget
results_text = Text(frame_results, wrap=WORD, bg='black', fg='red', width=100, height=20, yscrollcommand=scrollbar.set)
results_text.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
results_text.tag_configure("center", justify='center')
results_text.tag_add("center", "1.0", "end")

# creating fonts for the output (size and etc)
extralarge_font = tkfont.Font(size=18, weight="bold") # bigger red text
large_font = tkfont.Font(size=14, weight="bold") # red text
medium_font = tkfont.Font(size=11, weight="bold") # not actually small but it's the white text
small_font = tkfont.Font(size=13, weight="bold") # grey text

# configuring all fonts (assigning color)
results_text.tag_configure("extralarge_font", font=extralarge_font, foreground="#C10021") # red
results_text.tag_configure("large_font", font=large_font, foreground="#C10021")
results_text.tag_configure("medium_font", font=medium_font, foreground="white")
results_text.tag_configure("medium_font2", font=medium_font, foreground="#C10021") # just the red version of the same font size
results_text.tag_configure("small_font", font=small_font, foreground="#659FA3") # grey

# linking scrollbar to the Text widget
scrollbar.config(command=results_text.yview)

# font for buttons
bold_font = tkfont.Font(family="Helvetica", size=10, weight="bold")

# FOR RECORDS
showRecordButton = tk.Button(root, text="UFC\nRECORD HOLDERS", fg='black', command=on_record_button_click)
showRecordButton.configure(font=bold_font, width=1, bg="black",  # background color
                           fg="white",  # foreground (text) color
                           activebackground="darkred",  # background color when the button is clicked
                           activeforeground="white",  # font color when the button is clicked
                           padx=10, pady=5,
                           relief="raised",
                           bd=4)

# FOR RECENT FIGHTS
showFightsButton = tk.Button(root, text="PAST\n UFC EVENTS", fg='black', command=on_fight_button_click)
showFightsButton.configure(font=bold_font, width=1, bg="black",
                           fg="white",
                           activebackground="darkred",
                           activeforeground="white",
                           padx=10, pady=5,
                           relief="raised",
                           bd=4)

# FOR ALL FIGHTERS
showFightersButton = tk.Button(root, text="ALL\nUFC FIGHTERS", fg='black', command=on_fighter_button_click)
showFightersButton.configure(font=bold_font, width=1, bg="black",
                             fg="white",
                             activebackground="darkred",
                             activeforeground="white",
                             padx=10, pady=5,
                             relief="raised",
                             bd=2)

# FOR UPCOMING EVENTS
showUpcomingButton = tk.Button(root, text="ALL\nUPCOMING EVENTS", fg='black', command=on_upcoming_button_click)
showUpcomingButton.configure(font=bold_font, width=1, bg="black",
                             fg="white",
                             activebackground="darkred",
                             activeforeground="white",
                             padx=10, pady=5,
                             relief="raised",
                             bd=2)

# FOR UPDATING THE DATASET
updateDBButton = tk.Button(root, text="UPDATE\nALL RECORDS", fg='black', command=on_update_button_click)
updateDBButton.configure(font=bold_font, width=1, bg="#370408",
                         fg="white",
                         activebackground="black",
                         activeforeground="white",
                         padx=10, pady=5,
                         relief="raised",
                         bd=2)

# FOR UPDATING UPCOMING FIGHTS ONLY
updateUpcomingButton = tk.Button(root, text="UPDATE\nUPCOMING FIGHTS", fg='black',
                                 command=on_update_upcoming_button_click)
updateUpcomingButton.configure(font=bold_font, width=1, bg="#345A5B",
                               fg="white",
                               activebackground="black",
                               activeforeground="white",
                               padx=10, pady=5,
                               relief="raised",
                               bd=2)

# configure grid columns to distribute space evenly
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# PLACEMENT OF BUTTONS with 'sticky' attribute for alignment
showFightsButton.place(relx=0.1, rely=0.55, anchor='center', width=150, height=50)
showFightersButton.place(relx=0.30, rely=0.55, anchor='center', width=150, height=50)
showUpcomingButton.place(relx=0.70, rely=0.55, anchor='center', width=150, height=50)
showRecordButton.place(relx=0.90, rely=0.55, anchor='center', width=150, height=50)
updateDBButton.place(relx=0.5, rely=0.44, anchor='center', width=115, height=60)
updateUpcomingButton.place(relx=0.5, rely=0.35, anchor='center', width=150, height=60)

# keep it going
root.mainloop()
