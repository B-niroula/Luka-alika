import sqlite3
import qrcode
import json
from flask import Flask, render_template, request, send_file, url_for,redirect,session
from datetime import datetime, timedelta
from PIL import Image
import base64
import io
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Response



app = Flask(__name__)  
app.secret_key = "Lanjio"
rand_list = []

def db_connection(): #database connection
    conn = None
    try: 
        conn = sqlite3.connect("project.sqlite") 
    except sqlite3.error as e: 
        print(e) 
    return conn  


@app.route('/') 
def index():
    if not session.get('loggedIn'):
        return render_template("landingpage.html") 
    return redirect(url_for('homepage'))

@app.route('/home')
def homepage():
    if not session.get('loggedIn'):
        return redirect(url_for('index'))
    if session.get('loggedIn') == 'hospital':
        return redirect(url_for('LoginHospital'))
    if session.get('loggedIn') == 'visitor':
        return redirect(url_for('vistname'))
    if session.get('loggedIn') == 'place':
        return redirect(url_for('Agent'))
    if session.get('loggedIn') == 'agent':
        return redirect(url_for('LoginAgent'))
    return 'you are not supposed to be here'

@app.route('/Agent', methods=['GET','POST'])
def LoginAgent(): #login function for Agent    
        if session.get('loggedIn'):
            if session.get('loggedIn') == 'agent':
                search_id = request.args.get('search', '-1') 
                if not search_id.isnumeric():
                    search_id = -1
                return render_template('agent_portal.html', data=getAllUsers(search_id))
            else:
                return redirect(url_for('index'))
        else:
            conn = db_connection() 
            cursor = conn.cursor() 
            if request.method == "POST":
                agnt_username = request.form["username"] 
                agnt_password = request.form["password"]  
                statement = f"SELECT * from Agent WHERE username='{agnt_username}' AND password='{agnt_password}';"
                cursor.execute(statement)
                user = cursor.fetchone() 
                if user:
                    session['loggedIn'] = 'agent'
                    session['email'] = agnt_username
                    return render_template('agent_portal.html', data=getAllUsers())
                else: 
                    return render_template("Loginagency.html", invalid_credentials=True)  
            return render_template("Loginagency.html")

@app.route('/agent_dashboard')
def showAgentDashboard():
    if session.get('loggedIn') == 'agent':
        return render_template('agent_dashboard.html', data=getCoronaDataForVisualization())
    else:
        return redirect(url_for('index'))


#added                ----------------- ------------------
@app.route('/hospital_request',methods=['GET','POST'])
def showhospitalRequest():
    if session.get('loggedIn') == 'agent':
        return render_template('hospital_request.html', data=getAllHospitals())
    else:
        return redirect(url_for('index'))

#all users data show
@app.route('/allusers',methods=['GET','POST'])
def showallusers():
    if session.get('loggedIn') == 'agent':
        return render_template('all_users.html', data=getUsers())
    else:
        return redirect(url_for('index'))

def getUsers(searchID = -1):
    conn = db_connection()   
    cursor = conn.cursor()
    statement = f'SELECT * FROM Visitor;'
    cursor.execute(statement)
    users = cursor.fetchall()
    users = [list(user) for user in users]
    return users

#all places data show
@app.route('/allplaces',methods=['GET','POST'])
def showallplaces():
    if session.get('loggedIn') == 'agent':
        return render_template('all_places.html', data=getPlaces())
    else:
        return redirect(url_for('index'))

def getPlaces(searchID = -1):
    conn = db_connection()   
    cursor = conn.cursor()
    statement = f'SELECT * FROM Place;'
    cursor.execute(statement)
    users = cursor.fetchall()
    users = [list(user) for user in users]
    return users

#all hospitals data show
@app.route('/allhospitals',methods=['GET','POST'])
def showallhospitals():
    if session.get('loggedIn') == 'agent':
        return render_template('all_hospitals.html', data=getHospital())
    else:
        return redirect(url_for('index'))

def getHospital(searchID = -1):
    conn = db_connection()   
    cursor = conn.cursor()
    statement = f'SELECT * FROM Hospital;'
    cursor.execute(statement)
    users = cursor.fetchall()
    users = [list(user) for user in users]
    return users




#added                ----------------- ------------------
def getAllHospitals(searchID = -1):
    conn = db_connection()   
    cursor = conn.cursor()
    statement = f'SELECT * FROM Hospital_approval;'
    cursor.execute(statement)
    users = cursor.fetchall()
    users = [list(user) for user in users]
    return users

#Getting the person whos contacts are supposed to be traced
@app.route('/trace/<int:id>', methods=['GET'])
def trace(id):
    #checking if the logged in user is actually an agent
    if session.get('loggedIn') == 'agent':
        return render_template('agent_trace.html', data=getSubjectData(id))
    else:
        return redirect(url_for('index'))
    
#Executing the Trace. Due to the high complexity of this here a explenation how it works:
#This function starts with getting the data of the subject, which is the persons whos contacts are being traced. This person is always positive. Else it would not be able to trace his or her contacts.
#The actual trace start with the comment "STARTING THE TRACE"
#Fist we get all the places that were visited by our subject, and filter them such that only those are concidered which happend in the last two weeks
#Second we get all other people that visited the same place
#Third we look at every possible combination of visits of our subject and other users. This is done in a function for more explenation consult the comments of the funnction
#We then take the resulting data and find the actual data of the subject. This is necessary as a agent needs to contact possible contact persons
#This data is then filtered by removing duplicates and finally added to our json which is send to the frontend

def helper_1():
    data = {
        "subjectData": 0,
        "arrayOfContacts": []
    }
    return data

def getSubjectData(id):

    data = helper_1

    conn = db_connection()
    cursor = conn.cursor()
    
    #get data from person whos contacts are being taced
    statement = f'SELECT * FROM Visitor WHERE citizen_id = {id}'
    cursor.execute(statement)
    subject = cursor.fetchall()

    subject = [list(user) for user in subject]

    statement = f'SELECT COUNT(*) FROM Visiting WHERE citizen_id={subject[0][0]}'
    cursor.execute(statement)
    n_visits = cursor.fetchone()[0]

    subject[0].append(n_visits)

    data["subjectData"] = subject
    

    #start the trace

    #get all places visited by subject
    statement = f'SELECT * FROM Visiting WHERE citizen_id = {id}'
    cursor.execute(statement)
    placesVisitedBySubject = cursor.fetchall()
    print("All visits conducted by our subject:")
    print(placesVisitedBySubject)


    #filter to only get places thet were visited in the last two weeks
    for i in placesVisitedBySubject:
        if dateTwoWeeksAgo(i[4]):
            placesVisitedBySubject.remove(i)
    print("All visits conduncted by our subject in the last 2 weeks")
    print(placesVisitedBySubject)

    #get all people that also visited the place 
    usersThatVisitedSamePlace = []
    for i in placesVisitedBySubject:
        statement = f'SELECT * FROM Visiting WHERE citizen_id <> {id} AND place_id = {i[2]}'
        cursor.execute(statement)
        for j in cursor.fetchall():
            usersThatVisitedSamePlace.append(j)
    print("All visits to the same place as our subject")
    print(usersThatVisitedSamePlace)

    #Checking every possible intersection of visits by the subject and other users
    contacts = []
    for j in placesVisitedBySubject:
        print(j)
        for i in usersThatVisitedSamePlace:
            print(i)
            if inTheSameTimeFrame(i, j):
                contacts.append(i)
    print("Visits that are overlapping are:")
    print(contacts)

    #Get data of each visit intersection
    result = []
    for i in contacts:
        print(i)
        statement = f'SELECT * FROM Visitor WHERE citizen_id = {i[1]}'
        cursor.execute(statement)
        result.append(cursor.fetchall()[0])
    print("The data of those that were at the same place at the same time as our subject is(This can still include duplicates):")
    print(result)

    #Now we remove all the duplicates
    result = list(dict.fromkeys(result))
    print("The data of those that were at the same place at the same time as our subject is:")
    print(result)
    
    #We now add the number of visits that were done by each contact of our subject
    result = [list(user) for user in result]
    for user in result: 
        statement = f'SELECT COUNT(*) FROM Visiting WHERE citizen_id={user[0]};'
        cursor.execute(statement)
        n_visits = cursor.fetchone()[0]
        user.append(n_visits)
    print("The final results with the number of visits is:")
    print(result)

    #We add our findings to our JSON such that it can be send to the frontend and displayed
    data["arrayOfContacts"] = result
    print("The data that is being send to the frontend is:")
    print(data)
    
    return data

#We exclude visits before two weeks ago by suptracting two weeks and then comparing the two time stamps
def dateTwoWeeksAgo(arrivalTime):
    arrivalTime = datetime.fromisoformat(arrivalTime)
    currentDate = datetime.now()
    currentDateTwoWeeksAgo = currentDate - timedelta(weeks = 2)
    return(currentDateTwoWeeksAgo > arrivalTime)

#This function compares two visits and determines if they overlap
def inTheSameTimeFrame(visitToTheSamePlace, placeVisitedBySubject):
    #Printing of the data can be used for further debugging
    # print("================")
    # print("the place visited by the other person")
    # print(visitToTheSamePlace[2])
    visitorToTheSamePlacePlace = visitToTheSamePlace[2]
    # print("the arrival time of the other person:")
    # print(visitToTheSamePlace[3])
    visitorToTheSamePlaceArrivalTime = datetime.fromisoformat(visitToTheSamePlace[3])
    # print("the exit time of the other person")
    # print(visitToTheSamePlace[4])
    visitorToTheSamePlaceExitTime = datetime.fromisoformat(visitToTheSamePlace[4])
    # print("the place visitd by our subject person")
    # print(placeVisitedBySubject[2])
    placeVisitedByTheSubject = placeVisitedBySubject[2]
    # print("the arrival time of our subject person")
    #print(placeVisitedBySubject[3])
    arrivalTimeOfTheSubject = datetime.fromisoformat(placeVisitedBySubject[3])
    # print("the exit time of our subject person")
    #print(placeVisitedBySubject[4])
    exitTimeOfTheSubject = datetime.fromisoformat(placeVisitedBySubject[4])
    
    #Actual comparison of the two visits
    #First checking if they were at the same place
    if visitorToTheSamePlacePlace != placeVisitedByTheSubject:
        return False
    #THen checking if they were in the same timeframe
    else:
        if visitorToTheSamePlaceExitTime > arrivalTimeOfTheSubject and exitTimeOfTheSubject > visitorToTheSamePlaceArrivalTime:
            return True
        else:
            return False


@app.route('/contact-tracing', methods=['GET','POST'])
def contactTracing(): #login function for Agent    
        if session.get('loggedIn'):
            if session.get('loggedIn') == 'agent':
                search_id = request.args.get('search', '-1') 
                if not search_id.isnumeric():
                    search_id = -1
                return render_template('agent_contactTracing.html', data=getAllPositiveUsers(search_id))
            else:
                return redirect(url_for('index'))
      
@app.route('/plot')
def getPlot():
    fig = getCoronaPlot()
    buffer = io.BytesIO()
    FigureCanvas(fig).print_png(buffer)
    return Response(buffer.getvalue(), mimetype='image/png')

@app.route('/Hospital', methods=['GET','POST']) 
def LoginHospital(): #Login function for Hospital
        conn = db_connection() 
        cursor = conn.cursor()
        if session.get('loggedIn'):
            if session.get('loggedIn') == 'hospital':
                vist_search = request.args.get('search', '').lower()
                sql = f"SELECT citizen_id, visitor_name,email, phone_number, address, infected from Visitor WHERE lower(visitor_name)='{vist_search}' OR citizen_id='{vist_search}';"  
                cursor.execute(sql)  
                data = cursor.fetchall()  
                return render_template("hospital_portal.html", data=data) 
            else:
                return redirect(url_for('index'))
        else:
            if request.method == "POST": 
                Hsptl_id = request.form["id"]
                Hsptl_username = request.form["username"] 
                Hsptl_password = request.form["password"]  
                statement = f"SELECT * from Hospital WHERE hospital_id='{Hsptl_id}' AND username='{Hsptl_username}' AND password='{Hsptl_password}';"
                cursor.execute(statement)
                user = cursor.fetchone() 
                if user: 
                    session['loggedIn'] = 'hospital'
                    session['email'] = Hsptl_username
                    return render_template("hospital_portal.html") 
                else: 
                    return render_template("hospitalLogin.html", invalid_credentials=True)
            return render_template("hospitalLogin.html")

@app.route('/HospitalRegister', methods=['GET','POST']) 
def RegisterHospital(): #Login function for Hospital
    conn = db_connection() 
    cursor = conn.cursor()
    if request.method == "POST":
        Hsptl_id = request.form["id"]
        Hsptl_username = request.form["username"] 
        Hsptl_password = request.form["password"]  
        statement = f"INSERT INTO Hospital_approval(hospital_id,username,password) VALUES('{Hsptl_id}','{Hsptl_username}','{Hsptl_password}');"
        cursor.execute(statement)
        conn.commit()
        return redirect(url_for('index'))
    else:
        return render_template("hospitalRegister.html")

@app.route('/HospitalReq', methods=['GET'])
def HospitalReq():
    conn = db_connection() 
    cursor = conn.cursor()
    accept = request.args.get("state")
    Hsptl_id = request.args.get("id")
    Hsptl_username = request.args.get("username")
    Hsptl_password = request.args.get("password")
    statement = f"DELETE FROM Hospital_approval WHERE hospital_id='{Hsptl_id}' AND username='{Hsptl_username}' AND password='{Hsptl_password}';"
    cursor.execute(statement)
    conn.commit()
    if (accept=='1'):
        statement = f"INSERT INTO Hospital(hospital_id,username,password) VALUES('{Hsptl_id}','{Hsptl_username}','{Hsptl_password}');"
        cursor.execute(statement)
        conn.commit()
    return redirect(url_for('LoginAgent'))



@app.route('/Visitor', methods=['POST', 'GET']) 
def vistname():   
    if session.get('loggedIn'):
            if session.get('loggedIn') == 'visitor':
                if isCheckedIn(session.get('userID')):
                    return render_template('visitor_portal.html', citizen_id=session.get('userID'), checkedIn=True, username=getVisitorInfo(session.get('userID'))[1], covidStatus='Positive' if getVisitorCovidStatus(session.get('userID')) else 'Negative')
                else:
                    return render_template('visitor_portal.html', citizen_id=session.get('userID'), username=getVisitorInfo(session.get('userID'))[1], covidStatus='Positive' if getVisitorCovidStatus(session.get('userID')) else 'Negative')
            else:
                return redirect(url_for('index'))
    else:
        conn = db_connection() 
        cursor = conn.cursor() 
        if request.method == "POST":
            vist_email = request.form["email"] 
            vist_password = request.form["password"]  
            statement = f"SELECT * from Visitor WHERE email='{vist_email}' AND password='{vist_password}';"
            cursor.execute(statement)    
            user = cursor.fetchone()
            if user: 
                session['loggedIn'] = 'visitor'
                session['vist_email'] = vist_email
                session['userID'] = user[0]
                return redirect(url_for('vistname'))
            else: 
                return render_template("loginVisitor.html", invalid_credentials=True) 
        else: 
            return render_template("loginVisitor.html")

@app.route('/Place', methods=['POST', 'GET'])
def Place():
    if session.get('loggedIn'):
            if session.get('loggedIn') == 'place':
                return render_template('place_portal.html', data=getCheckedInAtPlace(session.get('userID')))
            else:
                return redirect(url_for('index'))
    else:
        conn = db_connection() 
        cursor = conn.cursor() 
        if request.method == "POST":
            place_email = request.form["email"] 
            place_password = request.form["password"]  
            statement = f"SELECT * from Place WHERE email='{place_email}' AND password='{place_password}';"
            cursor.execute(statement)    
            user = cursor.fetchone()
            if user: 
                session['loggedIn'] = 'place'
                session['email'] = place_email
                session['userID'] = user[0]
                return redirect(url_for('Place'))
            else: 
                return render_template("loginPlace.html", invalid_credentials=True) 
        else: 
            return render_template("loginPlace.html")


@app.route('/logout')
def logout():
    session['loggedIn'] = None
    session['email'] = None
    session['userID'] = None
    return redirect(url_for('index'))

@app.route('/register',methods=['POST','GET']) 
def register():  #Register for visitors
    if not session.get('loggedIn'):
        conn = db_connection()   
        cursor = conn.cursor()  
        if request.method == "POST":   
            vist_name = request.form["Vorname"]  
            vist_email = request.form["email"] 
            vist_phone = request.form["phone"] 
            vist_add = request.form["address"] 
            vist_pass = request.form["password"] 
            sql = """INSERT INTO Visitor (visitor_name,email,phone_number,address,password,infected) VALUES(?,?,?,?,?,?)""" 
            cursor = cursor.execute(sql,(vist_name,vist_email,vist_phone,vist_add,vist_pass, 0)) 
            conn.commit() 
            return render_template('success_visitor_reg.html')   
        return render_template("Registerpagev.html")  
    else:
        return redirect(url_for('index'))

@app.route('/pregister', methods=['POST','GET'])
def pregister():   #place registration
    if not session.get('loggedIn'):
        conn = db_connection()   
        cursor = conn.cursor() 
        if request.method == "POST":  
            try:
                place_name = request.form["place_name"]  
                place_phone = request.form["number"] 
                place_add = request.form["address"]
                place_email = request.form["email"] 
                place_password = request.form["password"]  
                sql = """INSERT INTO Place(place_name,email,password,phone_number,address) VALUES(?,?,?,?,?)""" 
                cursor = cursor.execute(sql,(place_name, place_email, place_password, place_phone, place_add)) 
                conn.commit()  
                return redirect(url_for('index'))
            except Exception as e:
                print(e) 
                return 'Error'
        return render_template("PlaceRegistration.html") 
    else:
        return redirect(url_for('index'))

@app.route('/QRcode')
def displayQR():
    if session.get('loggedIn') == 'place':
        vist_qr = '/visit/'+str(session.get('userID'))
        img = qrcode.make(vist_qr) #qr code generated 
        data = io.BytesIO()
        img.save(data, "JPEG")
        encoded_image_data = base64.b64encode(data.getvalue())
        return render_template('qr_code.html', image=encoded_image_data.decode('utf-8'))
    else:
        return redirect(url_for('index'))

def GenerateQR(placeID):
    vist_qr = '/visit/'+str(placeID)
    img = qrcode.make(vist_qr) #qr code generated 
    data = io.BytesIO()
    img.save(data, "JPEG")
    encoded_image_data = base64.b64encode(data.getvalue())

def getVisitorCovidStatus(id):
    conn = db_connection()   
    cursor = conn.cursor() 
    statement = f'SELECT infected FROM Visitor WHERE citizen_id={id};'
    cursor.execute(statement)
    user = cursor.fetchone()
    return user[0]

@app.route('/visit/<int:placeID>', methods=['POST', 'GET'])
def visitPlace(placeID):
    if session.get('loggedIn') == 'visitor':
        if isCheckedIn(session.get('userID')):
            return 'Already checked in'
        else:
            conn = db_connection() 
            cursor = conn.cursor()
            statement = f"""INSERT INTO Visiting (citizen_id, place_id, check_in_time) VALUES ({session.get('userID')}, {placeID}, '{datetime.now()}'); UPDATE Visitor SET checked_in=1 WHERE citizen_id={session.get('userID')};"""
            cursor.executescript(statement)
            conn.commit()
            return 'done'
    else:
        """ return render_template('ErrorVisiting.html') """
        return 'error' 

def isCheckedIn(id):
    conn = db_connection() 
    cursor = conn.cursor()
    statement = f'SELECT checked_in FROM Visitor WHERE citizen_id={id}'
    cursor.execute(statement)
    checked = cursor.fetchone()
    return bool(checked[0])

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if session.get('loggedIn') == 'visitor':
        conn = db_connection() 
        cursor = conn.cursor()
        statement = f"SELECT visiting_id FROM Visiting WHERE citizen_id={session.get('userID')} AND check_out_time IS NULL;"
        cursor.execute(statement)
        rows = cursor.fetchone()
        if rows:
            statement = f"""UPDATE Visiting SET check_out_time="{datetime.now()}" WHERE citizen_id={session.get("userID")};; UPDATE Visitor SET checked_in=0 WHERE citizen_id={session.get("userID")};"""
            cursor.executescript(statement)
            conn.commit()
            return redirect(url_for('vistname'))
        else:
            return redirect(url_for('vistname', error='Not Checked In'))
    else:
        """ return render_template('ErrorVisiting.html') """
        return redirect(url_for('index', error='Not Logged In As a Visitor'))

@app.route('/imprint')
def imprint(): #imprint
    return render_template("imprint.html")    

@app.route('/append',methods=['POST'])
def append(): #function to edit the infected
    conn = db_connection()   
    cursor = conn.cursor() 
    if request.method == "POST":  
        vist_id = request.form["id"] 
        vist_inf = request.form["Infected"]  #infected 0 being false and 1 being true
        stat = f"SELECT * from Visitor WHERE citizen_id='{vist_id}';" #updating the infected the value infected
        cursor.execute(stat) 
        value = cursor.fetchone()
        if (int(vist_inf) == 1 or int(vist_inf) == 0) and value != None:  #checking for valif id and infected value
            cursor.execute("UPDATE Visitor SET infected = ?\
                            WHERE citizen_id = ?",
                        (vist_inf, vist_id))
            conn.commit()  
            return redirect(url_for('LoginHospital', search = vist_id), code = 307) 
        else:  
            return "Infected should be between 0 and 1 or wrong id"
    else: 
        return redirect(url_for('LoginHospital')) 

@app.route('/getPlaceInfo/<int:id>', methods=['GET'])
def getPlaceInfo(id):
    conn = db_connection()   
    cursor = conn.cursor() 
    statement = f'SELECT * FROM Place WHERE place_id={id};'
    cursor.execute(statement)
    user = cursor.fetchone()
    return json.dumps(user)

def getVisitorInfo(id):
    conn = db_connection()   
    cursor = conn.cursor() 
    statement = f'SELECT * FROM Visitor WHERE citizen_id={id};'
    cursor.execute(statement)
    user = cursor.fetchone()
    return user

@app.route('/checkedInPlaceInfo', methods=['GET'])
def getCheckedInPlaceInfo():
    if session.get('loggedIn') == 'visitor':
        conn = db_connection()   
        cursor = conn.cursor() 
        statement = f'SELECT Visiting.visiting_id, Visiting.citizen_id, Visiting.place_id, Place.place_name, Visiting.check_in_time, Visiting.check_out_time FROM Visiting INNER JOIN Visitor ON Visiting.citizen_id = Visitor.citizen_id INNER JOIN Place ON Visiting.place_id = Place.place_id WHERE Visiting.citizen_id={session.get("userID")} AND Visiting.check_out_time IS NULL;'
        cursor.execute(statement)
        user = cursor.fetchone()
        return json.dumps(user)
    else:
        return 'You are not logged in as a visitor'

def getCheckedInAtPlaceALL(placeID):
    conn = db_connection()   
    cursor = conn.cursor() 
    statement = f'SELECT Visitor.visitor_name, Visitor.email, Visiting.check_in_time, Visiting.check_out_time, Visitor.infected FROM Visiting INNER JOIN Visitor ON Visiting.citizen_id = Visitor.citizen_id INNER JOIN Place ON Visiting.place_id = Place.place_id WHERE Visiting.place_id={placeID};'
    cursor.execute(statement)
    users = cursor.fetchall()
    return users

def getCheckedInAtPlace(placeID):
    conn = db_connection()   
    cursor = conn.cursor() 
    statement = f'SELECT Visitor.visitor_name, Visitor.email, Visiting.check_in_time, Visitor.infected FROM Visiting INNER JOIN Visitor ON Visiting.citizen_id = Visitor.citizen_id INNER JOIN Place ON Visiting.place_id = Place.place_id WHERE Visiting.place_id={placeID} AND Visiting.check_out_time IS NULL;'
    cursor.execute(statement)
    users = cursor.fetchall()
    return users
def getCoronaPlot():
    conn = db_connection()
    cursor = conn.cursor()

    statement = f'SELECT COUNT(infected) From Visitor WHERE infected = 1'
    cursor.execute(statement)
    numberOfCurrentlyPositive = cursor.fetchall()[0][0]

    statement = f'SELECT COUNT(infected) From Visitor WHERE infected = 0'
    cursor.execute(statement)
    numberOfCurrentlyNegative = cursor.fetchall()[0][0]

    pieLabels = ["Positive", "Negative"]

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])

    pies = ax.pie([numberOfCurrentlyPositive,numberOfCurrentlyNegative], labels = pieLabels)

    return fig


def getCoronaDataForVisualization():
    conn = db_connection()
    cursor = conn.cursor()
    data = {
        "numberOfCurrentlyPositive": 0,
        "numberOfCurrentlyNegative": 0,
        "totalNumberOfVisitors": 0
        }

    statement = f'SELECT COUNT(infected) From Visitor WHERE infected = 1'
    cursor.execute(statement)
    numberOfCurrentlyPositive = cursor.fetchall()[0][0]
    data["numberOfCurrentlyPositive"] = numberOfCurrentlyPositive


    statement = f'SELECT COUNT(infected) From Visitor WHERE infected = 0'
    cursor.execute(statement)
    numberOfCurrentlyNegative = cursor.fetchall()[0][0]
    data["numberOfCurrentlyNegative"] = numberOfCurrentlyNegative

    statement = f'SELECT COUNT(citizen_id) FROM Visitor'
    cursor.execute(statement)
    totalNumberOfVisitors = cursor.fetchall()[0][0]
    data["totalNumberOfVisitors"] = totalNumberOfVisitors

    return data

def getAllUsers(searchID = -1):
    conn = db_connection()   
    cursor = conn.cursor()
    if searchID == -1: 
        statement = f'SELECT * FROM Visitor;'
    else:
        statement = f'SELECT * FROM Visitor WHERE citizen_id={searchID};'
    cursor.execute(statement)
    users = cursor.fetchall()
    users = [list(user) for user in users]
    for user in users: 
        statement = f'SELECT COUNT(*) FROM Visiting WHERE citizen_id={user[0]};'
        cursor.execute(statement)
        n_visits = cursor.fetchone()[0]
        user.append(n_visits)
    return users

def getAllPositiveUsers(searchID = -1):
    conn = db_connection()
    cursor = conn.cursor()
    if searchID == -1:
        statement = f'SELECT * FROM Visitor WHERE infected = 1'
    else:
        statement = f'SELECT * FROM Visitor WHERE infected = 1 AND citizen_id ={searchID}'

    cursor.execute(statement)
    positiveUsers = cursor.fetchall()

    positiveUsers = [list(user) for user in positiveUsers]

    for user in positiveUsers:
        statement = f'SELECT COUNT(*) FROM Visiting WHERE citizen_id={user[0]}'
        cursor.execute(statement)
        n_visits = cursor.fetchone()[0]
        user.append(n_visits)
    return positiveUsers

if __name__ == "__main__": 
    app.run(debug=True) 
    