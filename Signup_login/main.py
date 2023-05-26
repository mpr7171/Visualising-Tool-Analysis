import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import db
from flask import Flask, session, render_template, request, redirect, request, flash, url_for
import re
import json
import requests
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import random



FIREBASE_WEB_API_KEY = "AIzaSyC0aEymSwOknoaBuMIYPrzU_JRLXmJF0dU"
rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


app = Flask(__name__)

app.secret_key = '666'
auth = firebase_admin.auth

app.secret_key='secret'
cred = credentials.Certificate('se-test-7f7e1-firebase-adminsdk-auhlb-6adf0cbd2c.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://se-test-7f7e1-default-rtdb.firebaseio.com"
})


@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Define the Firebase Realtime Database reference
def extract_roll_number(email):
    if email is None:
        return None
    
    if '20' in email:
        se = re.sub(r'^(.*?)20', 'se20', str(email))
        roll_number_match = re.search(r'^[^@]+', se)

    elif '19' in email:
        se = re.sub(r'^(.*?)19', 'se19', str(email))
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
            # print(token)

            if 'error' in token:
                if 'code' in token['error']:
                    if token['code'] == 400:
                        if token["message"] == "EMAIL_NOT_FOUND":
                            return redirect('/')
                            
                        elif token["message"] == "INVALID_PASSWORD":
                            return redirect('/')
                        
                        else:
                            return redirect('/')

                        
            if "registered" in token:
                email_splits = email.split("@")

                is_faculty = False
                if "." in email_splits[0]:
                    is_faculty = True

                # print(is_faculty)

                if is_faculty == False:    

                    if token["registered"] == True:
                        email = token['email']
                        name = token['displayName']

                        # print(name)

                        rollNo=extract_roll_number(email)

                        year,branch= extraction(email)
                        branch_dict = {'uari' : "AI", 
                        'ucse' : "CSE", 
                        'umee' : "ME", 
                        'uece' : "ECE", 
                        'ucam' : "CM",
                        'ueee' : "EEE"}
                
                        branch = branch_dict[branch]


                        session['student_id'] = rollNo.upper()
                        session['branch'] = branch
                        session['username'] = name
                        session['year'] = year

                        session['logged_in'] = True

                        return redirect(url_for('dashboard'))
                    
                    else:
                        # print("ooopss")
                        # return redirect(url_for('login'))
                        render_template('login.html')

            

                else:
                    if token["registered"] == True:
                        email = token['email']
                        # name = token['displayName']

                        fullname = email_splits[0].split(".")
                        fname = fullname[0]
                        lname = fullname[1]
                        name = fname + " " + lname

                        session['faculty_name'] = name
                        session['faculty_email'] = email

                        session['logged_in'] = True

                        # return render_template('index_faculty_db.html', prof_name = name)

                        return redirect(url_for('faculty_dashboard'))
                    
                    else:
                        print("ooopss2")
                        # return redirect(url_for('dashboard'))
                        render_template('login.html')



            else:
                render_template('login.html')
                

        except:
            return render_template('login.html')
    
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    student_id = session['student_id']
    branch = session['branch']
    username = session['username']
    year = session['year']


    print(username, branch, username)

    path = 'GPA/batch'

    stud_path = f'{path}/{year}/{branch}/{student_id}'
    
    ref = db.reference(stud_path)

    # gpa_dic = ref.get()

    # course_arr = [] 
    # gpa_arr = []   
    # for k in courses_dic:
    #     course_arr.append(k)
    #     gpa_arr.append(courses_dic[k])

    sems_arr = ['SEM'+str(i+1) for i in range(8)]
    gpa_arr = [random.uniform(3, 10) for i in range(8)]

    fig = go.Figure()

    # fig.add_trace(go.Scatter(x=sems_arr, y=gpa_arr, mode='markers+lines', name='GPA'))
    fig.add_trace(go.Scatter(x=sems_arr, y=gpa_arr, mode='markers+lines', name='GPA'))
    fig.update_xaxes(title_text="SEM")
    fig.update_yaxes(title_text="GPA obtained")
    fig.update_layout(
        height=492, width=760
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs=True)


    return render_template('index.html', student_id = student_id, branch = branch, username = username, graph_html=graph_html)




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

            if ('mahindrauniversity.edu.in' not in email):
                raise Exception("Please use only Mahindra University email")
            

            email_splits = email.split("@")

            if "." in email_splits[0]:
                raise Exception("Please use proper Mahindra University's student email")

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

            # user_data = {
            #     'name': name,
            #     'email': email,
            #     'branch':branch,
            #     'rollNo':rollNo,
            #     'admissionYear':year,
            # }



            path = 'students/batch'

            stud_path = f'{path}/{year}/{branch}'
            
            ref = db.reference(stud_path)

            ref.child(rollNo.upper()).set({
                    'name' : name,
                    'email': email
                })
            

            session['student_id'] = rollNo.upper()
            session['branch'] = branch
            session['username'] = name
            session['year'] = year

            session['logged_in'] = True

            return redirect('/')

            # return redirect('dashboard')

        except Exception as e:
            error = e
            print(error)
            flash(error)
            return render_template('signup.html', error=error)




@app.route('/grades')
def grades():
    return render_template('index_grades.html')



@app.route('/analytics')
def analytics():

    year = session['year']
    branch = session['branch']

    # ref = db.reference(f'grades/{year}/{branch}')

    path = f'grades/{year}/{branch}'
    
    # stud_path = f'{path}/{year}/{branch}'

    ref1 = db.reference(path)

            
    # ref
    data = ref1.get()

    print(data)

    courses = []
    course_scores_dic = {}

    for k in data.keys():
        courses.append(k)
        curr_scores = []
        course_scores = data[k]
        for rollno in course_scores:
            c_score = course_scores[rollno]
            curr_scores.append(c_score)

        course_scores[k] = curr_scores



    # mean = np.mean(marks)
    # std_dev = np.std(marks)
    # x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, 100)
    # y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values - mean) / std_dev) ** 2)

    # percentiles = np.percentile(marks, [50, 75, 90])

    # # fig = go.Figure()
    # fig = make_subplots(rows=2, cols=1, row_heights=[0.5, 0.5],
    #         subplot_titles=("Distrbution of marks across branch", "Histogram of marks (in branch)"))

    # fig.add_trace(go.Scatter(
    #     x=x_values,
    #     y=y_values,
    #     mode='lines',
    #     name='Normal Distribution'
    # ))

    # fig.add_trace(go.Scatter(
    #     x=[percentiles[0], percentiles[0]],
    #     y=[0, np.max(y_values)],
    #     mode='lines',
    #     name='50th Percentile',
    #     line=dict(dash='dash')
    # ))

    # fig.add_trace(go.Scatter(
    #     x=[percentiles[1], percentiles[1]],
    #     y=[0, np.max(y_values)],
    #     mode='lines',
    #     name='75th Percentile',
    #     line=dict(dash='dash')
    # ))

    # fig.add_trace(go.Scatter(
    #     x=[percentiles[2], percentiles[2]],
    #     y=[0, np.max(y_values)],
    #     mode='lines',
    #     name='90th Percentile',
    #     line=dict(dash='dash')
    # ))

    # fig.update_layout(
    #     title='Normal Distribution with Percentiles',
    #     xaxis_title='Marks',
    #     yaxis_title='Probability Density'
    # )

    # histogram = go.Histogram(
    #     x=marks,
    #     nbinsx=10,
    #     name='Marks Distribution'
    # )
    # fig.update_xaxes(title_text="Marks")
    # fig.update_yaxes(title_text="Frequency")

    # fig.add_trace(histogram, row=2, col=1)

    # class_average_str = "{:.2f}".format(mean)

    # fig.update_layout(
    #     # title='Histogram of marks',
    #     # xaxis_title='Marks',
    #     # yaxis_title='Frequency',
    #     height=1200, width=1500
    # )






    return render_template('index_analytics.html')





@app.route('/faculty_dashboard')
def faculty_dashboard():

    # checks if the session metrics are deleted, if deleted, then stays on the login page
    if len(session.keys()) == 0:
        return redirect('/')

    name = session['faculty_name']
    return render_template('index_faculty_db.html', prof_name = name)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')