from pathlib import Path
import sqlite3
import pandas as pd

def main_db():

    Path('/tmp/em_volunteer_survey.db').touch()

    conn = sqlite3.connect('/tmp/em_volunteer_survey.db')
    cur = conn.cursor()

    data = pd.read_csv('/tmp/cleaned_data.csv')
    contact = pd.read_csv('/tmp/contact_data.csv')

    data.to_sql('data', conn, if_exists='replace', index = True)
    contact.to_sql('contact', conn, if_exists='replace', index = True)


    #cur.execute("ALTER TABLE contact DROP COLUMN 'Unnamed: 0';")
    #conn.commit()
    #cur.execute("ALTER TABLE data DROP COLUMN 'Unnamed: 0';")
    #conn.commit()


