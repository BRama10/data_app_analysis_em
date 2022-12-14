import sqlite3
import flask
from flask import Flask, render_template, request, redirect, url_for
from data_visuals import create_bar_problems, create_scatter_therm_household, create_line_plot
from drive_reader import callbackFunction
from db_reader import main_db
from db_html import html_tables
from db_access_tool import Query, setup_sql_dict
import db_access_tool
import shutil
import os
from DataFiltration import setup
import pandas as pd
from bokeh.resources import INLINE

import google.oauth2.credentials
import google_auth_oauthlib.flow


# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

print(os.listdir('/tmp/'))

#create in-memory folders for templates and static files
try:
    os.mkdir('/tmp/templates')
except:
    pass
try:
    os.mkdir('/tmp/static')
except:
    pass


source_folder_templates = '/srv/templates/'
source_folder_static = '/srv/static/'
destination_folder_templates = '/tmp/templates/'
destination_folder_static = '/tmp/static/'

#copy all static and template files into the new location
for file_name in os.listdir(source_folder_templates):
    source = source_folder_templates + file_name
    dest = destination_folder_templates + file_name

    if os.path.isfile(source):
        shutil.copy(source, dest)
        print('Copied: ', file_name)

for file_name in os.listdir(source_folder_static):
    source = source_folder_static + file_name
    dest = destination_folder_static + file_name

    if os.path.isfile(source):
        shutil.copy(source, dest)
        print('Copied: ', file_name)


#start app with new redirect locations
app = Flask(__name__, template_folder = '/tmp/templates/', static_folder = '/tmp/static/')


app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

#converts the credentials from JSON to usable form
def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


#first page you enter, checks if user is logged in -- if not, then starts verification process
@app.route('/', methods=['GET', 'POST'])    
def start():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    return redirect(url_for('starter_page'))


#authorizes user through OAuth2 
@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  #flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
  flow.redirect_uri = 'https://em-data-science-app-370321.ue.r.appspot.com/oauth2callback'
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)

#verifies specific access to my application (this is after the general google login, and it contains the checkboxes)
@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('starter_page'))

#isn't useful for the user but I can use if needed to revoke someone's access from the app
@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())

#reboots the whole app's access tools, failsafe if unable to revoke individual's access
@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

#the first page (where you see the small box)
#verifies credentials, if valid, prompts you to enter file name 
#calls the drive_reader file in order to download the file and converts into needed formats
@app.route('/i', methods=['GET', 'POST'])
def starter_page():
    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
    
    if request.method == 'POST':
        val = request.form.get('file_name')
        callbackFunction(val, credentials)

        r_file = pd.read_csv("/tmp/datafile.file")
        r_file.to_csv("/tmp/datafile.csv", index=None)

        return render_template('drive.html', var= True)
    return render_template('drive.html', var=False)

#this is the webpage with the 'CLICK HERE' url
#basically calls the processing files one at a time
@app.route('/file_cleaner/')
def data_cleaning():
    global dc,val
    setup()
    main_db()
    html_tables()

    return redirect(url_for('index'))

#shows the index page (the one with the color and images)
@app.route('/index/')
def index():
    return render_template('index.html')

#shows the data table
@app.route('/data/')
def redirect_response_1():
    return render_template('data.html')

#shows the contacts table
@app.route('/contact/')
def redirect_response_2():
    return render_template('contact.html')

#displays the database query editor
@app.route('/database/')
def redirect_response_3():
    #nums1, nums2 = [x for x in range(len(names))], [x+100 for x in range(len(names))]
    #colNamesNums = list(map(lambda i,j,k : (i,j,k) , names,nums1, nums2))
    #return render_template('database.html',colNames = colNamesNums)
    
    #sets up the access tool
    setup_sql_dict()
    dc =[]
    from db_access_tool import _types, _names_contact, _names_data

    #specifies the rows that can display detailed query editors (the single-double bounds)
    for x in range(len(_types)):
        if _types[x] == 'REAL':
            dc.append(x)
    #displays webpage
    return render_template('database.html',contact_col = enumerate(_names_contact), data_col = enumerate(_names_data), dtypes_col=dc)

#displays the graph options page
@app.route('/trends/')
def redirect_response_4():
    return render_template('trends.html')


#['OR', 'col1_name', 'col_val']
#['col1_name', 'col_infoval']
#['col1_name', 'condition', [vals]]


#displays the results from the query
@app.route('/database_result/', methods =["POST"])
def redirect_response_5():
    #sets up access tool
    setup_sql_dict()
    from db_access_tool import _types, _raw_data, _raw_contact, _names_contact, _names_data
    dc = []
      
    #gets columns that have single or double bounds
    for x in range(len(_types)):
        if _types[x] == 'REAL':
            dc.append(x)
    
    #gets the desired table name
    if request.form.get('choosetable') == 'data':
        tbl_name = 'data'
    else:
        tbl_name = 'contact'

    marked_vals_contact, marked_vals_data, bounding = [], [], []
    

#somehow the dummy variables in the for loop become global -  need to fix later, temp fix was changing var names

    #note that both for loops are one-time calls, so data loss is prevented
    #also note that dynamic queries can be done, meaning the first query doesn't have to be the query on the top in the selector

    #gets a list of all results for contact table parameters (such as name, email, etc)
    for a,b in enumerate(_names_contact):
        if request.form.get('value_contact_'+str(a)) != "":
            marked_vals_contact.append([None, a, request.form.get('value_contact_'+str(a))])
            try:
                marked_vals_contact[-1][0] = request.form.get('contact_and_or_'+str(a))
            except:
                marked_vals_contact[-1][0] = 'FIRSTQUERY'
            
    #gets a list of all results for data table parameters (such as therm temp)
    for c,d in enumerate(_names_data):
        if request.form.get('value_data_'+str(c)) != "":
            marked_vals_data.append([None, c, request.form.get('value_data_'+str(c))])
            try:
                marked_vals_data[-1][0] = request.form.get('data_and_or_'+str(c))
            except:
                marked_vals_data[-1][0] = 'FIRSTQUERY'
    
    #identifies and demarcates the complex queries
    for x in dc:
        if request.form.get('double_float_name_'+str(x)) != 'NONE':
            bounding.append([x, request.form.get('double_float_name_'+str(x))])

        elif request.form.get('single_float_name_'+str(x)) != 'NONE':
            bounding.append([x, request.form.get('single_float_name_'+str(x))])
            
    #appends extra parameters to the complex queries in preparation for query generation
    for p in range(len(bounding)):
        for q in range(len(marked_vals_data)):
            if(bounding[p][0] == marked_vals_data[q][1]):
                marked_vals_data[q].append(bounding[p][1])

    #appends extra parameters to the contact table queries in preparation for query generation
    for p in range(len(marked_vals_contact)):
        marked_vals_contact[p][1] = _raw_contact.get(marked_vals_contact[p][1])
        if(len(marked_vals_contact[p]) == 3):
            marked_vals_contact[p].append('eq')
            
    #appends extra parameters to the data table queries in preparation for query generation
    for p in range(len(marked_vals_data)):
        marked_vals_data[p][1] = _raw_data.get(marked_vals_data[p][1])
        if(len(marked_vals_data[p]) == 3):
            marked_vals_data[p].append('eq')
    
    contact_sections, data_sections = [], []

    #create query generator object
    q = Query('/tmp/em_volunteer_survey.db')
    
    #create query sections
    for x in marked_vals_contact:
        contact_sections.append(q.query_generator(x, 'contact'))
    for x in marked_vals_data:
        data_sections.append(q.query_generator(x, 'data'))

    #mapping of first query to the starting on the sequence
    full_set = contact_sections + data_sections
    first_query = None
    
    for z in range(len(full_set)):
        if(full_set[z][0:2] == ' ('):
            first_query = full_set[z]
            del full_set[z]
            break
        
    if(first_query is None):
        exit()
    
    #build query
    result = q.build_query_v2(first_query, full_set, tbl_name)
    
    #call query
    vals = q.use_query(result)
      
    #display query
    return render_template('database_result.html', test=vals, tbl_name = tbl_name, _name_contact=_names_contact, _name_data=_names_data)

#displays graphs based on user choice
@app.route('/data_graph/<val>')
def graph_display(val):
    val = int(val)
    if(val == 1):
        script, div = create_bar_problems()
    elif(val == 2):
        script, div = create_scatter_therm_household()
    elif(val == 3):
        script, div = create_line_plot()
    return render_template('gtemplate.html',plot_script=script,plot_div=div,js_resources=INLINE.render_js(),css_resources=INLINE.render_css(),).encode(encoding='UTF-8')


#callback function to start the app (port # may change depending on GAE's settings at the time)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)

