from flask import Flask, render_template, request, request, redirect, url_for
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import pandas as pd
import logging
import requests
import plotly 
import plotly.tools as plotly_tools
import plotly.graph_objs as go
import plotly.express as px
import re
import numpy as np
# from scipy.stats import norm




app = Flask(__name__)


# Initialize Firebase
cred = credentials.Certificate('Faculty_upload_scores\Faculty Dashboard\se-test-7f7e1-firebase-adminsdk-auhlb-b7b4173ae5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def index():
    return render_template('upload.html')

# @app.route('/upload', methods=['POST'])

@app.route('/analytics')
def analytics(batch, subject_code, exam_type,branch):
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
        fig.update_layout(title="Minor 1 Marks")
        fig.update_layout(showlegend=True)
        
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
            title='Bell Curve',
            xaxis_title='X',
            yaxis_title='Probability Density',
            showlegend=True
        )
        graph_json = fig.to_json()
        graph2_json = fig2.to_json()
        return render_template('graph.html', graph_json = graph_json, graph2_json = graph2_json )
    
    
    
    
    
    
    # MINOR 2 --------------------------------------------------------------------------
    elif exam_type == "minor2":
        minor1_grades = []
        minor2_grades = []
        for i in range(len(studentID)):
            marks = db.reference(path+'/'+studentID[i]).get()
            minor1_grades.append(marks['minor1'])
            minor2_grades.append(marks['minor2'])
        avg_m1 = np.mean(minor1_grades)
        avg_m2 = np.mean(minor2_grades)
        minor1_df = pd.DataFrame({'Minor1': np.array(minor1_grades)})
        minor2_df = pd.DataFrame({'Minor2': np.array(minor2_grades)})
        fig = go.Figure()
        fig.add_trace(go.Box(y=minor1_df['Minor1'], name="Minor 1"))
        fig.add_trace(go.Box(y=minor2_df['Minor2'], name="Minor 2"))
        fig.update_layout(showlegend=True)
        graph_json = fig.to_json()
        return render_template('graph.html', graph_json=graph_json)
    # END SEM --------------------------------------------------------------
    
    
    
    
    
    elif exam_type == "endsem":
        minor1_grades = []
        minor2_grades = []
        end_sem_grades = []
        for i in range(len(studentID)):
            marks = db.reference(path+'/'+studentID[i]).get()
            minor1_grades.append(marks['minor1'])
            minor2_grades.append(marks['minor2'])
            end_sem_grades.append(marks['endsem'])
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
        graph_json = fig.to_json()
        return render_template('graph.html', graph_json=graph_json)
    
    return "Analytics cannot be viewed"


            
            
            
            
        
    
    
    

def upload_to_database(batch, exam_type, file):
    
    csv_file = request.files['file']

    fn_contents = csv_file.filename.split("_")
    
    database_url = 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
    subject_code = fn_contents[0]
    branch = subject_code[:2]
    
    
    
    
    path = 'grades/'+ batch + '/' + branch
    
  
    
    # input = {'subject_code': subject_code}
    # response = requests.put(f'{database_url}/{path}/{subject_code}.json',json = input)




    if csv_file and csv_file.filename.endswith('.csv'):

        df_csv = pd.read_csv(csv_file)

        if exam_type == "minor1":
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                data = {
                    'student_id': student_id,
                    'minor1': int(df_csv['Marks'][i])
                }
                response = requests.put(f'{database_url}/{path}/{subject_code}/{student_id}.json', json=data)
                if response.status_code == 200:
                    continue 
                else:
                    print("Error: Can't add details")


       
        elif exam_type == "minor2":
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                
                # response = requests.put(f'{database_url}/{path}/{subject_code}/{student_id}.json', json=data)
                student_ref = db.reference(str('grades/'+batch+'/'+ subject_code + '/' + student_id))
                student_details = student_ref.get()
                student_details['minor2'] = int(df_csv['Marks'][i])
                student_ref.update(student_details)
                
            
           

        elif exam_type == "endsem":
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                
                # response = requests.put(f'{database_url}/{path}/{subject_code}/{student_id}.json', json=data)
                student_ref = db.reference(str('grades/'+batch+'/'+ subject_code + '/' + student_id))
                student_details = student_ref.get()
                student_details['endsem'] = int(df_csv['Marks'][i])
                student_ref.update(student_details)
                

        
        # firebase_admin.delete_app(firebase_admin.get_app())
        return analytics(batch, subject_code, exam_type, branch)
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
    # return 'Data received: Batch={}, Subject Code={}, File={}'.format(batch, subject_code, file.filename)



if __name__ == '__main__':
    app.run(debug = True)