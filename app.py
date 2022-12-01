import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from data_visuals import create_bar_problems, create_scatter_therm_household, create_line_plot
from drive_reader import callbackFunction
from db_reader import main_db
from db_html import html_tables
from db_access_tool import Query, setup_sql_dict
import db_access_tool

import os
from DataFiltration import setup
import pandas as pd




app = Flask(__name__)



    



@app.route('/', methods=['GET', 'POST'])
def starter_page():
    global val
    if request.method == 'POST':
        val = request.form.get('file_name')
        callbackFunction(val)
        
        r_file = pd.read_csv(val)
        r_file.to_csv(val+'.csv', index=None)

        
        return render_template('drive.html', var= True)
    return render_template('drive.html', var=False)

@app.route('/file_cleaner/')
def data_cleaning():
    global dc,val
    setup('2022 Energy Masters Pre-Visitation Survey (Responses).csv')
    main_db()
    html_tables()

    return redirect(url_for('index'))


@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/data/')
def redirect_response_1():
    return render_template('data.html')

@app.route('/contact/')
def redirect_response_2():
    return render_template('contact.html')

@app.route('/database/')
def redirect_response_3():
    #nums1, nums2 = [x for x in range(len(names))], [x+100 for x in range(len(names))]
    #colNamesNums = list(map(lambda i,j,k : (i,j,k) , names,nums1, nums2))
    #return render_template('database.html',colNames = colNamesNums)
    setup_sql_dict()
    dc =[]
    from db_access_tool import _types, _names_contact, _names_data

    
    for x in range(len(_types)):
        if _types[x] == 'REAL':
            dc.append(x)
    
    return render_template('database.html',contact_col = enumerate(_names_contact), data_col = enumerate(_names_data), dtypes_col=dc)

@app.route('/trends/')
def redirect_response_4():
    return render_template('trends.html')


#['OR', 'col1_name', 'col_val']
#['col1_name', 'col_infoval']
#['col1_name', 'condition', [vals]]
@app.route('/database_result/', methods =["POST"])
def redirect_response_5():
    setup_sql_dict()
    from db_access_tool import _types, _raw_data, _raw_contact, _names_contact, _names_data
    dc = []
    for x in range(len(_types)):
        if _types[x] == 'REAL':
            dc.append(x)
    
    if request.form.get('choosetable') == 'data':
        tbl_name = 'data'
    else:
        tbl_name = 'contact'

    marked_vals_contact, marked_vals_data, bounding = [], [], []
    

#somehow the dummy variables in the for loop become global -  need to fix later, temp fix was changing var names

    for a,b in enumerate(_names_contact):
        if request.form.get('value_contact_'+str(a)) != "":
            marked_vals_contact.append([None, a, request.form.get('value_contact_'+str(a))])
            try:
                marked_vals_contact[-1][0] = request.form.get('contact_and_or_'+str(a))
            except:
                marked_vals_contact[-1][0] = 'FIRSTQUERY'

    for c,d in enumerate(_names_data):
        if request.form.get('value_data_'+str(c)) != "":
            marked_vals_data.append([None, c, request.form.get('value_data_'+str(c))])
            try:
                marked_vals_data[-1][0] = request.form.get('data_and_or_'+str(c))
            except:
                marked_vals_data[-1][0] = 'FIRSTQUERY'
    

    for x in dc:
        if request.form.get('double_float_name_'+str(x)) != 'NONE':
            bounding.append([x, request.form.get('double_float_name_'+str(x))])

        elif request.form.get('single_float_name_'+str(x)) != 'NONE':
            bounding.append([x, request.form.get('single_float_name_'+str(x))])
            
    for p in range(len(bounding)):
        for q in range(len(marked_vals_data)):
            if(bounding[p][0] == marked_vals_data[q][1]):
                marked_vals_data[q].append(bounding[p][1])

    for p in range(len(marked_vals_contact)):
        marked_vals_contact[p][1] = _raw_contact.get(marked_vals_contact[p][1])
        if(len(marked_vals_contact[p]) == 3):
            marked_vals_contact[p].append('eq')

    for p in range(len(marked_vals_data)):
        marked_vals_data[p][1] = _raw_data.get(marked_vals_data[p][1])
        if(len(marked_vals_data[p]) == 3):
            marked_vals_data[p].append('eq')
    
    contact_sections, data_sections = [], []

    q = Query('em_volunteer_survey.db')
    
    for x in marked_vals_contact:
        contact_sections.append(q.query_generator(x, 'contact'))
    for x in marked_vals_data:
        data_sections.append(q.query_generator(x, 'data'))

    full_set = contact_sections + data_sections
    first_query = None
    
    for z in range(len(full_set)):
        if(full_set[z][0:2] == ' ('):
            first_query = full_set[z]
            del full_set[z]
            break
        
    if(first_query is None):
        exit()
    
    result = q.build_query_v2(first_query, full_set, tbl_name)
    
    
    vals = q.use_query(result)
    return render_template('database_result.html', test=vals, tbl_name = tbl_name, _name_contact=_names_contact, _name_data=_names_data)

@app.route('/data_graph/<val>')
def graph_display(val):
    val = int(val)
    if(val == 1):
        return create_bar_problems()
    elif(val == 2):
        return create_scatter_therm_household()
    elif(val == 3):
        return create_line_plot()
    return True


    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)
