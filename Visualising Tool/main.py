import pyrebase 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, session, render_template, request, redirect ,jsonify
import re 


app=Flask(__name__,template_folder='template')

# config={
#   "apiKey": "AIzaSyC0aEymSwOknoaBuMIYPrzU_JRLXmJF0dU",
#   "authDomain": "se-test-7f7e1.firebaseapp.com",
#   "databaseURL": "https://se-test-7f7e1-default-rtdb.firebaseio.com",
#   "projectId": "se-test-7f7e1",
#   "storageBucket": "se-test-7f7e1.appspot.com",
#   "messagingSenderId": "985296505745",
#   "appId": "1:985296505745:web:b9fdeef8283aed7d7ea830",
#   "measurementId": "G-RENMCQBYJW"
# }


# firebase=pyrebase.initialize_app(config)
# auth=firebase.auth()
# database=firebase.database() 

app.secret_key='secret'
cred = credentials.Certificate('se-test-7f7e1-firebase-adminsdk-auhlb-6adf0cbd2c.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://se-test-7f7e1-default-rtdb.firebaseio.com"
})


# Define the Firebase Realtime Database reference
ref = db.reference('Users')

def extract_roll_number(email):
    if '20' in email:
        se = re.sub(r'^(.*?)20', 'se20', email)
        roll_number_match = re.search(r'^[^@]+', se)
    else:
        roll_number_match = re.search(r'^[^@]+', email)

    if roll_number_match:
        roll_number = roll_number_match.group(0)
    else:
        roll_number = None

    return roll_number

def extraction(email):
    year_match = re.search(r'\d+', email)
    if year_match:
        year = year_match.group(0)
    else:
        year = None

    # Extract the branch using the regular expression pattern
    branch_match = re.search(r'\d+(.*?)\d+', email)
    if branch_match:
        branch = branch_match.group(1)
    else:
        branch = None

    return year, branch



@app.route('/signup', methods=['POST','GET'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('pass')
    confirm_password = request.form.get('cpass')
    year,branch= extraction(email)
    rollNo=extract_roll_number(email)

    #User Json
    user_data = {
        'name': name,
        'email': email,
        'branch':branch,
        'rollNo':rollNo,
        'admissionYear':year,
        'password': password,
        'confirm_password': confirm_password
    }

    # Push the user data to the Firebase Realtime Database
    new_user = ref.push(user_data)

    # Return a response (optional)
    return render_template('signup.html')


if __name__ == '__main__':
    app.run()

