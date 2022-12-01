#from DataFiltration import convert_dict_problems, convert_dict_occur, convert_dict_light, convert_dict_watertap, convert_dict_minshower
#from DataFiltration import main_function
#from DataFiltration import convert_dict_leavelight, convert_dict_leavetv, convert_dict_leavekitchen, convert_dict_leavedish, convert_dict_leaveclothes, convert_dict_heatset
import sqlite3

_names_contact,_names_data,_map_contact, _copy_contact, _raw_contact,_map_data, _copy_data, _raw_data, _info_data,  _info_contact, _types = [None for x in range(11)]

def setup_sql_dict():
    global _names_contact,_names_data,_map_contact, _copy_contact, _raw_contact,_map_data, _copy_data, _raw_data, _info_data,  _info_contact, _types
    c = sqlite3.connect('em_volunteer_survey.db')
    cur = c.cursor()
    cur.execute("SELECT * FROM contact")
    _names_contact = [description[0] for description in cur.description][1:]
    cur.execute("SELECT * FROM data")
    _names_data = [description[0] for description in cur.description][1:]
    

    _map_contact, _copy_contact, _raw_contact = enumerate(_names_contact), enumerate(_names_contact), dict(enumerate(_names_contact))
    _map_data, _copy_data, _raw_data = enumerate(_names_data), enumerate(_names_data), dict(enumerate(_names_data))
    c.row_factory = sqlite3.Row

    _info_data = cur.execute("PRAGMA table_info(data)").fetchall()[1:]
    _info_contact = cur.execute("PRAGMA table_info(contact)").fetchall()[1:] 
    _types = [x[2] for x in _info_data]
    return True



class Translate:
    def __init__(self):
        keys = ["Energy Problems","Problem Location","Bulb Type","Leave Room-Lights","Leave Room-TV","Exhaust","Dishwasher","Clothes","Heat Setting", "Water Tap", "Shower"]
        values = [convert_dict_problems, convert_dict_occur, convert_dict_light, convert_dict_leavelight, convert_dict_leavetv, convert_dict_leavekitchen, convert_dict_leavedish, convert_dict_leaveclothes, convert_dict_heatset, convert_dict_watertap, convert_dict_minshower]
        args = dict(map(lambda i,j : (i,j) , keys,values))

        

class Query:
    def __init__(self, name):
        self.conn = sqlite3.connect(name)
        self.cur = self.conn.cursor()
        kwds = {
            1 : 'SELECT',
            2 : 'WHERE',
            3 : 'AND',
            4 : 'OR',
            5 : 'ORDER BY',
            6 : ['ASC', 'DSC'],
            7 : 'COUNT',
            8 : 'FROM'
            }
        self.result = []

##############################################################################################################
    # cmd must be in the format [val1, val2, val3, val4]
    # op must be in the format [op1, op2, op3] = [AND, OR, AND]
    # SELECT val1 FROM val2 WHERE val3 AND val4 AND val5 ORDER BY val6
#    def build_query(self, cmd, op, tbl_name):
#        query = 'SELECT ' + tbl_name + '.' + cmd[0] + ' FROM ' + cmd[1]
#        if(len(cmd) > 2):
#            query += ' WHERE '
#        for x in range(0, len(op)):
#            query += cmd[x+2] + ' ' + op[x] + ' '
#        query += cmd[-1] + 'AND data.index = contact.index'
#        return query+';'
##############################################################################################################


    def use_query(self, query):
        self.conn.row_factory = sqlite3.Row
        self.cur.execute(query)
        return self.cur.fetchall()

    #tbl is name of table
    #cols is the list of columns
    #vals is the list of tuples with corresponding value-data types
    def build_query_section(self, tbl, cols, vals):
        for x in range(0, len(vals)):
            if(vals[x][1] == 'INTEGER'):
                vals[x][0] = int(vals[x][0])
            elif(vals[x][1] == 'REAL'):
                vals[x][0] = float(vals[x][0])

        
        for x in range(0, len(cols)):
            if(vals[x][1] == 'TEXT'):
                self.result.append(tbl+'.`'+cols[x]+'` = ' + "\'" + vals[x][0] + "\'")
            else:
                self.result.append(tbl+'.`'+cols[x]+'` = ' + vals[x][0])

        return True

    #tbl_name is desired table
    #desired_col is the desired column, * if want all
    #tbls list of all tables in query
    def build_query(self, tbl_name, desired_col, tbls):
        if(desired_col != '*'):
            desired_col = '`' + desired_col + '`'
        #note that this function isn't scalable past two tables at the moment -- just hardcoded for time's sake.
        
        query = 'SELECT ' + tbl_name + '.' + desired_col + ' FROM ' + ','.join(tbls) + ' WHERE ' + ' AND '.join(self.result) + ' AND ' + tbls[0] + '.`index` = ' + tbls[1] + '.`index`;'

        return query
        

    def build_query_v2(self, first_query, queries, desired_tbl):
        start = 'SELECT ' + desired_tbl+'.*' + ' FROM data,contact WHERE (' + first_query
        for query in queries:
            start += query
        return start + ') AND (data.`index` = contact.`index`);'
    
        

    def query_generator(self, lst, tbl_name):
        key,TYPE,val,exitcode, TRACK = '', '', '', 1, ''
        col_name = '`'+lst[1]+'`'
        
        if lst[0] == None:
            cond = ''
        elif lst[0] == 'and':
            cond = ' AND'
        elif lst[0] == 'or':
            cond = ' OR'
        
        if lst[3] == 'eq':
            key = '='
        elif lst[3] == 'neq':
            key = '<>'
        elif lst[3] == 'geq':
            key = '>='
        elif lst[3] == 'leq':
            key = '<='
        elif lst[3] == 'lt':
            key = '<'
        elif lst[3] == 'gt':
            key = '>'
        elif lst[3] == 'between' or lst[3] == 'greater_lesser':
            if lst[3] == 'between':
                TRACK = 'AND'
            else:
                TRACK = 'OR'
            key = ['>=', '<=']

        if(tbl_name == 'data'):
            for x1,x2,x3,x4,x5,x6 in _info_data:
                if x2 == lst[1]:
                    TYPE = x3
                    break
        else:
            for x1,x2,x3,x4,x5,x6 in _info_contact:
                if x2 == lst[1]:
                    TYPE = x3
                    break
            
        if TYPE == 'INTEGER':
            #dummy line
            val = str(int(lst[2]))
        elif TYPE == 'REAL':
            try:
                #dummy line
                val = str(float(lst[2]))

            except:
                val = list(map(lambda x : str(float(x)), lst[2].split(sep=',')))
                exitcode = 2
        elif TYPE == 'TEXT':
            val = "\'" + lst[2] + "\'"

        if(exitcode == 1):
            query = tbl_name+'.'+col_name + ' ' + key + ' ' + val
        else:

            query = tbl_name+'.'+col_name + ' ' + key[0] + ' ' + val[0] + ' ' + TRACK + ' ' + tbl_name+'.'+col_name + ' ' + key[1] + ' ' + val[1]

        return cond + ' ' + '(' + query + ')'

#q = Query('em_volunteer_survey.db')
     
#test_list_contact = [[None, 'Full Name (First and Last)', 'Balaji Rama', 'eq'], ['and', 'Unit Number', '304', 'eq']]
#test_list_data = [['and', 'If yes, what is the thermostat temperature in the summer?', '90', 'lt'], ['and', 'If yes, what is the thermostat temperature in the winter?', '45,100', 'between'], ['and', 'What heat setting do you wash your clothes on?', '1', 'eq']]

#run_test_1 = test_list_contact[0]
#run_test_2 = test_list_contact[1]
#run_test_3 = test_list_data[0]
#run_test_4 = test_list_data[1]
#run_test_5 = test_list_data[2]

#d1 = q.query_generator(run_test_1, 'contact')
#d2 = q.query_generator(run_test_2, 'contact')
#d3 = q.query_generator(run_test_3, 'data')
#d4 = q.query_generator(run_test_4, 'data')
#d5 = q.query_generator(run_test_5, 'data')



#d6 = q.build_query_v2(d1, [d2,d3,d4,d5], 'contact')



    


        
        
        
        
        
        
            

    

    
    
