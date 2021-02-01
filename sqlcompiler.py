import sqlparse
import re
import numbers



def test(query,currentdb):
    def isidentifier(string):
        if (re.match(identifierregex,string)!=None and string.lower() not in keywords and operators):
            return True
        else:
            return False
    def isnumber(number):
        if (number.isdigit()):
            return True
        else:
            return False
    def iscsv(csv):
        if (re.match(csvregex,csv)):
            return True
        else:
            return False
    def sql_tokenize(string):
        """ Tokenizes a SQL statement into tokens.

        Inputs:
           string: string to tokenize.

        Outputs:
           a list of tokens.
        """
        tokens = []
        statements = sqlparse.parse(string)

        # SQLparse gives you a list of statements.
        for statement in statements:
            # Flatten the tokens in each statement and add to the tokens list.
            flat_tokens = sqlparse.sql.TokenList(statement.tokens).flatten()
            for token in flat_tokens:
                strip_token = str(token).strip()
                if len(strip_token) > 0:
                    tokens.append(strip_token)

        newtokens = []
        keep = True
        for i, token in enumerate(tokens):
            if token == ".":
                newtoken = newtokens[-1] + "." + tokens[i + 1]
                newtokens = newtokens[:-1] + [newtoken]
                keep = False
            elif keep:
                newtokens.append(token)
            else:
                keep = True

        return newtokens
    #REGEX
    identifierregex=r'^[a-zA-Z][a-zA-Z0-9]'
    numberregex=r'/^-?\d*\.?\d+$/'
    csvregex=r'.+(\.csv)$'

    #IMPORTANT LISTS
    keywords=['alter', 'asc', 'begin', 'by', 'column', 'commit', 'copy', 'create', 'database', 'delete', 'desc', 'drop', 'exclusive', 'export', 'from', 'in', 'index', 'inner', 'insert', 'integer', 'into', 'join', 'load', 'lock', 'mode', 'on', 'order', 'save', 'select', 'set', 'table', 'text', 'to', 'top', 'type', 'update', 'values', 'where', 'work']
    operators=['=','>','<','>=','<=',"<>"]
    selectoptionalkeywords=['top','order by','save']
    tokens=sql_tokenize(query)
    if tokens[0].lower() in keywords:
        #------------------------------------------CREATE--------------------------------------------#
        if tokens[0].lower()=="create":
            #------------------------------------------TABLE---------------------------------------------#
            try:
                if tokens[1].lower()=="table":
                    if isidentifier(tokens[2]):
                        if (tokens[3]=="("):
                            querybuilder=f"create_table('{tokens[2]}',"
                            i=4
                            columns=[]
                            types=[]
                            commas=0
                            while tokens[i]!=")":
                                if i%3==1:
                                    if isidentifier(tokens[i]):
                                        columns.append(tokens[i])
                                    else:
                                        return f"Invalid column name '{tokens[i]}' !"
                                elif i%3==2:
                                    if (tokens[i]=="int" or tokens[i]=="str"):
                                        types.append(tokens[i])
                                    else:
                                        return f"Invalid data type '{tokens[i]}' - must be int or str!"
                                elif i%3==0:
                                    if (tokens[i]==","):
                                        commas+=1
                                    else:
                                        return "Your forgot a comma!"
                                if tokens[i+1]==")" and len(columns)==len(types) and len(columns)==commas+1:
                                    index=i+2
                                i+=1
                            try:
                                tmp=tokens[index]
                            except:
                                return f"db.{querybuilder}{columns},{types})"
                            else:
                                if tmp!=";":
                                    return "You forgot a ';' !"
                                else:
                                    return f"db.{querybuilder}{columns},{types})"


                        else:
                            return "You forgot a '(' !"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                #---------------------------------------INDEX--------------------------------------------#
                elif tokens[1].lower()=="index":
                    if (isidentifier(tokens[2])):
                        if tokens[3].lower()=="on":
                            if (isidentifier(tokens[4])):
                                try:
                                    tmp=tokens[5]
                                except:
                                    return f"db.create_index('{tokens[4]}','Btree','{tokens[2]}')"
                                else:
                                    if tmp!=";":
                                        return "You forgot a ';' !"
                                    else:
                                        return f"db.create_index('{tokens[4]}','Btree','{tokens[2]}')"
                            else:
                                return f"Invalid table name '{tokens[4]}' !"
                        else:
                            return "You forgot the keyword 'ON' !"
                    else:
                        return f"Invalid index name '{tokens[2]}' !"

                else:
                    return f"Invalid query, a keyword must follow the command CREATE (TABLE,INDEX), you wrote {tokens[2]}"
            except:
                return f"'{query}' alone is not an sql command, valid format: CREATE TABLE name (column_1 type_1,...); or CREATE INDEX name ON table."

        #---------------------------------------DELETE--------------------------------------------#
        elif tokens[0].lower()=="delete":
            try:
                if (tokens[1].lower()=="from"):
                    if  (isidentifier(tokens[2])):
                        if (tokens[3].lower()=="where"):
                            try:
                                if (isidentifier(tokens[4]) and tokens[5] in operators and (isnumber(tokens[6]) or isidentifier(tokens[6]))):
                                    try:
                                        tmp=tokens[7]
                                    except:
                                        return f"db.delete('{tokens[2]}','{tokens[4]}{tokens[5]}{tokens[6]}')"
                                    else:
                                        if tmp!=";":
                                            return "You forgot a ';' !"
                                        else:
                                            return f"db.delete('{tokens[2]}','{tokens[4]}{tokens[5]}{tokens[6]}')"
                                else:
                                    return f"Your condition, '{tokens[4:]}' had a wrong format, right format is like '[column name][operator][number or column name]' !"
                            except:
                                return f"Your condition, '{tokens[4:]}' had a wrong format, right format is like '[column name][operator][number or column name]' !"
                        else:
                            return f"You forgot the keyword 'WHERE', instead you wrote '{tokens[3]}' !"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                else:
                    return f"Invalid query, a keyword must follow the command DELETE (FROM), you wrote '{tokens[1]}'"
            except:
                return f"'{query}' alone is not an sql command, valid format: DELETE FROM table WHERE condition."

        #-------------------------------------------------UPDATE----------------------------------------------#
        elif tokens[0].lower()=="update":
            try:
                if  (isidentifier(tokens[1])):
                    if (tokens[2].lower()=="set"):
                        try:
                            if (isidentifier(tokens[3]) and tokens[4]=="=" and (isnumber(tokens[5]) or isidentifier(tokens[5]))):
                                if  (tokens[6].lower()=="where"):
                                    if (isidentifier(tokens[7]) and tokens[8] in operators and (isnumber(tokens[9]) or isidentifier(tokens[9]))):
                                        try:
                                            tmp=tokens[10]
                                        except:
                                            return f"db.update('{tokens[1]}','{tokens[5]}','{tokens[3]}','{tokens[7]}{tokens[8]}{tokens[9]}')"
                                        else:
                                            if tmp!=";":
                                                return "You forgot a ';' !"
                                            else:
                                                return f"db.update('{tokens[1]}','{tokens[5]}','{tokens[3]}','{tokens[7]}{tokens[8]}{tokens[9]}')"
                                    else:
                                        return f"Your condition, '{tokens[7:]}' had a wrong format, right format is like '[column name][operator][number or column name]' !"
                                else:
                                    return f"You forgot the keyword 'WHERE', instead you wrote '{tokens[6]}' !"
                            else:
                                return f"Your condition, '{tokens[3:]}' had a wrong format, right format is like '[column name][=][value]' !"
                        except:
                            return f"Your condition, '{tokens[3:]}' had a wrong format, right format is like '[column name][operator][value]' or you are missing WHERE keyword !"
                    else:
                        return f"Invalid query, a keyword must follow the command UPDARE table (SET), you wrote '{tokens[2]}'"
                else:
                    return f"Invalid table name '{tokens[1]}' !"
            except:
                return f"'{query}' alone is not an sql command, valid format: UPDATE table SET column=value WHERE condition."

        #----------------------------------------------------ALTER-----------------------------------------------------------#
        elif tokens[0].lower()=="alter":
            try:
                if tokens[1].lower()=="table":
                    if  (isidentifier(tokens[2])):
                        try:
                            if (tokens[3].lower()=="alter" and tokens[4].lower()=="column"):
                                if  (isidentifier(tokens[5])):
                                    try:
                                        if (tokens[6].lower()=="type" and (tokens[7]=="int" or tokens[7]=="str")):
                                            try:
                                                tmp=tokens[8]
                                            except:
                                                return f"db.cast_column('{tokens[2]}','{tokens[5]}',{tokens[7]})"
                                            else:
                                                if tmp!=";":
                                                    return "You forgot a ';' !"
                                                else:
                                                    return f"db.cast_column('{tokens[2]}','{tokens[5]}',{tokens[7]})"
                                        else:
                                            return f"Invalid type '{tokens[7]}', or forgot to declare type str or int or missing keyword TYPE"
                                    except:
                                        return f"Invalid type '{tokens[7]}', or forgot to declare type str or int or missing keyword TYPE"
                                else:
                                    return f"Invalid column name '{tokens[5]}' !"
                            else:
                                return f"Did you mean ALTER COLUMN instead of '{tokens[3]} {tokens[4]}'"
                        except:
                            return f"You forgot the keyword 'ALTER TABLE', instead you wrote '{tokens[3]}{tokens[4]}' !"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                else:
                    return f"You forgot the keyword 'TABLE', instead you wrote '{tokens[1]}' !"
            except:
                return f"'{query}' alone is not an sql command, valid format: ALTER TABLE name ALTER COLUMN column TYPE [int/str]."

        #-------------------------------------------SAVE-----------------------------------------#
        elif tokens[0].lower()=="save":
            try:
                if tokens[1].lower()=="database":
                    if tokens[2].lower()==currentdb:
                        try:
                            tmp=tokens[3]
                        except:
                            return "db.save()"
                        else:
                            if tmp!=";":
                                return "You forgot a ';' !"
                            else:
                                return "db.save()"
                    else:
                        return "You cannot save another database while you are working with this one"
                else:
                    return f"'{query}' alone is not an sql command, valid format: SAVE DATABASE current_working_database"
            except:
                return f"'{query}' alone is not an sql command, valid format: SAVE DATABASE current_working_database"

        #---------------------------------------DROP------------------------------------------------------#
        elif tokens[0].lower()=="drop":
            try:
                if tokens[1].lower()=="database":
                    if tokens[2].lower()==currentdb:
                        try:
                            tmp=tokens[3]
                        except:
                            return "db.drop_db()"
                        else:
                            if tmp!=";":
                                return "You forgot a ';' !"
                            else:
                                return "db.drop_db()"
                    else:
                        return "You cannot drop another database while you are working with this one"
                elif tokens[1].lower()=="table":
                    if (isidentifier(token[2])):
                        try:
                            tmp=tokens[3]
                        except:
                            return f"db.drop_table('{tokens[2]}')"
                        else:
                            if tmp!=";":
                                return "You forgot a ';' !"
                            else:
                                return f"db.drop_table('{tokens[2]}')"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                elif tokens[1].lower()=="index":
                        if (isidentifier(token[2])):
                            try:
                                tmp=tokens[3]
                            except:
                                return f"db.drop_index('{tokens[2]}')"
                            else:
                                if tmp!=";":
                                    return "You forgot a ';' !"
                                else:
                                    return f"db.drop_index('{tokens[2]}')"
                        else:
                            return f"Invalid index name '{tokens[2]}' !"
                else:
                    return f"'{query}' alone is not an sql command, valid format: DROP DATABASE current_working_database OR DROP TABLE table OR DROP INDEX name"
            except:
                return f"'{query}' alone is not an sql command, valid format: DROP DATABASE current_working_database OR DROP TABLE table OR DROP INDEX name"

        #-----------------------------EXPORT-----------------------------------------#
        elif tokens[0].lower()=="export":
            try:
                if tokens[1].lower()=="table":
                    if isidentifier(tokens[2]):
                        if tokens[3].lower()=="to":
                            if iscsv(tokens[4]):
                                try:
                                    tmp=tokens[5]
                                except:
                                    return f"db.table_to_csv('{tokens[2]}','{tokens[4]}')"
                                else:
                                    if tmp!=";":
                                        return "You forgot a ';' !"
                                    else:
                                        return f"db.table_to_csv('{tokens[2]}','{tokens[4]}')"
                            else:
                                return f"Invalid csv file name '{tokens[4]}' !"
                        else:
                            return f"Invalid keyword '{tokens[3]}', did you mean 'TO' ?"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                else:
                    return f"Invalid keyword '{tokens[1]}', did you mean 'TABLE' ?"
            except:
                return f"'{query}' alone is not an sql command, valid format: EXPORT TABLE name TO csvname.csv"

        #------------------------------LOCK/UNLOCK----------------------------#
        elif (tokens[0].lower()=="lock"):
            try:
                if tokens[1].lower()=="table":
                    if isidentifier(tokens[2]):
                        try:
                            tmp=tokens[3]
                        except:
                            return f"db.lockX_table('{tokens[2]}')"
                        else:
                            if tmp!=";":
                                return "You forgot a ';' !"
                            else:
                                return f"db.lockX_table('{tokens[2]}')"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                else:
                    return f"Invalid keyword '{tokens[1]}', did you mean 'TABLE' ?"
            except:
                return f"'{query}' alone is not an sql command, valid format: LOCK TABLE table"

        elif (tokens[0].lower()=="unlock"):
            try:
                if tokens[1].lower()=="table":
                    if isidentifier(tokens[2]):
                        try:
                            tmp=tokens[3]
                        except:
                            return f"db.unlock_table('{tokens[2]}')"
                        else:
                            if tmp!=";":
                                return "You forgot a ';' !"
                            else:
                                return f"db.unlock_table('{tokens[2]}')"
                    else:
                        return f"Invalid table name '{tokens[2]}' !"
                else:
                    return f"Invalid keyword '{tokens[1]}', did you mean 'TABLE' ?"
            except:
                return f"'{query}' alone is not an sql command, valid format: UNLOCK TABLE table"

        #------------------------------------------------------------SELECT------------------------------------------------------------#
        elif (tokens[0].lower()=="select"):
            try:
                #----------------------------------------------------SELECT INNER JOIN--------------------------------------------------------#
                if (tokens[1]=='*' and "inner" in query.lower() and "where" not in query.lower()):
                    if tokens[2].lower()=='from':
                        if isidentifier(tokens[3]):
                            if (tokens[4].lower()=="inner join"):
                                if isidentifier(tokens[5]):
                                    if (tokens[6].lower()=="on"):
                                        try:
                                            if (isidentifier(tokens[7]) and (tokens[8] in operators) and (isnumber(tokens[9]) or isidentifier(tokens[9]))):
                                                try:
                                                    tmp=tokens[10]
                                                except:
                                                    return f"db.inner_join('{tokens[3]}','{tokens[5]}','{tokens[7]}{tokens[8]}{tokens[9]}')"
                                                else:
                                                    if tmp!=";":
                                                        return "You forgot a ';' !"
                                                    else:
                                                        return f"db.inner_join('{tokens[3]}','{tokens[5]}','{tokens[7]}{tokens[8]}{tokens[9]}')"
                                            else:
                                                return f"Invalid condition, you wrote '{tokens[7:]}', valid format [column][operator][value]"
                                        except:
                                            return f"Invalid condition, you wrote '{tokens[7:]}', valid format [column][operator][value]"
                                    else:
                                        return f"Invalid keyword '{tokens[6]}', did you mean 'ON'?"
                                else:
                                    return f"Invalid table name '{tokens[5]}' !"
                            else:
                                return f"Invalid keyword '{tokens[4]}', did you mean 'INNER JOIN'?"
                        else:
                            return f"Invalid table name '{tokens[3]}' !"
                    else:
                        return f"Invalid SELECT command, you wrote '{tokens[2]}', did you mean 'FROM'?"

                #------------------------------------------------------------------SELECT INNER JOIN WHERE-------------------------------------------------------------#
                elif (isidentifier(tokens[1]) and "inner" in query.lower() and "where" in query.lower()):
                    cols=[]
                    i=1
                    commas=0
                    while tokens[i].lower()!="from":
                        if i+2%2==1:
                            if isidentifier(tokens[i]):
                                cols.append(tokens[i])
                            else:
                                return f"Invalid column name '{tokens[i]}' !"
                        elif i+2%2==0:
                            if tokens[i]==',':
                                commas+=1
                            else:
                                return "Your forgot a comma!"
                        if tokens[i+1].lower()=="from" and len(cols)==commas+1:
                            index=i+1
                        i+=1
                    if (tokens[index].lower()=='from'):
                        if (isidentifier(tokens[index+1])):
                            if (tokens[index+2].lower()=="inner join"):
                                if isidentifier(tokens[index+3]):
                                    if (tokens[index+4].lower()=="on"):
                                        try:
                                            if (isidentifier(tokens[index+5]) and (tokens[index+6] in operators) and (isnumber(tokens[index+7]) or isidentifier(tokens[index+7]))):
                                                if (tokens[index+8].lower()=="where"):
                                                        try:
                                                            if (isidentifier(tokens[index+9]) and (tokens[index+10] in operators) and (isnumber(tokens[index+11]) or isidentifier(tokens[index+11]))):
                                                                tmp=tokens[index+12]
                                                                if tmp!=";" and tmp.lower() not in selectoptionalkeywords:
                                                                    return "You forgot a ';' or spelled incorrect one of the following: [ORDER BY], [TOP], [SAVE]!"
                                                                elif tmp==";":
                                                                    return f"db.inner_join('{tokens[index+1]}',{tokens[index+3]},'{tokens[index+5]}{tokens[index+6]}{tokens[index+7]}',return_object=True)._select_where({cols},'{tokens[index+9]}{tokens[index+10]}{tokens[index+11]}',return_object=True)"
                                                                else:
                                                                    top='top_k=None'
                                                                    order='order_by=None'
                                                                    asc='asc=False'
                                                                    save='save_as=None'
                                                                    for j in range(index+12,len(tokens)+1):
                                                                        try:
                                                                            if tokens[j].lower()=="top":
                                                                                try:
                                                                                    if isnumber(tokens[j+1]):
                                                                                        top='top_k='+tokens[j+1]
                                                                                    else:
                                                                                        return f"Invalid [TOP k] command"
                                                                                except:
                                                                                    return f"Invalid [TOP k] command"
                                                                        except:
                                                                            pass

                                                                    for j in range(index+12,len(tokens)+1):
                                                                        try:
                                                                            if tokens[j].lower()=="order by":
                                                                                try:
                                                                                    if isidentifier(tokens[j+1]):
                                                                                        try:
                                                                                            if tokens[j+2].lower()=="asc":
                                                                                                order='order_by='+tokens[j+1]
                                                                                                asc='asc=True'
                                                                                            else:
                                                                                                order='order_by='+tokens[j+1]
                                                                                                asc='asc=False'
                                                                                        except:
                                                                                            order='order_by='+tokens[j+1]
                                                                                            asc='asc=False'
                                                                                    else:
                                                                                        return "Invalid [ORDER BY column [asc/desc]] command"
                                                                                except:
                                                                                    return "Invalid [ORDER BY column [asc/desc]] command"
                                                                        except:
                                                                            pass

                                                                    for j in range(index+12,len(tokens)+1):
                                                                        try:
                                                                            if  tokens[j].lower()=="save" :
                                                                                try:
                                                                                    if tokens[j+1].lower()=="as" and isidentifier(tokens[j+2]):
                                                                                        save='save_as='+tokens[j+2]
                                                                                    else:
                                                                                        return f"Invalid [SAVE AS table] command"
                                                                                except:
                                                                                    return f"Invalid [SAVE AS table] command"
                                                                        except:
                                                                            pass
                                                                    if tokens[-1]==";":
                                                                        return f"db.inner_join('{tokens[index+1]}',{tokens[index+3]},'{tokens[index+5]}{tokens[index+6]}{tokens[index+7]}',return_object=True)._select_where({cols},'{tokens[index+9]}{tokens[index+10]}{tokens[index+11]}',{order},{asc},{top},{save},return_object=True)"
                                                                    else:
                                                                        return "You forgot a ';' !"

                                                            else:
                                                                return f"Invalid condition '{tokens[index+9:]}' after keyword 'WHERE' !"
                                                        except:
                                                            return f"Invalid condition '{tokens[index+9:]}' after keyword 'WHERE' !"

                                                else:
                                                    return f"Invalid keyword '{tokens[index+8]}', did you mean 'WHERE' instead?"
                                            else:
                                                return f"Invalid condition, you wrote '{tokens[index+5:index+8]}', valid format [column][operator][value]"
                                        except:
                                            return f"Invalid condition, you wrote '{tokens[index+5:index+8]}', valid format [column][operator][value]"
                                    else:
                                        return f"Invalid keyword '{tokens[index+4]}', did you mean 'ON'?"
                                else:
                                    return f"Invalid table name '{tokens[index+3]}' !"
                            else:
                                return f"Invalid keyword '{tokens[index+2]}', did you mean 'INNER JOIN'?"
                        else:
                            return f"Invalid talbe name '{tokens[index+1]}' !"
                    else:
                        return f"Invalid keyword '{tokens[index]}', did you mean 'FROM'?"

                #-----------------------------------------------------SELECT WHERE----------------------------------------------------------#
                elif ((isidentifier(tokens[1]) or tokens[1]=='*') and "inner" not in query.lower()):
                    if (tokens[1]=='*'):
                        cols='\'*\''
                        index=2
                    elif (isidentifier(tokens[1])):
                        cols=[]
                        i=1
                        commas=0
                        while tokens[i].lower()!="from":
                            if i+2%2==1:
                                if isidentifier(tokens[i]):
                                    cols.append(tokens[i])
                                else:
                                    return f"Invalid column name '{tokens[i]}' !"
                            elif i+2%2==0:
                                if tokens[i]==',':
                                    commas+=1
                                else:
                                    return "Your forgot a comma!"
                            if tokens[i+1].lower()=="from" and len(cols)==commas+1:
                                index=i+1
                            i+=1

                    if (tokens[index].lower()=='from'):
                        if (isidentifier(tokens[index+1])):
                            try:
                                tmp=tokens[index+2]
                            except:
                                return f"db.select('{tokens[index+1]}',{cols},return_object=True)"
                            else:
                                if tmp!=";" and tmp.lower()!="where":
                                    return "You forgot a ';' !"
                                elif tmp.lower()=="where":
                                    try:
                                        if (isidentifier(tokens[index+3]) and (tokens[index+4] in operators) and (isnumber(tokens[index+5]) or isidentifier(tokens[index+5]))):
                                            try:
                                                tmp=tokens[index+6]
                                            except:
                                                return f"db.select('{tokens[index+1]}',{cols},'{tokens[index+3]}{tokens[index+4]}{tokens[index+5]}',return_object=True)"
                                            else:
                                                if tmp!=";" and tmp.lower() not in selectoptionalkeywords:
                                                    return "You forgot a ';' or spelled incorrect one of the following: [ORDER BY], [TOP], [SAVE]!"
                                                elif tmp==";":
                                                    return f"db.select('{tokens[index+1]}',{cols},'{tokens[index+3]}{tokens[index+4]}{tokens[index+5]}',return_object=True)"
                                                else:
                                                    top='top_k=None'
                                                    order='order_by=None'
                                                    asc='asc=False'
                                                    save='save_as=None'
                                                    for j in range(index+6,len(tokens)+1):
                                                        try:
                                                            if tokens[j].lower()=="top":
                                                                try:
                                                                    if isnumber(tokens[j+1]):
                                                                        top='top_k='+tokens[j+1]
                                                                    else:
                                                                        return f"Invalid [TOP k] command"
                                                                except:
                                                                    return f"Invalid [TOP k] command"
                                                        except:
                                                            pass

                                                    for j in range(index+6,len(tokens)+1):
                                                        try:
                                                            if tokens[j].lower()=="order by":
                                                                try:
                                                                    if isidentifier(tokens[j+1]):
                                                                        try:
                                                                            if tokens[j+2].lower()=="asc":
                                                                                order='order_by='+tokens[j+1]
                                                                                asc='asc=True'
                                                                            else:
                                                                                order='order_by='+tokens[j+1]
                                                                                asc='asc=False'
                                                                        except:
                                                                            order='order_by='+tokens[j+1]
                                                                            asc='asc=False'
                                                                    else:
                                                                        return "Invalid [ORDER BY column [asc/desc]] command"
                                                                except:
                                                                    return "Invalid [ORDER BY column [asc/desc]] command"
                                                        except:
                                                            pass

                                                    for j in range(index+6,len(tokens)+1):
                                                        try:
                                                            if  tokens[j].lower()=="save" :
                                                                try:
                                                                    if tokens[j+1].lower()=="as" and isidentifier(tokens[j+2]):
                                                                        save='save_as='+tokens[j+2]
                                                                    else:
                                                                        return f"Invalid [SAVE AS table] command"
                                                                except:
                                                                    return f"Invalid [SAVE AS table] command"
                                                        except:
                                                            pass
                                                    if tokens[-1]==";":
                                                        return f"db.select('{tokens[index+1]}',{cols},'{tokens[index+3]}{tokens[index+4]}{tokens[index+5]}',{order},{asc},{top},{save},return_object=True)"
                                                    else:
                                                        return "You forgot a ';' !"

                                        else:
                                            return f"Invalid condition '{tokens[index+3:]}' after keyword 'WHERE' !"
                                    except:
                                        return f"Invalid condition '{tokens[index+3:]}' after keyword 'WHERE' !"

                                elif tmp==";":
                                    return f"db.select('{tokens[index+1]}','*',return_object=True)"
                        else:
                            return f"Invalid table name '{tokens[index+1]}' !"
                    else:
                        return f"Invalid keyword '{tokens[index]}' , expected FROM"
                else:
                    return "Something it's not right, maybe you forgot a comma or had an invalid column name or you have entered an incomplete query!"
            except:
                return f"'{query}' alone is not an sql command, valid format: SELECT columns/* FROM table [WHERE condition] [TOP k] [ORDER BY column] [ASC|DESC] [SAVE AS table2] OR SELECT * FROM table1 INNER JOIN table2 ON condition OR SELECT columns FROM table1 INNER JOIN table2 ON condition1 WHERE condition2 [TOP k] [ORDER BY column] [ASC|DESC] [SAVE AS table3] OR SELECT columns/* FROM table"

        else:
            return f"Invalid first keyword '{tokens[0]}', must be one of the following SELECT,INSERT,ALTER,CREATE,DELETE,SAVE,DROP,EXPORT,UPDATE,LOCK,UNLOCK"
    else:
        return f"Queries must start with a keyword, not '{tokens[0]}' !"

#GET RAW SQL CODE
raw="SELECT * from dsada;"
