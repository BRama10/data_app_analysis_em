import pandas as pd
from pathlib import Path

def html_tables():
 
    #path = str(Path(__file__).parent.absolute())+ '\\templates'
    path = '/tmp/templates/'

    #writes data & contact tables into html files, which are then displayed to the user when selected
    #strategy is => download from csv, convert to html, save as html in new location
    df1 = pd.read_csv('/tmp/cleaned_data.csv', index_col=0)
    df2 = pd.read_csv('/tmp/contact_data.csv', index_col=0)
 
    f = open(path + 'data.html','w')
    result = df1.to_html()
    f.write(result)
    f.close()

    f = open(path + 'contact.html','w')
    result = df2.to_html()
    f.write(result)
    f.close()

