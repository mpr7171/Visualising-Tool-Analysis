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
import pandas as pd
from datetime import datetime
import logging
from functions import *


FIREBASE_WEB_API_KEY = "AIzaSyC0aEymSwOknoaBuMIYPrzU_JRLXmJF0dU"
rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


app = Flask(__name__)

app.secret_key = '666'
auth = firebase_admin.auth

app.secret_key='secret'
cred = credentials.Certificate("Main_folder\\se-test-7f7e1-firebase-adminsdk-auhlb-6adf0cbd2c.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://se-test-7f7e1-default-rtdb.firebaseio.com"
})

database=db.reference('Gpa2')
resources=db.reference('Resources')

@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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


def previous_year(curr_year,branch):

    path_prev = f'grades/{int(curr_year)-1}/{branch}'
    ref_prev = db.reference(path_prev)

    path = f'grades/{curr_year}/{branch}'
    ref1 = db.reference(path)

    no_data = False
    disp_msg = ""
    data = ref1.get()
    data_prev = ref_prev.get()

    if data and data_prev == None:
        data = {}
        no_data  = True
        disp_msg = "Please wait until your respective faculty upload the scores."
    elif data == None:
        data={}
        no_data = True
        disp_msg = "Please wait until your respective faculty upload the scores."
    elif data_prev == None:
        data={}
        no_data = True
        disp_msg = "Please wait until your respective faculty upload the scores."
    
    courses = []
    prev_course_scores_dic = {}
    course_scores_dic = {}
    curr_user_scores = []
    curr_user_perc = []
    graphs = []

    if (data and data_prev) == None or data == None or data_prev == None:
        return (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc)
    
    for k in data.keys():
        if k in data_prev.keys():
            courses.append(k)
            curr_scores = []
            prev_scores = []
            course_scores = data[k]
            prev_course_scores = data_prev[k]
            for rollno in course_scores:
                c_score = course_scores[rollno]
                curr_scores.append(c_score)
            course_scores_dic[k] = curr_scores

            for rollno in prev_course_scores:
                p_score = prev_course_scores[rollno]
                prev_scores.append(p_score)
            prev_course_scores_dic[k] = prev_scores
    
    num_pres = 0
    exam_type = 'endsem'

    for course in courses:
        curr_course_scores = course_scores_dic[course]
        prev_course_scores = prev_course_scores_dic[course]

        curr_marks = []
        prev_marks = []
        cscore = 0
        flag = False

        for stud in curr_course_scores:
            if exam_type in stud:
                flag= True
                curr_marks.append(stud[exam_type])
                if stud['student_id'] == session['student_id']:
                    curr_user_scores.append(stud[exam_type])
                    cscore = stud[exam_type]
        
        for stud in prev_course_scores:
            if exam_type in stud:
                prev_marks.append(stud[exam_type])
                

        if flag:
            num_pres+=1
            curr_user_perc.append(calculate_percentage(your_score=cscore, scores = curr_marks))
            mean = np.mean(curr_marks)
            mean_prev = np.mean(prev_marks)
            std_dev = np.std(curr_marks)
            std_dev_prev = np.std(prev_marks)
            x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, 100)
            y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values - mean) / std_dev) ** 2)
            x_values_prev = np.linspace(mean_prev - 3 * std_dev_prev, mean_prev + 3 * std_dev_prev, 100)
            y_values_prev = (1 / (std_dev_prev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values_prev - mean_prev) / std_dev_prev) ** 2)

            percentiles = np.percentile(curr_marks, [50, 75, 90])
            percentiles_prev = np.percentile(prev_marks, [50, 75, 90])

            fig = make_subplots(rows=4, cols=1, subplot_titles=(f"Distrbution of marks across for {course}", 
                                                                f"Distrbution of marks across for {course} of Previous Year",
                                                                "Histogram of marks (in branch)", 
                                                                "Histogram of marks (in branch) of Previous Year"))

            # curr_scatter = go.Scatter(
            #     x=x_values,
            #     y=y_values,
            #     mode='lines',
            #     name='Normal Distribution'
            # )

            # curr_scatter.add_trace(go.Scatter(
            #     x=[mean, mean],
            #     y=[0, np.max(y_values)],
            #     mode='lines',
            #     name='Mean',
            #     line=dict(dash='dash')
            # ))

            # curr_scatter.add_trace(go.Scatter(
            #     x=[np.max(curr_marks), np.max(curr_marks)],
            #     y=[0, np.max(y_values)],
            #     mode='lines',
            #     name='Max score obtained',
            #     line=dict(dash='dash')
            # ))

            # curr_scatter.add_trace(go.Scatter(
            #     x=[percentiles[2], percentiles[2]],
            #     y=[0, np.max(y_values)],
            #     mode='lines',
            #     name='90th Percentile',
            #     line=dict(dash='dash')
            # ))

            # curr_scatter.add_trace(go.Scatter(
            #     x=[cscore, cscore],
            #     y=[0, np.max(y_values)],
            #     mode='lines',
            #     name='Your score',
            #     line=dict(dash='solid')
            # ))

            # curr_scatter.update_layout(
            #     title='Normal Distribution with Percentiles',
            #     xaxis_title='Marks',
            #     yaxis_title='Probability Density',
            #     height=2400,
            #     width=1600
            # )

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                name='Normal Distribution'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[mean, mean],
                y=[0, np.max(y_values)],
                mode='lines',
                name='Mean',
                line=dict(dash='dash')
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[np.max(curr_marks), np.max(curr_marks)],
                y=[0, np.max(y_values)],
                mode='lines',
                name='Max score obtained',
                line=dict(dash='dash')
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[percentiles[2], percentiles[2]],
                y=[0, np.max(y_values)],
                mode='lines',
                name='90th Percentile',
                line=dict(dash='dash')
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[cscore, cscore],
                y=[0, np.max(y_values)],
                mode='lines',
                name='Your score',
                line=dict(dash='solid')
            ), row=1, col=1)

            # fig.update_layout(
            #     # title='Normal Distribution with Percentiles',
            #     xaxis_title='Marks',
            #     yaxis_title='Probability Density',
            #     height=2400,
            #     width=1600
            # )


            # prev_scatter = go.Scatter(
            #     x=x_values_prev,
            #     y=y_values_prev,
            #     mode='lines',
            #     name='Normal Distribution'
            # )

            # prev_scatter.add_trace(go.Scatter(
            #     x=[mean_prev, mean_prev],
            #     y=[0, np.max(y_values_prev)],
            #     mode='lines',
            #     name='Mean',
            #     line=dict(dash='dash')
            # ))

            # prev_scatter.add_trace(go.Scatter(
            #     x=[np.max(prev_marks), np.max(prev_marks)],
            #     y=[0, np.max(y_values_prev)],
            #     mode='lines',
            #     name='Max score obtained',
            #     line=dict(dash='dash')
            # ))

            # prev_scatter.add_trace(go.Scatter(
            #         x=[percentiles_prev[2], percentiles_prev[2]],
            #         y=[0, np.max(y_values_prev)],
            #         mode='lines',
            #         name='90th Percentile',
            #         line=dict(dash='dash')
            # ))

            # prev_scatter.update_layout(
            #     title='Normal Distribution with Percentiles (Previous Year)',
            #     xaxis_title='Marks',
            #     yaxis_title='Probability Density',
            #     height=2400,
            #     width=1600
            # )
            fig.add_trace(go.Scatter(
                x=x_values_prev,
                y=y_values_prev,
                mode='lines',
                name='Normal Distribution'
            ), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=[mean_prev, mean_prev],
                y=[0, np.max(y_values_prev)],
                mode='lines',
                name='Mean',
                line=dict(dash='dash')
            ), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=[np.max(prev_marks), np.max(prev_marks)],
                y=[0, np.max(y_values_prev)],
                mode='lines',
                name='Max score obtained',
                line=dict(dash='dash')
            ), row=2, col=1)

            fig.add_trace(go.Scatter(
                    x=[percentiles[2], percentiles[2]],
                    y=[0, np.max(y_values_prev)],
                    mode='lines',
                    name='90th Percentile',
                    line=dict(dash='dash')
                ))

            # fig.update_layout(
            #     # title='Normal Distribution with Percentiles (Previous Year)',
            #     xaxis_title='Marks',
            #     yaxis_title='Probability Density',
            #     height=2400,
            #     width=1600
            # )


            # histogram = go.Histogram(
            #     x=curr_marks,
            #     nbinsx=10,
            #     name='Marks Distribution'
            # )

            # histogram.update_layout(
            #     title='Histogram of Marks',
            #     xaxis_title='Marks',
            #     yaxis_title='Frequency'
            #     height=800,
            #     width=1200
            # )

            # histogram_prev = go.Histogram(
            #     x=prev_marks,
            #     nbinsx=10,
            #     name='Marks Distribution (Previous Year)'
            # )

            # histogram_prev.update_layout(
            #     title='Histogram of Marks (Previous Year)',
            #     xaxis_title='Marks',
            #     yaxis_title='Frequency',
            #     height=2400,
            #     width=1600
            # )
            fig.add_trace(go.Histogram(
                x=curr_marks,
                nbinsx=10,
                name='Marks Distribution'
            ), row=3, col=1)

            # fig.update_layout(
            #     # title='Histogram of Marks',
            #     xaxis_title='Marks',
            #     yaxis_title='Frequency'
            #     height=800,
            #     width=1200
            # )

            fig.add_trace(go.Histogram(
                x=prev_marks,
                nbinsx=10,
                name='Marks Distribution (Previous Year)'
            ), row=4, col=1)

            fig.update_layout(
                # title='Histogram of Marks (Previous Year)',
                # xaxis_title='Marks',
                # yaxis_title='Frequency',
                height=2400,
                width=1600
            )

            fig.update_xaxes(title_text='Marks',row=1,col=1)
            fig.update_yaxes(title_text='Probability Density', row=1, col=1)
            fig.update_xaxes(title_text='Marks',row=2,col=1)
            fig.update_yaxes(title_text='Probability Density', row=2, col=1)
            fig.update_xaxes(title_text='Marks',row=3,col=1)
            fig.update_yaxes(title_text='Frequency', row=3, col=1)
            fig.update_xaxes(title_text='Marks',row=4,col=1)
            fig.update_yaxes(title_text='Frequency', row=4, col=1)

            # fig.update_xaxes(title_text="Marks")
            # fig.update_yaxes(title_text="Frequency")
            # fig.update_layout(
            # title='Histogram of marks',
            # xaxis_title='Marks',
            # yaxis_title='Frequency',
            # height=800, width=1200
            # )
            # fig.add_trace(curr_scatter,row=1,col=1)
            # fig.add_trace(prev_scatter,row=2,col=1)
            # fig.add_trace(histogram,row=3,col=1)
            # fig.add_trace(histogram_prev,row=4,col=1)
            

            graph_html = fig.to_html(full_html=False, include_plotlyjs=True)
            graphs.append(graph_html)


        if num_pres == 0:
            no_data = True

            disp_msg = "Please wait until your respective faculty uploads the scores."

        return (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc)


def get_analytics_info(year, branch, exam_type):
    if exam_type=='previousyear':
        (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc) = previous_year(year,branch)
        return (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc)
    else:
        path = f'grades/{year}/{branch}'
        
        ref1 = db.reference(path)

        no_data = False
        disp_msg = ""

        data = ref1.get()

        if data == None:
            data = {}
            no_data  = True
            disp_msg = "Please wait until your respective faculty upload the scores."
        
            

        courses = []
        course_scores_dic = {}

        curr_user_scores = []
        curr_user_perc = []
        graphs = []

        if data == None:
            return (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc)

        for k in data.keys():
            courses.append(k)
            curr_scores = []
            course_scores = data[k]
            for rollno in course_scores:    

                c_score = course_scores[rollno]
                curr_scores.append(c_score)

            course_scores_dic[k] = curr_scores

        num_pres = 0
        
        for course in courses:
            curr_course_scores = course_scores_dic[course]

            curr_marks = []

            cscore = 0  

            flag = False

            for stud in curr_course_scores:

                if exam_type in stud:
                    flag = True
                    curr_marks.append(stud[exam_type])


                    if stud['student_id'] == session["student_id"]:
                        curr_user_scores.append(stud[exam_type])
                        cscore = stud[exam_type]
                
                    
            if flag:
                num_pres += 1
                curr_user_perc.append(calculate_percentage(your_score=cscore,scores=curr_marks))

                mean = np.mean(curr_marks)
                std_dev = np.std(curr_marks)
                x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, 100)
                y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values - mean) / std_dev) ** 2)

                percentiles = np.percentile(curr_marks, [50, 75, 90])

                fig = go.Figure()
                fig = make_subplots(rows=2, cols=1, row_heights=[0.5, 0.4],
                        subplot_titles=(f"Distrbution of marks across for {course}", "Histogram of marks (in branch)"))

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='lines',
                    name='Normal Distribution'
                ))

                fig.add_trace(go.Scatter(
                    x=[mean, mean],
                    y=[0, np.max(y_values)],
                    mode='lines',
                    name='Mean',
                    line=dict(dash='dash')
                ))

                fig.add_trace(go.Scatter(
                    x=[np.max(curr_marks), np.max(curr_marks)],
                    y=[0, np.max(y_values)],
                    mode='lines',
                    name='Max score obtained',
                    line=dict(dash='dash')
                ))


                fig.add_trace(go.Scatter(
                    x=[percentiles[2], percentiles[2]],
                    y=[0, np.max(y_values)],
                    mode='lines',
                    name='90th Percentile',
                    line=dict(dash='dash')
                ))

                fig.add_trace(go.Scatter(
                    x=[cscore, cscore],
                    y=[0, np.max(y_values)],
                    mode='lines',
                    name='Your score',
                    line=dict(dash='solid')
                ))

                fig.update_layout(
                    title='Normal Distribution with Percentiles',
                    xaxis_title='Marks',
                    yaxis_title='Probability Density'
                )

                histogram = go.Histogram(
                    x=curr_marks,
                    nbinsx=10,
                    name='Marks Distribution'
                )
                fig.update_xaxes(title_text="Marks")
                fig.update_yaxes(title_text="Frequency")

                fig.add_trace(histogram, row=2, col=1)

                fig.update_layout(
                title='Histogram of marks',
                xaxis_title='Marks',
                yaxis_title='Frequency',
                height=800, width=1200
                )

                graph_html = fig.to_html(full_html=False, include_plotlyjs=True)
                graphs.append(graph_html)

            
        
        if num_pres == 0:
            no_data = True

            disp_msg = "Please wait untill your respective faculty uploads the scores."

        return (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc)



@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            token = sign_in_with_email_and_password(email, password)
            session['user_id'] = token['localId']
            session['email'] = email
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
                        # session['email'] = email

                        session['logged_in'] = True

                        return redirect(url_for('dashboard'))
                    
                    else:

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

    year_int = int("20"+year)
    curr_sem = calculate_current_semester(year_int)

    path = 'GPA'

    stud_path = f'{path}/{year}/{branch}/{student_id}'
    ref = db.reference(stud_path)

    sems_arr = []
    gpa_arr = []
    gpa_dic = ref.get()

    no_flag = False
    if gpa_dic == None:
        no_flag = True


    if no_flag == False:
        gpa_arr_temp = list(gpa_dic.values())
        for i in range(len(gpa_arr_temp)):

            sems_arr.append('SEM'+str(i+1))

            if gpa_arr_temp[i] == "NULL":
                gpa_arr.append(0)

            else:
                gpa_arr.append(gpa_arr_temp[i])

    else:
        for i in range(8):

            sems_arr.append('SEM'+str(i+1))
            gpa_arr.append(0)

    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=sems_arr, y=gpa_arr, mode='markers+lines', name='GPA'))
    fig.update_xaxes(title_text="SEM")
    fig.update_yaxes(title_text="GPA obtained")
    fig.update_layout(
        height=498, width=765
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs=True)


    return render_template('index.html', student_id = student_id, branch = branch, username = username, curr_sem = curr_sem ,graph_html=graph_html)




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

            rollNo=extract_roll_number(email)

            branch_dict = {'uari' : "AI", 
                       'ucse' : "CSE", 
                       'umee' : "ME", 
                       'uece' : "ECE", 
                       'ucam' : "CM",
                       'ueee' : "EEE"}
            
            branch = branch_dict[branch]


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
    if 'user_id' in session:
        # Existing code for user authentication and session handling...

        # Extract roll number and year batch from session's email
        rollNo = extract_roll_number(session['email'])
        yearBatch = extraction(session['email'])
        year = yearBatch[0]

        # Fetch grades based on the year batch and branch
        if yearBatch[1] == 'uari':
            location = f"{year}/AI/{rollNo}"
            fetch = database.child(location).get()
        
        if yearBatch[1] == 'ucse':
            location = f"{year}/CSE/{rollNo}"
            fetch = database.child(location).get()
        
        if yearBatch[1] == 'ueee':
            location = f"{year}/EEE/{rollNo}"
            fetch = database.child(location).get()

        # If no grades are found, render template with empty data
        if not fetch:
            return render_template('index_grades.html', courses=[], additional_resources={}, previous_year_papers_link=None)

        courses = []  # List to store the fetched courses
        additional_resources = {}  # Dictionary to store additional resources
        previous_year_papers_link = resources.child('previousYearPapers').get()  # Fetch the previous year papers link

        # Process the fetched courses and their grades
        for course_key, course_data in fetch.items():
            course = {
                'courseName': course_data['courseName'],
                'courseCredit': course_data['courseCredit'],
                'score': course_data['gradeGot']
            }
            if course_data['gradeGot'] <= 4:
                # Fetch study playlist for courses with a score less than 4
                playlist_key = course_data['courseName']
                additional_resources[playlist_key] = {
                    'studyPlaylist': resources.child('Branch').child('AI').child('Sem-3').child(playlist_key).get()
                }
            courses.append(course)

        # Render template with the processed data
        return render_template('index_grades.html', courses=courses, additional_resources=additional_resources, previous_year_papers_link=previous_year_papers_link)
    else:
        # Redirect to login page if user not authenticated
        return redirect(url_for('login'))

# @app.route('/analytics')
# def analytics():

#     year = session['year']
#     branch = session['branch']

#     (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc) = get_analytics_info(year,branch, exam_type='minor1')

#     return render_template('index_analytics.html', 
#                         courses=courses,
#                         graphs=graphs,
#                         curr_user_scores = curr_user_scores ,
#                         curr_user_perc = curr_user_perc, 
#                         zip=zip, 
#                         no_data = no_data, disp_msg = disp_msg)



@app.route('/analytics_redirect')
def analytics():

    student_id = session['student_id']
    branch = session['branch']
    username = session['username']
    year = session['year']

    year_int = int("20"+year)
    curr_sem = calculate_current_semester(year_int)

    return render_template('analytics_redirect.html', 
                        student_id = student_id, branch = branch, username = username, curr_sem = curr_sem )





@app.route('/minor1')
def minor1():
    year = session['year']
    branch = session['branch']

    path = f'grades/{year}/{branch}'
    

    (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc) = get_analytics_info(year,branch, exam_type='minor1')


    return render_template('index_analytics.html', 
                        courses=courses,
                        graphs=graphs,
                        curr_user_scores = curr_user_scores ,
                        curr_user_perc = curr_user_perc, 
                        zip=zip, 
                        no_data = no_data, disp_msg = disp_msg)

@app.route('/minor2')
def minor2():
    year = session['year']
    branch = session['branch']

    path = f'grades/{year}/{branch}'
    

    (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc) = get_analytics_info(year,branch, exam_type='minor2')


    return render_template('index_analytics_m2.html', 
                        courses=courses,
                        graphs=graphs,
                        curr_user_scores = curr_user_scores ,
                        curr_user_perc = curr_user_perc, 
                        zip=zip, 
                        no_data = no_data, disp_msg = disp_msg)

@app.route('/endsem')
def endsem():
    year = session['year']
    branch = session['branch']

    path = f'grades/{year}/{branch}'
    

    (no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc) = get_analytics_info(year,branch, exam_type='endsem')


    return render_template('index_analytics_es.html', 
                        courses=courses,
                        graphs=graphs,
                        curr_user_scores = curr_user_scores ,
                        curr_user_perc = curr_user_perc, 
                        zip=zip, 
                        no_data = no_data, disp_msg = disp_msg)

@app.route('/prevyear')
def prevyear():
    year = session['year']
    branch = session['branch']

    # path = f'grades/{year}/{branch}'
    no_data,disp_msg,courses,graphs,curr_user_scores,curr_user_perc = get_analytics_info(year,branch, exam_type='previousyear')
    return render_template('index_analytics_pyear.html', 
                        courses=courses,
                        graphs=graphs,
                        curr_user_scores = curr_user_scores ,
                        curr_user_perc = curr_user_perc, 
                        zip=zip, 
                        no_data = no_data,
                        disp_msg = disp_msg)
    # implement the function for grabbing and comapring previous year grades.
    

#######################  FACULTY  ##########################


@app.route('/upload')
def index():
    return render_template('upload.html')


@app.route('/faculty_analytics')
def faculty_analytics(batch, subject_code, exam_type,branch):
    database_url = 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
    path = 'grades/' + batch + '/' +branch + '/' + subject_code
    data = db.reference(path).get()
    studentID = list(data.keys())
    
    
    
    
    
    
    # MINOR 1 ----------------------------------------------------------------------
    if exam_type == "minor1":
        minor1_grades = []
        for i in range(len(studentID)):
            marks = db.reference(path+'/'+studentID[i]).get()
            minor1_grades.append(marks['minor1'])
        
        minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
        fig = go.Figure()
        fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
        fig.update_layout(title= "The grade analysis of the course " + subject_code)
        fig.update_layout(showlegend=True)
        
        #Normal Curve 
        minor1_grades = np.array(minor1_grades)
        avg_m1 = np.mean(minor1_grades)
        std = np.std(minor1_grades)
        
        

        # # Generate x-axis values
        x = np.linspace(minor1_grades.min(), minor1_grades.max(), 100)
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - avg_m1) / std) ** 2)

       

        # Plot the bell curve
        fig2 = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Bell Curve'))
        fig2.update_layout(
            title="The normal distribution analysis of the " + subject_code,
            xaxis_title='Marks',
            yaxis_title='Probability Density',
            showlegend=True
        )
        sample = np.random.normal(avg_m1, std, len(minor1_grades))

        percentiles = [75, 90, 95]

        counts_above_percentiles = []

        # Calculate the percentiles and the number of values above each percentile
        for percentile in percentiles:
            percentile_value = np.percentile(sample, percentile)
            count_above_percentile = sum(value > percentile_value for value in sample)
            counts_above_percentiles.append(count_above_percentile)
            
            
            # Calculate the percentiles
        colors = ['red', 'blue', 'green']  # Specify colors for each percentile line
        percentiles = [ 75, 90, 95]
        percentile_values = np.percentile(minor1_grades, percentiles)

        for percentile, value, color in zip(percentiles, percentile_values, colors):
            fig2.add_shape(
                type="line",
                xref="x",
                yref="y",
                x0=value,
                x1=value,
                y0=0,
                y1=max(y),
                line=dict(color=color, width=2, dash="dash"),
            )

        # Add invisible scatter traces for legends
            fig2.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(color=color),
                    name=f"{percentile}th Percentile"
                )
            )

        fig2.update_layout(showlegend=True)
        
        
        
        
        hist, bins = np.histogram(minor1_grades)

        # Find the bin with the highest count
        highest_freq_bin_index = np.argmax(hist)
        highest_freq_count = np.max(hist)

        # Determine the range of the bin with the highest count
        range_start = bins[highest_freq_bin_index]
        range_end = bins[highest_freq_bin_index + 1]

        fig3 = go.Figure(data=[go.Histogram(x=minor1_grades)])

        # Find the index of the bin with the highest count
    

        # Set the color for all bins
        colors = ['lightblue'] * len(hist)

        # Set a different color for the bin with the highest count
        colors[highest_freq_bin_index] = 'red'

        # Update the marker color for the histogram trace
        fig3.update_traces(marker=dict(color=colors))

        fig3.update_layout(title="Histogram of Minor1 Grades",
                            xaxis_title="Marks",
        yaxis_title="Frequency")
        

        # fig3 = go.Figure(data=[go.Histogram(x=minor1_grades)])


        # fig3.update_layout(
        #     title="Histogram for the Minor 1 Grades",
        #     xaxis_title="Marks",
        #     yaxis_title="Frequency"
        # )

        
        graph_json = fig.to_json()
        graph2_json = fig2.to_json()
        graph3_json = fig3.to_json()
        
        highest = minor1_grades.max()
        lowest = minor1_grades.min()
        Q1 = np.percentile(minor1_grades, 25)
        Q3 = np.percentile(minor1_grades, 75)
        sorted_array = np.sort(minor1_grades)[::-1]
        
        return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json, graph3_json = graph3_json, avg = avg_m1, highest = highest, lowest = lowest, 
                           course = subject_code, type = 'Minor 1', q1 = Q1, q2 = Q3, start = range_start, end = range_end, high_freq_count = highest_freq_count+1,
                           asc = sorted_array, counts = counts_above_percentiles)
    
    
    
    
    
    
    # MINOR 2 -------------------------------------------------------------------------- 
    
    
    elif exam_type == "minor2":
        minor1_grades = []
        minor2_grades = []
        for i in range(len(studentID)):
            
            marks = db.reference(path+'/'+studentID[i]).get()
            if(marks['minor1'] == None):
                return "Minor 1 grades have not been uploaded. Please upload Minor1 grades"
            minor1_grades.append(marks['minor1'])
            minor2_grades.append(marks['minor2'])
        minor1_grades = np.array(minor1_grades)
        minor2_grades = np.array(minor2_grades)
        avg_m1 = np.mean(minor1_grades)
        avg_m2 = np.mean(minor2_grades)
        minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
        minor2_df = pd.DataFrame({'Minor2': np.array(minor2_grades)})
        fig = go.Figure()
        fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
        fig.add_trace(go.Box(y=minor2_df['Minor2'], name="Minor 2"))
        fig.update_layout(showlegend=True)
        
        
        
        std = np.std(minor2_grades)
        x = np.linspace(minor2_grades.min(), minor2_grades.max(), 100)
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - avg_m1) / std) ** 2)
        fig2 = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Bell Curve'))
        fig2.update_layout(
            title="The normal distribution analysis of the course " + subject_code,
            xaxis_title='Marks',
            yaxis_title='Probability Density',
            showlegend=True
        )
        
        
        # Calculate the percentiles
        sample = np.random.normal(avg_m2, std, len(minor2_grades))

        percentiles = [75, 90, 95]

        counts_above_percentiles = []

        # Calculate the percentiles and the number of values above each percentile
        for percentile in percentiles:
            percentile_value = np.percentile(sample, percentile)
            count_above_percentile = sum(value > percentile_value for value in sample)
            counts_above_percentiles.append(count_above_percentile)
            
            
            # Calculate the percentiles
        colors = ['red', 'blue', 'green']  # Specify colors for each percentile line
        percentiles = [ 75, 90, 95]
        percentile_values = np.percentile(minor2_grades, percentiles)

        for percentile, value, color in zip(percentiles, percentile_values, colors):
            fig2.add_shape(
                type="line",
                xref="x",
                yref="y",
                x0=value,
                x1=value,
                y0=0,
                y1=max(y),
                line=dict(color=color, width=2, dash="dash"),
            )

        # Add invisible scatter traces for legends
            fig2.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(color=color),
                    name=f"{percentile}th Percentile"
                )
            )

        
        fig2.update_layout(showlegend=True)
    
    
        
        hist, bins = np.histogram(minor2_grades)

        # Find the bin with the highest count
        highest_freq_bin_index = np.argmax(hist)
        highest_freq_count = np.max(hist)

        # Determine the range of the bin with the highest count
        range_start = bins[highest_freq_bin_index]
        range_end = bins[highest_freq_bin_index + 1]

        fig3 = go.Figure(data=[go.Histogram(x=minor2_grades)])

        # Find the index of the bin with the highest count
    

        # Set the color for all bins
        colors = ['lightblue'] * len(hist)

        # Set a different color for the bin with the highest count
        colors[highest_freq_bin_index] = 'red'

        # Update the marker color for the histogram trace
        fig3.update_traces(marker=dict(color=colors))

        fig3.update_layout(title="Histogram of Minor2 Grades",
                            xaxis_title="Marks",
        yaxis_title="Frequency")
        

        
        
        
        # fig3 = go.Figure(data=[go.Histogram(x=minor1_grades)])


        # fig3.update_layout(
        #     title="Histogram for the Minor 1 Grades",
        #     xaxis_title="Marks",
        #     yaxis_title="Frequency"
        # )

        
        graph_json = fig.to_json()
        graph2_json = fig2.to_json()
        graph3_json = fig3.to_json()
        
        
        
        
        
        
        #

        highest = minor2_grades.max()
        lowest = minor2_grades.min()
        Q1 = np.percentile(minor2_grades, 25)
        Q3 = np.percentile(minor2_grades, 75)
        sorted_array = np.sort(minor2_grades)[::-1]
        
        return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json, graph3_json = graph3_json, avg = avg_m2, highest = highest, lowest = lowest, 
                           course = subject_code, type = 'Minor 2', q1 = Q1, q2 = Q3, start = range_start, end = range_end, high_freq_count = highest_freq_count+1,
                           asc = sorted_array, counts = counts_above_percentiles)
    
    
    
    
    
    
    
    
    
    
    # END SEM --------------------------------------------------------------
    
    
    
    
    
    elif exam_type == "endsem":
        minor1_grades = []
        minor2_grades = []
        end_sem_grades = []
        for i in range(len(studentID)):
            marks = db.reference(path+'/'+studentID[i]).get()
            if(marks['minor1'] == None):
                return "Minor 1 grades have not been uploaded. Please upload Minor1 grades"
            elif (marks['minor2'] == None):
                return "Minor 2 grades have not been uploaded. Please upload Minor2 grades"
            
            minor1_grades.append(marks['minor1'])
            minor2_grades.append(marks['minor2'])
            end_sem_grades.append(marks['endsem'])
            
        minor1_grades = np.array(minor1_grades)
        minor2_grades = np.array(minor2_grades)
        end_sem_grades = np.array(end_sem_grades)
        avg_m1 = np.mean(minor1_grades)
        avg_m2 = np.mean(minor2_grades)
        avg_endsem = np.mean(end_sem_grades)
        minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
        minor2_df = pd.DataFrame({'Minor2': np.array(minor2_grades)})
        endsem_df = pd.DataFrame({'End Sem': np.array(end_sem_grades)})
        fig = go.Figure()
        fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
        fig.add_trace(go.Box(y=minor2_df['Minor2'], name="Minor 2"))
        fig.add_trace(go.Box(y=endsem_df['End Sem'], name="End Semester"))
        fig.update_layout(showlegend=True)
        
        std = np.std(end_sem_grades)
        x = np.linspace(end_sem_grades.min(), end_sem_grades.max(), 100)
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - avg_m1) / std) ** 2)
        fig2 = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Normal dist'))
        fig2.update_layout(
            title="The normal distribution  analysis of the " + subject_code,
            xaxis_title='Marks',
            yaxis_title='Probability Density',
            showlegend=True
        )
        
        # Calculate the percentiles
        sample = np.random.normal(avg_endsem, std, len(end_sem_grades))

        percentiles = [ 75, 90, 95]

        counts_above_percentiles = []

        # Calculate the percentiles and the number of values above each percentile
        for percentile in percentiles:
            percentile_value = np.percentile(sample, percentile)
            count_above_percentile = sum(value > percentile_value for value in sample)
            counts_above_percentiles.append(count_above_percentile)
            
            # Calculate the percentiles
        colors = ['red', 'blue', 'green']  # Specify colors for each percentile line
    
        percentile_values = np.percentile(end_sem_grades, percentiles)

        for percentile, value, color in zip(percentiles, percentile_values, colors):
            fig2.add_shape(
                type="line",
                xref="x",
                yref="y",
                x0=value,
                x1=value,
                y0=0,
                y1=max(y),
                line=dict(color=color, width=2, dash="dash"),
            )

        # Add invisible scatter traces for legends
            fig2.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(color=color),
                    name=f"{percentile}th Percentile"
                )
            )

        
        fig2.update_layout(showlegend=True) 
        
        
        hist, bins = np.histogram(end_sem_grades)

        # Find the bin with the highest count
        highest_freq_bin_index = np.argmax(hist)
        highest_freq_count = np.max(hist)

        # Determine the range of the bin with the highest count
        range_start = bins[highest_freq_bin_index]
        range_end = bins[highest_freq_bin_index + 1]

        fig3 = go.Figure(data=[go.Histogram(x=end_sem_grades)])

        # Find the index of the bin with the highest count
    

        # Set the color for all bins
        colors = ['lightblue'] * len(hist)

        # Set a different color for the bin with the highest count
        colors[highest_freq_bin_index] = 'red'

        # Update the marker color for the histogram trace
        fig3.update_traces(marker=dict(color=colors))

        fig3.update_layout(title="Histogram of End semester Grades",
                            xaxis_title="Marks",
        yaxis_title="Frequency")
        

        
        
        
        # fig3 = go.Figure(data=[go.Histogram(x=minor1_grades)])


        # fig3.update_layout(
        #     title="Histogram for the Minor 1 Grades",
        #     xaxis_title="Marks",
        #     yaxis_title="Frequency"
        # )

        
        graph_json = fig.to_json()
        graph2_json = fig2.to_json()
        graph3_json = fig3.to_json()
        
        
        
        
        
        
        #

        highest = end_sem_grades.max()
        lowest = end_sem_grades.min()
        Q1 = np.percentile(end_sem_grades, 25)
        Q3 = np.percentile(end_sem_grades, 75)
        sorted_array = np.sort(end_sem_grades)[::-1]
        
        return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json, graph3_json = graph3_json, avg = avg_endsem, highest = highest, lowest = lowest, 
                           course = subject_code, type = 'End Sem', q1 = Q1, q2 = Q3, start = range_start, end = range_end, high_freq_count = highest_freq_count+1,
                           asc = sorted_array, counts = counts_above_percentiles)

    return "Analytics cannot be viewed"
            
            
            
        
    
    
    

def upload_to_database(batch, exam_type, file):
    
    csv_file = request.files['file']

    fn_contents = csv_file.filename.split("_")
    
    database_url = 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
    subject_code = fn_contents[0]
    branch = subject_code[:2]
    
    
    if len(batch)>2:
        batch = batch[2:]

    
    
        
    path = 'grades/'+ batch + '/' + branch + '/' + subject_code 
    


    if csv_file and csv_file.filename.endswith('.csv'):

        df_csv = pd.read_csv(csv_file)

        if exam_type == "minor1":
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                data = {
                    'student_id': student_id,
                    'minor1': int(df_csv['Marks'][i])
                }
                response = requests.put(f'{database_url}/{path}/{student_id}.json', json=data)
                if response.status_code == 200:
                    continue 
                else:
                    print("Error: Can't add details")


       
        elif exam_type == "minor2":
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                
                # response = requests.put(f'{database_url}/{path}/{subject_code}/{student_id}.json', json=data)
                student_ref = db.reference(str(path +'/' + student_id))
                student_details = student_ref.get()
                
                
                if(student_details == None):
                    return 'Please upload Minor1 Results'
                else:
                    student_details['minor2'] = int(df_csv['Marks'][i])
                    student_ref.update(student_details)
                
            
           

        elif exam_type == "endsem":
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                
                # response = requests.put(f'{database_url}/{path}/{subject_code}/{student_id}.json', json=data)
                student_ref = db.reference(str(path + '/' + student_id))
                student_details = student_ref.get()
                if(student_details == None):
                    return 'Please upload Minor1 and Minor2 Results'
                student_details['endsem'] = int(df_csv['Marks'][i])
                student_ref.update(student_details)
                

        
        # firebase_admin.delete_app(firebase_admin.get_app())
        return faculty_analytics(batch, subject_code, exam_type, branch)
        # return ' Added successfully'
    

    else:
        # firebase_admin.delete_app(firebase_admin.get_app())
        return 'Invalid file format. Please upload a CSV file.'
                
            


    
    


@app.route('/process', methods=['POST', 'GET'])
def process():
    batch = request.form['batch']
    # subject_code = request.form['subject_code']
    exam_type = request.form['exam_type']
    file = request.files['file']
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Log the received data
    logger.info("Batch: %s", batch)
    logger.info("Exam type: %s", exam_type)
    logger.info("File Name: %s", file.filename)
    result = upload_to_database(batch, exam_type, file)
    # Process the user inputs and file as needed

    return result


@app.route('/faculty_dashboard')
def faculty_dashboard():

    # checks if the session metrics are deleted, if deleted, then stays on the login page
    if len(session.keys()) == 0:
        return redirect('/')

    name = session['faculty_name']

    first_name, last_name = name.split()
    # Capitalize the first letter of each name
    capitalized_first_name = first_name.capitalize()
    capitalized_last_name = last_name.capitalize()

    # Create the capitalized full name
    capitalized_name = capitalized_first_name + " " + capitalized_last_name
        
    db_name = name.replace(' ', '_')
    path = 'faculty/' + db_name + '/Courses'
    # database_url = 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
    
    courses = db.reference(path).get()
    course_list = list(courses.keys())
    course_names = []
    
    for i in range(len(course_list)):
        c_name = db.reference('course_names/'+course_list[i]+'/course_name').get()
        course_names.append(c_name)
        
    temp_b = db.reference('faculty/' + db_name + '/Courses').get()
    batch = []
    keys = list(temp_b.keys())

    for i in range(len(keys)):
        batch.append(db.reference(f'faculty/' + db_name + '/Courses/' + keys[i]).get())
        
    
    return render_template('index_faculty_db.html', prof_name = capitalized_name, course_list = course_list, course_names = course_names, batch = batch)


## need to make changes for faculty database
@app.route('/minor1_analytics')
def minor1_analytics():
    course = request.args.get('course')
    batch = request.args.get('batch')
    branch  =request.args.get('branch')
    path = 'grades/' + batch + '/' +branch + '/' + course
    
    data = db.reference(path).get()
    if data == None:
        return render_template('failure.html')
    
    
    studentID = list(data.keys())
    
    minor1_grades = []
    for i in range(len(studentID)):
        marks = db.reference(path+'/'+studentID[i]).get()
        minor1_grades.append(marks['minor1'])
        
    #top 3 marks
    sorted_array = np.sort(minor1_grades)[::-1]
    
    
        
    
        
    minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
    fig = go.Figure()
    fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
    fig.update_layout(title= "The grade analysis of the course " + course)
    fig.update_layout(showlegend=True)
    Q1 = np.percentile(minor1_grades, 25)
    Q3 = np.percentile(minor1_grades, 75)
        
        #Normal Curve 
    minor1_grades = np.array(minor1_grades)
    avg_m1 = np.mean(minor1_grades)
    std = np.std(minor1_grades)
        
        

        # # Generate x-axis values
    x = np.linspace(minor1_grades.min(), minor1_grades.max(), 100)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - avg_m1) / std) ** 2)

       
       
       
       
       

        # # Plot the bell curve
    fig2 = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Bell Curve'))
    fig2.update_layout(
        title="The normal distribution analysis of the " + course,
        xaxis_title='Marks',
        yaxis_title='Probability Density',
        showlegend=True
    )
    
    sample = np.random.normal(avg_m1, std, len(minor1_grades))

    percentiles = [75, 90, 95]

    counts_above_percentiles = []

    # Calculate the percentiles and the number of values above each percentile
    for percentile in percentiles:
        percentile_value = np.percentile(sample, percentile)
        count_above_percentile = sum(value > percentile_value for value in sample)
        counts_above_percentiles.append(count_above_percentile)
        
        
        # Calculate the percentiles
    colors = ['red', 'blue', 'green']  # Specify colors for each percentile line
    percentiles = [ 75, 90, 95]
    percentile_values = np.percentile(minor1_grades, percentiles)

    for percentile, value, color in zip(percentiles, percentile_values, colors):
        fig2.add_shape(
            type="line",
            xref="x",
            yref="y",
            x0=value,
            x1=value,
            y0=0,
            y1=max(y),
            line=dict(color=color, width=2, dash="dash"),
        )

    # Add invisible scatter traces for legends
        fig2.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(color=color),
                name=f"{percentile}th Percentile"
            )
        )

    fig2.update_layout(showlegend=True)  # Display legends in the graph
    
    
    
    
    
    
    hist, bins = np.histogram(minor1_grades)

    # Find the bin with the highest count
    highest_freq_bin_index = np.argmax(hist)
    highest_freq_count = np.max(hist)

    # Determine the range of the bin with the highest count
    range_start = bins[highest_freq_bin_index]
    range_end = bins[highest_freq_bin_index + 1]

    fig3 = go.Figure(data=[go.Histogram(x=minor1_grades)])

    # Find the index of the bin with the highest count
   

    # Set the color for all bins
    colors = ['lightblue'] * len(hist)

    # Set a different color for the bin with the highest count
    colors[highest_freq_bin_index] = 'red'

    # Update the marker color for the histogram trace
    fig3.update_traces(marker=dict(color=colors))

    fig3.update_layout(title="Histogram of Minor 1 Grades",
                        xaxis_title="Marks",
    yaxis_title="Frequency")
    


        
    graph_json = fig.to_json()
    graph2_json = fig2.to_json()
    graph3_json = fig3.to_json()
    highest = minor1_grades.max()
    lowest = minor1_grades.min()
    
    return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json, graph3_json = graph3_json, avg = avg_m1, highest = highest, lowest = lowest, 
                           course = course, type = 'Minor1', q1 = Q1, q2 = Q3, start = range_start, end = range_end, high_freq_count = highest_freq_count+1,
                           asc = sorted_array, counts = counts_above_percentiles)
    
    
   
@app.route('/minor2_analytics')
def minor2_analytics():
    course = request.args.get('course')
    batch = request.args.get('batch')
    branch  =request.args.get('branch')
    path = 'grades/' + batch + '/' +branch + '/' + course
    
    data = db.reference(path).get()
    
    if data == None:
        return render_template('failure.html')
    
    studentID = list(data.keys())
    
    
    check = db.reference(path+'/'+studentID[0]).get() 
    check = list(check.keys())
    
    if ('minor2' not in check):
        return render_template('failure.html')
    
    minor1_grades = []
    minor2_grades = []
    
    for i in range(len(studentID)):
            
        marks = db.reference(path+'/'+studentID[i]).get()  
          
        if(marks['minor2'] == None):
            return "Minor 2 grades have not been uploaded. Please upload Minor 2 grades"
        
        minor1_grades.append(marks['minor1'])
        minor2_grades.append(marks['minor2'])
        
    sorted_array = np.sort(minor2_grades)[::-1]
        
        
    
    minor1_grades = np.array(minor1_grades)
    minor2_grades = np.array(minor2_grades)
    avg_m1 = np.mean(minor1_grades)
    avg_m2 = np.mean(minor2_grades)
    minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
    minor2_df = pd.DataFrame({'Minor2': np.array(minor2_grades)})
    fig = go.Figure()
    fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
    fig.add_trace(go.Box(y=minor2_df['Minor2'], name="Minor 2"))
    fig.update_layout(showlegend=True)
    
    Q1 = np.percentile(minor2_grades, 25)
    Q3 = np.percentile(minor2_grades, 75)    
        
        
    std = np.std(minor2_grades)
    x = np.linspace(minor2_grades.min(), minor2_grades.max(), 100)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - avg_m1) / std) ** 2)
    fig2 = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Bell Curve'))
    fig2.update_layout(
        title="The normal distribution analysis of the course " + course,
        xaxis_title='Marks',
        yaxis_title='Probability Density',
        showlegend=True
    )
    
    
    sample = np.random.normal(avg_m2, std, len(minor2_grades))

    percentiles = [75, 90, 95]

    counts_above_percentiles = []

    # Calculate the percentiles and the number of values above each percentile
    for percentile in percentiles:
        percentile_value = np.percentile(sample, percentile)
        count_above_percentile = sum(value > percentile_value for value in sample)
        counts_above_percentiles.append(count_above_percentile)
        
        
        # Calculate the percentiles
    colors = ['red', 'blue', 'green']  # Specify colors for each percentile line
    percentiles = [ 75, 90, 95]
    percentile_values = np.percentile(minor2_grades, percentiles)

    for percentile, value, color in zip(percentiles, percentile_values, colors):
        fig2.add_shape(
            type="line",
            xref="x",
            yref="y",
            x0=value,
            x1=value,
            y0=0,
            y1=max(y),
            line=dict(color=color, width=2, dash="dash"),
        )

    # Add invisible scatter traces for legends
        fig2.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(color=color),
                name=f"{percentile}th Percentile"
            )
        )

    
    fig2.update_layout(showlegend=True)  # Display legends in the graph
    
    
    
    
    hist, bins = np.histogram(minor2_grades)

    # Find the bin with the highest count
    highest_freq_bin_index = np.argmax(hist)
    highest_freq_count = np.max(hist)

    # Determine the range of the bin with the highest count
    range_start = bins[highest_freq_bin_index]
    range_end = bins[highest_freq_bin_index + 1]

    fig3 = go.Figure(data=[go.Histogram(x=minor1_grades)])

    # Find the index of the bin with the highest count
   

    # Set the color for all bins
    colors = ['lightblue'] * len(hist)

    # Set a different color for the bin with the highest count
    colors[highest_freq_bin_index] = 'red'

    # Update the marker color for the histogram trace
    fig3.update_traces(marker=dict(color=colors))

    fig3.update_layout(title="Histogram of Minor 2 Grades",
                        xaxis_title="Marks",
    yaxis_title="Frequency",)
        
    # fig3 = go.Figure(data=[go.Histogram(x=minor2_grades)])


    # fig3.update_layout(
    #     title="Histogram for the Minor 2 grades",
    #     xaxis_title="Marks",
    #     yaxis_title="Frequency"
    # )

        
    graph_json = fig.to_json()
    graph2_json = fig2.to_json()
    graph3_json = fig3.to_json()
    highest = minor2_grades.max()
    lowest = minor2_grades.min()
    
    return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json, graph3_json = graph3_json, avg = avg_m2, highest = highest, lowest = lowest, 
                           course = course, type = 'Minor 2', q1 = Q1, q2 = Q3, start = range_start, end = range_end, high_freq_count = highest_freq_count+1,
                           asc = sorted_array,counts = counts_above_percentiles)
    
    
    
    

@app.route('/endsem_analytics')
def endsem_analytics():
    course = request.args.get('course')
    batch = request.args.get('batch')
    branch  =request.args.get('branch')
    path = 'grades/' + batch + '/' +branch + '/' + course
    
    data = db.reference(path).get()
    if data == None:
        return render_template('failure.html')
    
    studentID = list(data.keys())
    
    check = db.reference(path+'/'+studentID[0]).get() 
    check = list(check.keys())
    
    if ('endsem' not in check):
        return render_template('failure.html')
    
    minor1_grades = []
    minor2_grades = []
    end_sem_grades = []
    for i in range(len(studentID)):
        marks = db.reference(path+'/'+studentID[i]).get()
        if(marks['minor1'] == None):
            return "Minor 1 grades have not been uploaded. Please upload Minor1 grades"
        elif (marks['minor2'] == None):
            return "Minor 2 grades have not been uploaded. Please upload Minor2 grades"
            
        minor1_grades.append(marks['minor1'])
        minor2_grades.append(marks['minor2'])
        end_sem_grades.append(marks['endsem'])
        
    sorted_array = np.sort(end_sem_grades)[::-1]
            
    minor1_grades = np.array(minor1_grades)
    minor2_grades = np.array(minor2_grades)
    end_sem_grades = np.array(end_sem_grades)
    avg_m1 = np.mean(minor1_grades)
    avg_m2 = np.mean(minor2_grades)
    avg_endsem = np.mean(end_sem_grades)
    minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
    minor2_df = pd.DataFrame({'Minor2': np.array(minor2_grades)})
    endsem_df = pd.DataFrame({'End Sem': np.array(end_sem_grades)})
    fig = go.Figure()
    fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
    fig.add_trace(go.Box(y=minor2_df['Minor2'], name="Minor 2"))
    fig.add_trace(go.Box(y=endsem_df['End Sem'], name="End Semester"))
    fig.update_layout(showlegend=True)
    Q1 = np.percentile(end_sem_grades, 25)
    Q3 = np.percentile(end_sem_grades, 75)
        
    std = np.std(end_sem_grades)
    x = np.linspace(end_sem_grades.min(), end_sem_grades.max(), 100)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - avg_m1) / std) ** 2)
    fig2 = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Normal dist'))
    fig2.update_layout(
        title="The normal distribution  analysis of the " + course,
        xaxis_title='Marks',
        yaxis_title='Probability Density',
        showlegend=True
    )
    
    sample = np.random.normal(avg_endsem, std, len(end_sem_grades))

    percentiles = [ 75, 90, 95]

    counts_above_percentiles = []

    # Calculate the percentiles and the number of values above each percentile
    for percentile in percentiles:
        percentile_value = np.percentile(sample, percentile)
        count_above_percentile = sum(value > percentile_value for value in sample)
        counts_above_percentiles.append(count_above_percentile)
        
        # Calculate the percentiles
    colors = ['red', 'blue', 'green']  # Specify colors for each percentile line
   
    percentile_values = np.percentile(end_sem_grades, percentiles)

    for percentile, value, color in zip(percentiles, percentile_values, colors):
        fig2.add_shape(
            type="line",
            xref="x",
            yref="y",
            x0=value,
            x1=value,
            y0=0,
            y1=max(y),
            line=dict(color=color, width=2, dash="dash"),
        )

    # Add invisible scatter traces for legends
        fig2.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(color=color),
                name=f"{percentile}th Percentile"
            )
        )

    
    fig2.update_layout(showlegend=True)  # Display legends in the graph
    
    hist, bins = np.histogram(end_sem_grades)

    # Find the bin with the highest count
    highest_freq_bin_index = np.argmax(hist)
    highest_freq_count = np.max(hist)

    # Determine the range of the bin with the highest count
    range_start = bins[highest_freq_bin_index]
    range_end = bins[highest_freq_bin_index + 1]

    fig3 = go.Figure(data=[go.Histogram(x=end_sem_grades)])

    # Find the index of the bin with the highest count
   

    # Set the color for all bins
    colors = ['lightblue'] * len(hist)

    # Set a different color for the bin with the highest count
    colors[highest_freq_bin_index] = 'red'

    # Update the marker color for the histogram trace
    fig3.update_traces(marker=dict(color=colors))

    fig3.update_layout(title="Histogram of End Sem Grades",
                        xaxis_title="Marks",
    yaxis_title="Frequency")
        
        
    graph_json = fig.to_json()
    graph2_json = fig2.to_json()
    graph3_json = fig3.to_json()
    highest = end_sem_grades.max()
    lowest = end_sem_grades.min()
    
    return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json, graph3_json = graph3_json, avg = avg_endsem, highest = highest, lowest = lowest, 
                           course = course, type = 'End Sem', q1 = Q1, q2 = Q3, start = range_start, end = range_end, high_freq_count = highest_freq_count+1,
                           asc = sorted_array, counts = counts_above_percentiles)
    
    


@app.route('/menu_analytics')
def menu_analytics():
    course = request.args.get('course')
    batch = request.args.get('batch')
    if len(batch)>2:
        batch = batch[2:]
    branch = course[:2]
    
    return render_template('menu_grades.html', course = course, batch = batch, branch = branch )
    
   

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=6969)