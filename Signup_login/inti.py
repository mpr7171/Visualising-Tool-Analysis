import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, session, render_template, request, redirect ,jsonify
# from flask_cors import CORS
import re 



app = Flask(__name__)
# CORS(app)

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
    if email is None:
        return None
    
    if '20' in email:
        se = re.sub(r'^(.*?)20', 'se20', str(email))
        roll_number_match = re.search(r'^[^@]+', se)
    else:
        roll_number_match = re.search(r'^[^@]+', str(email))

    if roll_number_match:
        roll_number = roll_number_match.group(0)
    else:
        roll_number = None

    return roll_number

def extraction(email):
    year_match = re.search(r'\d+', str(email))
    if year_match:
        year = year_match.group(0)
    else:
        year = None

    # Extract the branch using the regular expression pattern
    branch_match = re.search(r'\d+(.*?)\d+', str(email))
    if branch_match:
        branch = branch_match.group(1)
    else:
        branch = None

    return year, branch


# @app.route('/', methods = ['POST'])

@app.route('/', methods=['POST','GET'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('pass')
    confirm_password = request.form.get('cpass')

    year,branch= extraction(email)
    rollNo=extract_roll_number(email)

    if branch == "uari":
        branch = "AI"

    if branch == "ucse":
        branch = "CSE"

    if branch == "umee":
        branch = "ME"

    if branch == "ueee":
        branch = "EEE"

    if branch == "ucam":
        branch = "CM"

    if branch == "uece":
        branch = "ECE"

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
    app.debug = True
    app.run()



# @auth.route('/signup', methods=['GET', 'POST'])# we define the sign 
#                                                # up path
# def signup(): # define the sign up function
#     if request.method=='GET': # If the request is GET we return the 
#                               # sign up page and forms
#         return render_template('signup.html')
#     else: # if the request is POST, then we check if the email 
#           # doesn't already exist and then we save data
#         email = request.form.get('email')
#         name = request.form.get('name')
#         password = request.form.get('password')
#         user = User.query.filter_by(email=email).first() # if this 
#                               # returns a user, then the email 
#                               # already exists in database
#         if user: # if a user is found, we want to redirect back to 
#                  # signup page so user can try again
#             flash('Email address already exists')
#             return redirect(url_for('auth.signup'))
#         # create a new user with the form data. Hash the password so 
#         # the plaintext version isn't saved.
#         new_user = User(email=email, name=name, \
#                         password=generate_password_hash(password, \
#                         method='sha256'))#add the new user to the db
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('auth.login'))
