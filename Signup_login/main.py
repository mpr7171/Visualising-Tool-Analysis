import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import db
from flask import Flask, session, render_template, request, redirect, request, flash
import re
import json
import requests



FIREBASE_WEB_API_KEY = "AIzaSyC0aEymSwOknoaBuMIYPrzU_JRLXmJF0dU"
rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


app = Flask(__name__)

auth = firebase_admin.auth


app.secret_key='secret'
cred = credentials.Certificate('se-test-7f7e1-firebase-adminsdk-auhlb-6adf0cbd2c.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://se-test-7f7e1-default-rtdb.firebaseio.com"
})

# Define the Firebase Realtime Database reference


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

    branch_match = re.search(r'\d+(.*?)\d+', str(email))
    if branch_match:
        branch = branch_match.group(1)
    else:
        branch = None

    return year, branch


def sign_in_with_email_and_password(email, password, return_secure_token = True):
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": return_secure_token
    })

    rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    r = requests.post(rest_api_url,
                    params={"key": FIREBASE_WEB_API_KEY},
                    data=payload)

    return r.json()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        
        try:

            token = sign_in_with_email_and_password(email, password)
            print(token)

            if 'code' in token:
                if token['code'] == 400:

                    if token["message"] == "EMAIL_NOT_FOUND":
                        return render_template('login.html')
                        
                    if token["message"] == "INVALID_PASSWORD":
                        return render_template('login.html')
                    
            if "registered" in token:
                if token["registered"] == True:
                    email = token['email']
                    name = token['displayName']

                    rollNo=extract_roll_number(email)


                    year,branch= extraction(email)
                    branch_dict = {'uari' : "AI", 
                       'ucse' : "CSE", 
                       'umee' : "ME", 
                       'uece' : "ECE", 
                       'ucam' : "CM",
                       'ueee' : "EEE"}
            
                    branch = branch_dict[branch]


            return render_template('index.html',email = email, student_id = rollNo.upper(), branch = branch, username = name)
        
        
        except Exception as e:
            print(e)
            return render_template('login.html')


    
    else:
        return render_template('login.html')





@app.route('/dashboard')
def dashboard():
    return render_template('index.html')




@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method=='GET':

        return render_template('signup.html')
    

    if request.method=='POST':

        name = request.form.get('signup_name')
        email = request.form.get('signup_email')
        password = request.form.get('signup_password')
        confirm_password = request.form.get('signup_confirm_password')


        if password != confirm_password:
            error_message = "Passwords do not match. Please try again."
            return render_template('signup.html', error_message=error_message)

        try:
            # print(name)
            usr_created = firebase_admin.auth.create_user(email = email, password = password, display_name = name)


            year,branch= extraction(email)
            # year = "20" + year
            rollNo=extract_roll_number(email)

            branch_dict = {'uari' : "AI", 
                       'ucse' : "CSE", 
                       'umee' : "ME", 
                       'uece' : "ECE", 
                       'ucam' : "CM",
                       'ueee' : "EEE"}
            
            branch = branch_dict[branch]
            #User Json
            user_data = {
                'name': name,
                'email': email,
                'branch':branch,
                'rollNo':rollNo,
                'admissionYear':year,
            }





            path = 'students/batch'

            stud_path = f'{path}/{year}/{branch}'
            
            ref = db.reference(stud_path)

            ref.child(rollNo.upper()).set({
                    'name' : name,
                    'email': email
                })


            return redirect('/')

        except Exception as e:
            error = e
            print(error)
            flash(error)
            return render_template('signup.html', error=error)



if __name__ == '__main__':
    app.debug = True
    app.run()