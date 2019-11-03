import requests
import sys
import datetime
import json
import sqlite3
from random import seed
from random import randint
from flask import Flask, render_template, g, request, url_for
app = Flask(__name__)
flightInfo=[]
possibleDepartureAirports = set([])
securityTime = 0
airport = 'AUS'
address = '5002 Pineridge Dr.'
daysPrior = 0;
leavingTime = '00:00NOT WORKING'
message = 'ERROR SHOULD NOT SEE THIS'
flightTime = '0'
flightTimeMin = 0
driveTime = 0
driveTimeString = '0'
waitTimeInput = 0
security = 0
finalDate = 0

airports = ['DFW (Dallas Fort Worth)', 'JFK (Queens New York)', 'LAX (Los Angeles)', 'ORD (Orlando)']

@app.route('/', methods=['GET'])
def dropdown():
    return render_template('home.html', airports=airports)


@app.route('/home/', methods=['GET', 'POST'])
def home():
        return render_template('home.html', airports=airports)


@app.route('/leave/' , methods=['GET', 'POST'])
def leave():
    select1 = request.form.get('airports')
    select2 = request.form.get('address')
    global airport
    airport = (str(select1)[:3])
    global address
    address = (str(select2))
    print('Airport: ' + airport)
    print('Address: ' + address)
 #   return(s); # just to see what select is
    getFlightInfo()
    print(leavingTime)
    hours = driveTime/60
    min = driveTime%60
    driveTimeString = str(hours) + ' hours and ' + str(min) + ' minutes'
    return render_template('leave.html', time=leavingTime, message=message, flightTime=flightTime, driveTime=driveTimeString, security=securityTime)


@app.route("/input/" , methods=['GET', 'POST'])
def input():
    select3 = request.form.get('airports2')
    select4 = request.form.get('waittime')
    global airport
    airport = (str(select3)[:3])
    global waitTimeInput
    waitTimeInput = (str(select4))
    print('Airport: ' + airport)
    print('Wait Time: ' + waitTimeInput)
 #   return(s); # just to see what select is
    inputTime(airport,waitTimeInput)
    return render_template('home.html', airports=airports)

##########################################################


@app.route('/flightInfo', methods=['GET'])
def getFlightInfo():
    global daysPrior
    daysPrior = 0
    date = datetime.datetime.today()
    date = date.strftime('%Y-%m-%d')
    month = date[5:7]
    day = date[8:10]
    date = month + day
    #print("airport from getFlightInfo(): " + airport)
    #print("GET ACTUAL AIRPORT DEPARTURE FROM NIKITA's DROPDOWN MENU")\
    link = "https://hacktx-2019.herokuapp.com/flights?date="
    response = requests.get(link + date)

    status = response.json()
    for flight in status:
        possibleDepartureAirports.add(flight["origin"]["code"])
    print(possibleDepartureAirports)
    global flightTime
    flightTime = str(getRandomDepartureTime())
    print(flightTime)
    global driveTime
    driveTime = getDriveTime(airport)/60
    print(driveTime)
    #driveTime = driveTime.split()[0]
    print(driveTime)
    print(getLeavingTime(flightTimeMin, driveTime))

def getDriveTime(airport):
    #home = input("What is the address that you are leaving from? Please enter in the sample format: 1234 Crowdsource Avenue, Austin")
    home = "2401 Whitis Avenue"
    home = address.replace(" ", "+")
    print(home)
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=" + home + "&destinations=" + airport + "&key=AIzaSyBeT4eC2MQtTDl9vKgMxrj3uWSfMnvxAFs"
    print(url)
    response2 = requests.get(url)
    print(response2.content)
    status2 = response2.json()
    return(status2["rows"][0]["elements"][0]["duration"]["value"])

def getRandomDepartureTime():
    seed()
    time = (randint(0, 1440))
    global flightTimeMin
    flightTimeMin = time
    #math here
    hours = time/60
    minutes = time%60
#   timeToLeave = str(hours) + ":" + str(minutes)
#    hours, minutes = timeToLeave.split(":")
#    hours, minutes = int(hours), int(minutes)
    setting = "AM"
    if hours > 12:
        setting = "PM"
        hours -= 12
    elif hours == 0:
        hours = 12
        setting = "AM"
    elif hours == 12:
        setting = "PM"

    time = ("%02d:%02d " + setting) % (hours, minutes)
    return (time)

def getLeavingTime(flightTime, driveTime):
    global securityTime
    securityTime = averageWait(airport,finalDate)
    security = averageWait(airport, finalDate)
    print('flight time: ' + str(flightTime))
    print('drive time: ' + str(driveTime))
    print('security time: ' + str(securityTime))
    leavingTime = flightTime - (driveTime + securityTime + 30)
    while leavingTime < 0:
        print('while loop!')
        print(daysPrior)
        global daysPrior
        daysPrior += 1
        print(daysPrior)
        leavingTime += 1440

    print('leaving')
    print(leavingTime)
    hours = leavingTime/60
    minutes = leavingTime%60
#   timeToLeave = str(hours) + ":" + str(minutes)
#    hours, minutes = timeToLeave.split(":")
#    hours, minutes = int(hours), int(minutes)
    setting = "AM"
    if hours > 12:
        setting = "PM"
        hours -= 12
    elif hours == 0:
        hours = 12
        setting = "AM"
    elif hours == 12:
        setting = "PM"

    if daysPrior > 1:
        global message
        message = 'leave ' + str(daysPrior) + ' days prior at '
        print('leave ' + str(daysPrior) + ' days prior at ')
    elif daysPrior == 1:
        global message
        message = 'leave the previous day at '
        print('leave the previous day at ')
    else:
        global message
        message = 'leave the day of at '
        print('leave the day of at ')
    print(("%02d:%02d " + setting) % (hours, minutes))
    global leavingTime
    leavingTime = ("%02d:%02d " + setting) % (hours, minutes)
    return(("%02d:%02d " + setting) % (hours, minutes))
    #hours = leavingTime/60
    #print(hours)
    #if(hours>12):
        #hours-=12
        #hours = str(hours) + " PM"
        #print(hours)
    #minutes = leavingTime%60
    #if(minutes<10):
        #timeToLeave = str(hours) + ":0" + str(minutes)
    #else:
    #    timeToLeave = str(hours) + ":" + str(minutes)

def averageWait(code, date):
    sum = 0
    counter = 1
    for american in query_db('select * from crowdsourced'):
        if american[0] == code:
            sum += american[2]
            counter+= 1
            print american[0], 'has the date', american[2]
    sum = sum/counter
    return sum

def query_db(query, args=(), one=False):
    connection = None
    try:
      connection = sqlite3.connect(DATABASE)
      print('in try')
      print(connection)
    except Error as e:
      print(e)
      print("SQL is a bitch")
    cur = connection.execute(query, args)
    rv = cur.fetchall()
    connection.commit()
    return (rv[0] if rv else None) if one else rv

DATABASE = './american.db';

def inputTime(airport, time):
    randomMonth = str(randint(1,12))
    randomDay = str(randint(1,31))
    print(randomMonth)
    print(randomDay)
    if(int(randomMonth) < 10):
        randomMonth = '0' + str(randomMonth)
    if(int(randomDay) < 10):
        randomDay = '0' + str(randomDay)
    date = str(str(randomMonth)+randomDay)
    print(query_db("insert into crowdsourced(airport, date, waittime) values('" + airport + "','" + date + "','" + time + "')"))


def get_db():
    return connection

@app.route('/airports')
def getAllAirports():
    return possibleDepartureAirports


if __name__ == "__main__":
    #getFlightInfo()
    app.run(debug=False)
