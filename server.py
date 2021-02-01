from flask import Flask, redirect, url_for, render_template,request, flash
from database import Database
import os
from flask import send_from_directory
from sqlcompiler import *
import sqlparse

#This flask api-like application takes the whole miniDB project ,and by server.py,
#is posting the data from the database to the web (locally) and at the same time the queries affect your local databases.
#
#The general app runs like that:
#1)Run server.py
#
#2)Type the localhost url of the gome page: "http://127.0.0.1:5000/home", to select an existing database or to create a new one.
#You can also write the following url: http://127.0.0.1:5000/YOURDATABASE.
#YOURDATABASE can be a existing database or a new one. Either way it will either be loaded or created.
#
#3)Then you will have a textarea to run miniDB commands seperated by the ";". Else you will run into an error. Hit run and below you will get the results (if the query is a select or inner join).
#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#
#Initialize the flask app
app=Flask(__name__)
#Set an optional encryption key for the POST method where used
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#Set a list that is visible from all functions of the current existing databases
dbs=[]

@app.route("/home", methods=["POST","GET"])
def home():
    #If we are serving the page do the following
    if request.method== "GET":
        #Clear the existing databases that we go in dbs list
        dbs.clear()
        #Look up, fetch and save to dbs list all the currectly existing databases
        for i,j,y in os.walk("dbdata"):
            for p in j:
                dbs.append(p.replace("_db",""))
            break
        #Send the page with all the available databases
        return render_template("index.html",databases=dbs)
    else:
        #If we get the form data from http://127.0.0.1:5000/home do the following
        #Try to take the name of one of the existing databases
        #If it the client didn't select one of the existing or there is no existing db run the except code else load the existing
        try :
            tmp=request.form["dbselect"]
        except:
            #Check if the db already exists or not and do the appropriate loading or creating
            if request.form["dbnew"] in dbs:
                flash("Your database "+request.form["dbnew"]+" already existed, but loaded successfully.","info")
            else:
                db=Database(request.form["dbnew"],load=False)
                flash("Your database has been created successfully.")
            return redirect(url_for("client",database=request.form["dbnew"]))
        else:
            flash("Your database loaded successfully.")
            return redirect(url_for("client",database=tmp))



@app.route("/client/<database>",methods=["POST","GET"])
@app.route("/client/<database>/<name>/<headers>/<types>/<pk>/<rows>",methods=["POST","GET"])
def client(database,name=None,headers=None,types=None,pk=None,rows=None):
    #When we post the page to the client
    if request.method=="GET":
        return render_template("client.html",database=database)
    else:
        #When we get the script, load the selected database
        db= Database(database,load=True)
        #Get the script to the variable data
        data=request.form["code"]
        #Split multiple sql commands by ;
        data=sqlparse.split(data)
        for query in data:
            #For every query remove enter characters if the client changed line
            query=query.replace('\r','')
            query=query.replace('\n','')
            #At this point an sql compiler can be placed here
            #At our assignment, we just did the following:
            #1)If we have a select or inner join query (that we need to return a table) we add the miniDB command "return_object=True" at the appropriate location
            #so we can get an object from the db.query command and not a command line result
            #
            #2)If the query was drop database we redirect the client to the home Page
            #
            #3)For other commands we just run them
            try:
                command=test(query,database)
                if "db." in command:
                    if ("drop_db()" in command or "save()" in command):
                        try:
                            eval(command)
                            return redirect(url_for("home"))
                        except:
                            #If an error was raised print that error
                            flash("Something wrong with "+str(e)+" please check your database, maybe you had an incorrect spelling of a table or column2","error")
                            return redirect(url_for("client",database=database))
                    elif ("select" or "inner_join" in command):
                        try:
                            tmp=eval(command)
                            name=tmp._name
                            headers=tmp.column_names
                            types=tmp.column_types
                            pk=tmp.pk_idx
                            rows=tmp.data
                        except Exception as e:
                            #If an error was raised print that error
                            flash("Something wrong with "+str(e)+" please check your database, maybe you had an incorrect spelling of a table or column1","error")
                            return redirect(url_for("client",database=database))
                    else:
                        try:
                            eval(command)
                        except:
                            #If an error was raised print that error
                            flash("Something wrong with "+str(e)+" please check your database, maybe you had an incorrect spelling of a table or column3","error")
                            return redirect(url_for("client",database=database))
                else:
                    flash(command,"error")
                    return redirect(url_for("client",database=database))
            except:
                flash("Problem with the sql compiler","error")
                return redirect(url_for("client",database=database))
    flash("Query success","success")
    return redirect(url_for("client",database=database,name=name,headers=headers,types=types,pk=pk,rows=rows))

if __name__=="__main__":
    app.run(debug=True)
