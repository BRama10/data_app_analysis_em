import pandas as pd
import numpy as np
from bokeh.layouts import column
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, LinearAxis, Plot, VBar, RangeTool, HoverTool
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Spectral6, magma,Spectral10
from DataFiltration import convert_dict_problems, convert_dict_occur
from scipy.stats import linregress
from bokeh.embed import components
from bokeh.transform import factor_cmap, factor_mark
from datetime import datetime
from bokeh.resources import INLINE

#dicts for converting from to text
inv_dict_problems = {v: k for k, v in convert_dict_problems.items()}
inv_dict_occur = {v: k for k, v in convert_dict_occur.items()}

#converts DataFrame lists from immutable sequences to mutable strings 
def to_1D(series):
    return pd.Series([x for _list in series for x in _list])





#method for creating bar graph
def create_bar_problems():
    #read data file into DataFrame
    df = pd.read_pickle('/tmp/cleaned_data.pkl')
    
    #ensure type formatting is correct
    for x in range(len(df.iloc[:,2])):
      df.iat[x,2] = list(str(df.iat[x,2]))

    #call previous method and get key-value pairs in dict format
    d = to_1D(df['What Energy-Related Problems Do You Face (Select All Applicable Choices)']).value_counts().to_dict()

    #next few lines basically ignore null values, and convert all data in readable format again
    x,y=[],[]

    if d.get('-') != None:
        count = d.get('-')
        d['1'] = d['1'] - count

    for a in d.keys():
        if(a != '-'):
            x.append(a)
            y.append(d.get(a))

    for i in range(len(x)):
        x[i] = inv_dict_problems.get(x[i])

    #create graph template
    source = ColumnDataSource(data=dict(x=x, y=y, color=Spectral6))

    #customize graph template
    p = figure(x_range=x, height=350, title="Types of Energy Problems", toolbar_location='right')

    #create graph itself
    p.vbar(x='x', top='y', width=0.9, color='color', source=source)

    #account for window resizing -- add names
    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    p.xaxis.axis_label = "Problem Name"
    p.yaxis.axis_label = "Number of Households"

    #return metadata of the graph (used in main.py to display in HTML)
    script, div = components(p)

    return script, div

#create scatter plot
def create_scatter_therm_household():
    #read data and assign columns
    df = pd.read_pickle('/tmp/cleaned_data.pkl')
    
    x = df['If yes, what is the thermostat temperature in the winter?']
    y = df['If yes, what is the thermostat temperature in the summer?']

    #setup some external libs such as color and initialize graph template
    source = ColumnDataSource(data=dict(x=x, y=y, ur= df['Number of Household Members']))
    colors = factor_cmap('ur', palette=Spectral10, factors=df['Number of Household Members'].unique())
    #MARKERS = ['hex', 'circle_x', 'triangle']
    #markers = factor_mark('species', MARKERS, df['Number of Household Members'].unique())


    #create regression line template
    res = linregress(np.array(x), np.array(y))
    
    #display actual scatterplot
    plot = figure(title="Correlation Between Winter & Summer Thermostat Temp")
    plot.scatter(x='x',y='y', fill_color=colors,fill_alpha=0.6,size=15,source=source, legend_group='ur', name='scatter')

    #plot.circle(x='x',y='y',size=20,fill_color=colors,fill_alpha=0.6,source=source)

    #display regression line
    y_regress = res.slope * x + res.intercept
    plot.line(x=x, y=y_regress, color='red', legend_label="Regression (Trend) Line", name="regression")

    #add axis labels
    plot.xaxis.axis_label = "Winter Temp (F)"
    plot.yaxis.axis_label = "Summer Temp (F)"

    #return graph metadata for later use
    script, div = components(plot)
    return script, div


#Purely artifical graph
#So few values in table that this kind of graph can't evne be constructed until 4 or 5 workdays....this is useful for an overall picture
#When we collect enough data and on the full version, it'll be only real data.

#generates a bunch of datetime values for use in the demo
def date_gen():
    STATIC_DAYS = ['02','07', '10', '13', '17', '19', '23']
    STATIC_MONTHS = ['11', '12', '01', '02', '03', '04', '05']
    STATIC_YEARS = ['2022', '2022', '2023', '2023', '2023', '2023', '2023']
    dates= []
    form = '%Y-%m-%d'
    for x in range(7):
        dates.append(datetime.strptime((STATIC_YEARS[x]+'-'+STATIC_MONTHS[x]+'-'+STATIC_DAYS[x]), form))
    return dates

#same thing as above but in string format
def date_gen_str():
    STATIC_DAYS = ['02','07', '10', '13', '17', '19', '23']
    STATIC_MONTHS = ['11', '12', '01', '02', '03', '04', '05']
    STATIC_YEARS = ['2022', '2022', '2023', '2023', '2023', '2023', '2023']
    dates= []
    form = '%Y-%m-%d'
    for x in range(7):
        dates.append(STATIC_YEARS[x]+'-'+STATIC_MONTHS[x]+'-'+STATIC_DAYS[x])
    return dates

#creates last line plot
def create_line_plot():
    #set up all values required to plot
    dates = date_gen()
    dates_str = date_gen_str()
    lightbulbs = [42, 19, 50, 65, 80, 72, 75]
    airtight = [66, 72, 93, 78, 84, 79, 92]
    avg_energy_awareness_1 = [x*100 for x in [0.2, 0.23, 0.35, 0.45, 0.42, 0.62, 0.59]]
    avg_energy_awareness_2 = [None, None, None, None, 31, 34, 33]
    vol_part = [40, 20, 24, 23, 45, 42, 50]
    
    #create graph template
    source = ColumnDataSource(data=dict(vol_part = vol_part, date=dates, air=airtight, lights=lightbulbs,avg_energy_1=avg_energy_awareness_1, avg_energy_2=avg_energy_awareness_2, datestr=dates_str))

    #setup interactive tools
    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
    
    #display figure
    p = figure(height = 800, width = 1300,title = 'Overall Trends Graph', x_axis_type = 'datetime', x_axis_label='Date',background_fill_color="#efefef", tools=TOOLS)

    #hover = p.select(dict(type=HoverTool))
    #Unable to get the formatter aligned with transformation from literal to datetime object so created another data column with dates in string format
    #hover.tooltips = [('Date', '@datestr'), ('Lightbulbs Replaced', '@vol_part'),]
    #hover.mode = 'mouse'
    #hover.formatters  = {'@date':'datetime'}
    #p.add_tools(HoverTool(tooltips=[('Date', '@data{%F}'), ('Lightbulbs Replaced', '@lights'),],formatters={'@data':'datetime',},mode='vline'))
    #HoverTool.formatters={'@date':'datetime'}
    #HoverTool.tooltips = [('Date', '@date'), ('Lightbulbs Replaced', '@lights'),]

    #basic stats regarding numbers
    #create different linegraphs for each of the vars and also add a hovertool for each option
    plot1 = p.line(line_width = 3, line_dash = 'dotted', x='date', y='lights', source=source, legend_label='Lightbulbs Replaced', color='green')
    p.add_tools(HoverTool(renderers=[plot1],tooltips=[('Date', '@datestr'), ('Lightbulbs Replaced', '@lights'),],))
    
    plot2 = p.line(line_width = 3, line_dash = 'dotted', x='date', y='air', source=source, legend_label='Electrical Outlets Sealed', color='blue')
    p.add_tools(HoverTool(renderers=[plot2],tooltips=[('Date', '@datestr'), ('Electrical Outlets Sealed', '@air'),],))
    
    plot3 = p.line(line_width = 3, x='date', y='avg_energy_2', source=source, legend_label='Average Energy Awareness Score - Alexandria City (/100)', color='orange')
    p.add_tools(HoverTool(renderers=[plot3],tooltips=[('Date', '@datestr'), ('Avg E-Score : Alexandria', '@avg_energy_2'),]))

    plot4 = p.line(line_width = 3, x='date', y='avg_energy_1', source=source, legend_label='Average Energy Awareness Score - Gates of Ballston (/100)', color='red')
    p.add_tools(HoverTool(renderers=[plot4],tooltips=[('Date', '@datestr'), ('Avg E-Score : Ballston', '@avg_energy_1'),]))

    plot5 = p.line(line_width = 3, x='date', y='vol_part', source=source, legend_label='Volunteer Participation (numbers)', color='purple')
    p.add_tools(HoverTool(renderers=[plot5],tooltips=[('Date', '@datestr'), ('Volunteer Participation', '@vol_part'),]))

    #relational stats based on scores
    #scores are weighted percentages of survey results. For example, for the question "when do you leave the water running", originally someone may choose all 4 options. However, after one follow-up, they choose only 3, and then on a secon follow-up, they choose 1. This demonstrates energy efficiency awareness.
    
    #customize legend and axis titles
    p.legend.click_policy="hide"
    p.legend.location = 'bottom_right'

    p.xaxis.axis_label = "Date (Timeseries)"
    p.yaxis.axis_label = "Value (Units depending on metric)"
        
    #return graph metadata
    script, div = components(p)
    return script, div


#Some more failed attempts at trying to get the formatting right :/
    
#p = figure(y_axis_type="linear", height=300, width=800, tools=TOOLS, toolbar_location=None, x_axis_type="datetime", background_fill_color="#efefef")
#p.line('date', 'lights', source=source)

#select = figure(title="Drag the middle and edges of the selection box to change the range above", height=130, width=100, y_range=p.y_range, x_axis_type="datetime", y_axis_type=None,tools="", toolbar_location=None, background_fill_color="#efefef")
#range_tool = RangeTool(x_range=p.x_range)
#range_tool.overlay.fill_color = "navy"
#range_tool.overlay.fill_alpha = 0.2

#select.line('date', 'lights', source=source)
#select.ygrid.grid_line_color = None
#select.add_tools(range_tool)
#select.toolbar.active_multi = range_tool


#create_scatter_therm_household()









