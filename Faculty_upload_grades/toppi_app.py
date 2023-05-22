from flask import Flask, render_template, request, request, redirect, url_for
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import pandas as pd

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate('tempproj1-24067-firebase-adminsdk-9c0hq-c879d057e3.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tempproj1-24067-default-rtdb.firebaseio.com/'
})

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])


# def upload():
#       # get the uploaded file
#       uploaded_file = request.files['file']
#       if uploaded_file.filename != '':
#            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
#           # set the file path
#            uploaded_file.save(file_path)
#           # save the file
#       return redirect(url_for('index'))

def upload():

    csv_file = request.files['file']

    if csv_file and csv_file.filename.endswith('.csv'):

        df_csv = pd.read_csv(csv_file)
        data = []
        for i in range(len(df_csv)):
            student_id = df_csv.iloc[i]['RollNo']
            name = df_csv.iloc[i]['Name']
            marks = df_csv.iloc[i]['Marks']
            data.append({'student_id': student_id, 'name': name, 'marks': marks})
        
        # Store the data in the Firebase Realtime Database
        ref = db.reference('students3')
        for item in data:
            try:
                ref.child(item['student_id']).set({
                    'name': item['name'],
                    'marks': item['marks']
                })
            except:
                continue
        
        firebase_admin.delete_app(firebase_admin.get_app())
        return 'Data uploaded successfully!'
    
    else:
        firebase_admin.delete_app(firebase_admin.get_app())
        return 'Invalid file format. Please upload a CSV file.'



# print(type(csv_file))

    # if csv_file and csv_file.filename.endswith('.csv'):
    #     # Read and process the CSV file
    #     data = []
    #     # csv_reader = csv.DictReader(csv_file)
    #     # csv_reader  = csv_file
    #     # csvfile = TextIOWrapper(request.files['portfolios'], encoding=request.encoding)

        
    #     for row in csv_file:
    #         print(row, flush=True)
    #         student_id = row['RollNo']
    #         name = row['Name']
    #         marks = row['Marks']
    #         data.append({'student_id': student_id, 'name': name, 'marks': marks})
        
    #     # Store the data in the Firebase Realtime Database
    #     ref = db.reference('students2')
    #     for item in data:
    #         ref.child(item['student_id']).set({
    #             'name': item['name'],
    #             'marks': item['marks']
    #         })
        
    #     firebase_admin.delete_app(firebase_admin.get_app())
    #     return 'Data uploaded successfully!'
    # else:
    #     firebase_admin.delete_app(firebase_admin.get_app())
    #     return 'Invalid file format. Please upload a CSV file.'
    



if __name__ == '__main__':
    app.run(debug = True)
