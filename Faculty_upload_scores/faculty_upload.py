from flask import Flask, render_template, request, request, redirect, url_for
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import pandas as pd
import logging
import requests
import re


app = Flask(__name__)


# Initialize Firebase
cred = credentials.Certificate('tempproj1-24067-firebase-adminsdk-9c0hq-c879d057e3.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tempproj1-24067-default-rtdb.firebaseio.com/'
})


@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/upload', methods=['POST'])


def upload_to_database(batch, exam_type, file):
    # Upload the csv file to firebase database
    # cred = credentials.Certificate('se-test-7f7e1-firebase-adminsdk-auhlb-b7b4173ae5.json')
    # firebase_admin.initialize_app(cred, {
    #     'databaseURL': 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
    # })
    
    # branch = re.findall(r'[a-zA-Z]+', subject_code)
    # database_url = 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
   
    
    csv_file = request.files['file']

    fn_contents = csv_file.filename.split("_")

    subject_code = fn_contents[0]

    database_url = 'https://tempproj1-24067-default-rtdb.firebaseio.com/'
    path = 'grades/'+batch+'/branch/'+ subject_code

    # file.filename

    if csv_file and csv_file.filename.endswith('.csv'):

        df_csv = pd.read_csv(csv_file)

        if exam_type == "minor1":
        # if "minor1" in file.filename.lower():
            data = []
            for i in range(len(df_csv)):
                student_id = df_csv.iloc[i]['RollNo']
                name = df_csv.iloc[i]['Name']
                m1 = df_csv.iloc[i]['Marks']
                data.append({'student_id': student_id,'m1': m1, 'name':name})
            
            # Store the data in the Firebase Realtime Database
            ref = db.reference('/').child('grades').child(batch).child(subject_code)
            
            for item in data:
                try:
                    ref.child(item['student_id']).set({
                        'name':item['name'],
                        'm1': item['m1']
                    })
                except:
                    continue

        # elif "minor2" in file.filename.lower():
        elif exam_type == "minor2":
            data = []
            for i in range(len(df_csv)):
                student_id = df_csv.iloc[i]['RollNo']
                name = df_csv.iloc[i]['Name']
                m2 = df_csv.iloc[i]['Marks']
                data.append({'student_id': student_id,'m2': m2, 'name':name})
            
            # Store the data in the Firebase Realtime Database
            ref = db.reference('/').child('grades').child(batch).child(subject_code)
            
            for item in data:
                try:
                    ref.child(item['student_id']).set({
                        'name':item['name'],
                        'm2': item['m2']
                    })
                except:
                    continue

        else:
            data = []
            for i in range(len(df_csv)):
                student_id = df_csv.iloc[i]['RollNo']
                name = df_csv.iloc[i]['Name']
                endsem = df_csv.iloc[i]['Marks']
                data.append({'student_id': student_id,'endsem': endsem, 'name':name})
            
            # Store the data in the Firebase Realtime Database
            ref = db.reference('/').child('grades').child(batch).child(subject_code)
            
            for item in data:
                try:
                    ref.child(item['student_id']).set({
                        'name':item['name'],
                        'endsem': item['endsem']
                    })
                except:
                    continue

        
        firebase_admin.delete_app(firebase_admin.get_app())
        return 'Data uploaded successfully!'
    

    else:
        firebase_admin.delete_app(firebase_admin.get_app())
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