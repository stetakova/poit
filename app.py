
from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import math
import time
import random
import MySQLdb       
import configparser as ConfigParser
import serial
async_mode = None

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

ser=serial.Serial("/dev/ttyUSB0", 9600)
read_ser=ser.readline()



def background_thread(args):
    count = 0
    dataCounter = 0
    dataList = []
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)  
    while True:
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
        else:
          A = 1
          btnV = 'null' 
        
        btnV = dict(args).get('btn_value')
        print(args)  
        socketio.sleep(2)
        count += 1
        dataCounter += 1
        print(float(ser.readline()))
        if btnV == 1:
            dataDict = {
              "x": dataCounter,
              "y": float(ser.readline())}
            dataList.append(dataDict)
        elif btnV==0:
            if len (dataList)>0:
                values = str(dataList).replace("'", "\"")
                cursor = db.cursor()
                query = "INSERT INTO graf (hodnoty) VALUES ('%s')" % (values)
                cursor.execute(query)
                db.commit()
            
                fo = open("static/files/test.txt","a+")
                fo.write("%s\r\n" %values)
                fo.close()
                
            dataCounter = 0
            dataList = []
              
        if btnV==1:
            print(btnV)
            socketio.emit('my_response',
                      {'data': float(ser.readline()), 'count': count},
                      namespace='/test')
                  
    db.close()
 
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
  
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']
    ser.write(str(message['value']).encode())
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  cursor.execute("SELECT hodnoty FROM  graf WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])

@app.route('/read/<string:num>', methods=['GET', 'POST'])
def readmyfile(num):
    fo = open("static/files/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    #emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_eventStart', namespace='/test')
def db_message(message):   
    session['btn_value'] = 1


@socketio.on('click_eventStop', namespace='/test')
def db_message(message):   
    session['btn_value'] = 0
    

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)