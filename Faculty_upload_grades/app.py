



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
cred = credentials.Certificate('se-test-7f7e1-firebase-adminsdk-auhlb-b7b4173ae5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
})



@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/upload', methods=['POST'])


def upload_to_database(batch, exam_type, file):

    csv_file = request.files['file']

    fn_contents = csv_file.filename.split("_")
    
    database_url = 'https://se-test-7f7e1-default-rtdb.firebaseio.com/'
    subject_code = fn_contents[0]
    
    
    
    
    path = 'grades/'+batch
    
  
    
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
                
            
           

        else:
            for i in range(len(df_csv)):
                student_id = df_csv['Student_ID'][i]
                
                # response = requests.put(f'{database_url}/{path}/{subject_code}/{student_id}.json', json=data)
                student_ref = db.reference(str('grades/'+batch+'/'+ subject_code + '/' + student_id))
                student_details = student_ref.get()
                student_details['end_sem'] = int(df_csv['Marks'][i])
                student_ref.update(student_details)
                

        
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