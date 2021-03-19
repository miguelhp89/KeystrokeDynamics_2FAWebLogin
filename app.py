#!/usr/bin/python3
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from CaptureTimeWeb import CaptureTimeWeb
import pyxhook
from KeystrokeMLWeb import KeystrokeMLWeb
import time
from KeystrokeMLWeb import KeystrokeMLWeb
import logging
import datetime
import syslog


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        #self.multifactor = multifactor  #MH

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='mhermozap', password='.tie5Roanl'))
users.append(User(id=2, username='s040', password='.tie5Roanl'))
users.append(User(id=3, username='s026', password='.tie5Roanl'))
logging.basicConfig(filename="logfilename.log", level=logging.INFO)

pred = KeystrokeMLWeb()
capTime = CaptureTimeWeb()
capTime.CreateDicTimes()
hookman = pyxhook.HookManager()
hookman.KeyDown = capTime.KeyDownEvent
hookman.KeyUp = capTime.KeyUpEvent
hookman.HookKeyboard()
hookman.start()

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " Loggin process started!")
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        multifactor = request.form.get('multifactor') #MH
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password: #MH: First Factor evaluation
            print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " First Auth Factor: User and Password verified!")
            if multifactor == "multifactor": #MH
                capTime.CalculateKeystrokesDynamics() #MH

                y_pred = pred.predictFromFile('./00_weblogin/output/HardcodeUser_timings.csv') #MH
                print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " ML Classification Model Result (y_pred): ", y_pred) #MH
                print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " User Account Entered: ", user.username) #MH
                if y_pred == user.username: #MH: Second Factor evaluation
                    print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " ML Classification Model Result IS EQUAL to Entered Account!") #MH
                    print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " Access Granted!") #MH
                    msg = " , event: login , result: successful , type: legitimate , user input:" + user.username + " , user predicted: " + y_pred + " , message: (F1) User and Password verified correctly. (F2) User Input and User Predicted are equal" #MH
                    syslog.syslog((syslog.LOG_INFO | syslog.LOG_LOCAL0), msg) #MH
                    session['user_id'] = user.id 
                    return redirect(url_for('multifactor')) #MH
                else:
                    print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " ML Classification Model Result IS NOT EQUAL to Entered Account!") #MH
                    print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " Access Denied!") #MH
                    msg = " , event: login , result: fail , type: illegitimate , user input:" + user.username + " , user predicted: " + y_pred + " , message: (F1) User and Password verified correctly. (F2) User Input and User Predicted are not equal"  #MH
                    syslog.syslog((syslog.LOG_INFO | syslog.LOG_LOCAL0), msg) #MH
            else: #MH
                session['user_id'] = user.id 
                return redirect(url_for('profile'))               
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')

@app.route('/multifactor')
def multifactor():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('multifactor.html')



#para que la aplicación se mantenga escuchando siempre
if __name__=='__main__':
    app.run(debug=True)