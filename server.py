from flask import Flask, redirect, url_for, render_template,request, flash
from database import Database
import os
from flask import send_from_directory


app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
dbs=[]
@app.route("/home", methods=["POST","GET"])
def home():
    if request.method== "GET":
        dbs.clear()
        for i,j,y in os.walk("dbdata"):
            for p in j:
                dbs.append(p.replace("_db",""))
            break
        return render_template("index.html",databases=dbs)
    else:
        if (request.form["dbnew"]!= ""):
            if request.form["dbnew"] in dbs:
                flash("Your database "+request.form["dbnew"]+" already existed, but loaded successfully.","info")
            else:
                flash("Your database has been created successfully.")
            return redirect(url_for("client",database=request.form["dbnew"]))
        else:
            flash("Your database loaded successfully.")
            return redirect(url_for("client",database=request.form["dbselect"]))



@app.route("/client/<database>",methods=["POST","GET"])
@app.route("/client/<database>/<name>/<headers>/<types>/<pk>/<rows>",methods=["POST","GET"])
def client(database,name=None,headers=None,types=None,pk=None,rows=None):
    if request.method=="GET":
        return render_template("client.html",database=database)
    else:
        db= Database(database,load=True)
        data=request.form["code"]
        data=data.split(";")
        for query in data:
            query=query.replace('\r','')
            query=query.replace('\n','')
            try:
                if ("select" in query):
                    query.replace(')','return_object=True)')
                    tmp=eval("db"+"."+query)
                    name=tmp._name
                    headers=tmp.column_names
                    types=tmp.column_types
                    pk=tmp.pk_idx
                    rows=tmp.data
                elif("inner_join" in query):
                    query.replace(')','return_object=True)',1)
                    print(query)
                    tmp=eval("db"+"."+query)
                    name=tmp._name
                    headers=tmp.column_names
                    types=tmp.column_types
                    pk=tmp.pk_idx
                    rows=tmp.data
                elif (query=="drop_db()"):
                    return redirect(url_for("home"))
                else:
                    eval("db"+"."+query)

            except Exception as e:
                flash(str(e),"error")
                return redirect(url_for("client",database=database))

    return redirect(url_for("client",database=database,name=name,headers=headers,types=types,pk=pk,rows=rows))

if __name__=="__main__":
    app.run(debug=True)
