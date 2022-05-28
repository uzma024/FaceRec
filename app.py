from flask import Flask, make_response, redirect,render_template, request,redirect,jsonify,url_for
from flask_sqlalchemy import SQLAlchemy
import pyttsx3
import os, cv2

from base64 import b64decode
import uuid
import io
from PIL import Image
from pipeline import register, log,log2,add_to_csv

import pandas as pd
import shutil

app = Flask(__name__)

haarcasecade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Student.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    sno = db.Column(db.String(200),primary_key=True)
    name = db.Column(db.String(200),nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.name}"


@app.route("/",methods=['GET','POST'])
def hello_world():
    
    return render_template("index.html")

@app.route("/capture",methods=['GET','POST'])
def take_image():
    if request.method=="POST":
        sno = request.form['sno']
        name = request.form['name']
        Studentsno = Student.query.filter_by(sno=sno).first()
        print("Take image ",sno,name)
        print(Studentsno)
        if Studentsno == None:
            if sno[0]=='-':     # if sno is negative
                return render_template("message.html",ImgName="present",title="Faliure",message_head="Invalid Rollno" ,message_body='Please enter valid rollno gnot starting with -')
            return render_template('captures.html', sno=sno,name=name)
        else:
            return render_template('message.html',ImgName="present",title="Faliure",message_head="Roll no already present" ,message_body='The user is already registered in the database')
    else:
        return render_template('captures.html')

@app.route('/test-image', methods=['POST'])
def checkImage():
    filename = f'{uuid.uuid4().hex}.jpeg'
    message = request.get_json(force=True)
    encoded = message['image']
    decoded = b64decode(encoded)
    image = Image.open(io.BytesIO(decoded)) 

    sno = message['sno']
    Std_name = message['name']

    print('filename outer: ', filename)
    print('user roll no: ', sno,Std_name)
    foundUser = Student.query.filter_by(sno=sno).first()
    # if user is not fount, add to the database directory
    # print('user roll no: ', foundUser)
    if foundUser == None:
        # New student is being registered
        reg_res = register(image, sno)
        print("foundUser == None :",reg_res)
        new_user = Student(sno=sno,name=Std_name)
        try:
            print('got user roll no: ', sno)
            if reg_res == 'User was successfully registered':
                print("Commiting to db")
                db.session.add(new_user)
                db.session.commit()
            print('filename inner: ', filename)
            print('Registration Response : ', reg_res)
            response = { 'prediction': { 'result': reg_res } }
        except:
            response = { 'prediction': { 'result': 'There is already a user with the same name, try something different' } }
        return jsonify(response)
    elif foundUser.sno == '-1':         
        # Admin login
        log_res = log2(image, sno)
        print("log_res: ",log_res)
        if (type(log_res) == str):
            response = { 'prediction': { 'result': log_res } }
        else:
            print("Login Response: ", log_res)
            response = { 'prediction': { 'result': 'Successfully logged in' } }
        return jsonify(response)
    else:
        # Student sno already in database 
        response = { 'prediction': { 'result': 'There is already a user with the same name, try something different' } }
        return jsonify(response)

@app.route('/test-image-att', methods=['POST'])
def checkImage_att():
    filename = f'{uuid.uuid4().hex}.jpeg'
    message = request.get_json(force=True)
    encoded = message['image']
    decoded = b64decode(encoded)
    image = Image.open(io.BytesIO(decoded)) 

    sno = message['sno']
    Std_name = message['name']
    sub = message['subject']
    print('user roll no: ', sno,Std_name,"Subject: ",sub)
    foundUser = Student.query.filter_by(sno=sno).first()
    print('filename outer: ', filename)

    if foundUser == None:
        render_template("message.html",ImgName="present",title="Faliure",message_head="Roll no not found" ,message_body='The user is not registered in the database')
    else:
        # Student came for attendance
        log_res = log(image, sno,Std_name,sub)
        if (type(log_res) == str):
            print('Login Response: ', log_res)
            response = { 'prediction': { 'result': log_res } }
        else:
            response = { 'prediction': { 'result': 'Successfully logged in' } }
        return jsonify(response)


@app.route("/mark",methods=['GET','POST'])
def mark_attendance():
    if request.method=="POST":
        sub= request.form['subject']
        sno= request.form['Roll']
        student = Student.query.filter_by(sno=sno).first()
        print("student: ",student)
        if student == None:
            return render_template('message.html',ImgName="present",title="Faliure",message_head="Roll number was not found", message='Student Roll number was not found in the database')
        else:
            return render_template('attendance.html',sno=student.sno, name=student.name,subject=sub)
    else:
        return render_template('index.html')

@app.route("/mark-admin",methods=['GET','POST'])
def mark_attendance_admin():
    if request.method=="POST":
        sub= request.form['subject']
        sno= request.form['Roll']
        date=request.form['date']
        time=request.form['time']
        student = Student.query.filter_by(sno=sno).first()
        
        if student == None:
            return render_template('message.html',ImgName="present",title="Faliure",message_head="Roll number was not found", message='Student Roll number was not found in the database')
        else:
            res=add_to_csv(sub,sno,student.name,date,time)
            if res=="Attendance Added":
                return render_template('message.html',ImgName="present",title="Success",message_head="Attendance marked", message='Attendance marked successfully')
            else:
                return render_template('message.html',ImgName="present",title="Faliure",message_head="Attendance not marked", message='Attendance not marked')
    else:
        return redirect("/")

@app.route("/check",methods=['GET','POST'])
def check_att():
    if request.method=="POST":
        sub= request.form['subject']
        date= request.form['date'].split("-")
        time= request.form['time'].split(":")
        print("sub: ",sub)
        print("date: ",date)
        print("time: ",time)
        if time.__len__()==1:
            file_name=sub + '_' +date[0] + '-' +date[1] + '-' +date[2] + '_0' +time[0]+'.csv'
        else:
            file_name=sub + '_' +date[0] + '-' +date[1] + '-' +date[2] + '_' +time[0]+'.csv'
        print("File_name: ",file_name)
        p = os.path.join('Attendance',sub,file_name)
        if os.path.isfile(p):
            data = pd.read_csv(p)
            return render_template('tables.html', tables=[data.to_html()], titles=[''])
    return render_template('message.html',ImgName="present",title="Faliure",message_head="File Not found", message='No attendance records present for the given subject,date and time')
        
  
@app.route("/view")
def view():
    allToStudents = Student.query.all()
    return render_template("view.html",allToStudents=allToStudents)

# ADMIN CONTROL
admin_username = "Uzma"
admin_password =  'Admin$$123'

@app.route('/admin-login', methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        sno= request.form['sno']
        name= request.form['name']
        # student = Student.query.filter_by(sno=sno).first()
        if sno == "-1":
            print(" sno=='-1' ")
            return render_template('admin.html',sno=sno,name=name)
        else:
            return render_template('message.html',ImgName="null",title="Faliure",message_head="Invalid data", message='Roll number does not correspond to admin database')        
    else:
        return render_template('admin.html',sno=-1,name=admin_username)

@app.route("/show-admin")
def show():
    allToStudents = Student.query.all()
    return render_template("show.html",allToStudents=allToStudents)

@app.route("/delete",methods=['GET','POST'])
def delete():
    if request.method=="POST":
        sno= (request.form['sno'])
        if sno == "-1":
            return render_template('message.html',ImgName="null",title="Faliure",message_head="Cannot remove admin", message='Please Enter valid serial number.')        
        temp = Student.query.filter_by(sno=sno).first()

        path = os.path.join('database',temp.sno)
        shutil.rmtree(path, ignore_errors=True)
        # print("Very Dangerous test executed")

        db.session.delete(temp)
        db.session.commit()
    return redirect("/")

@app.route("/update",methods=['GET','POST'])
def update():
    if request.method=="POST":
        sno= (request.form['sno'])
        newName=(request.form['new-name'])
        temp = Student.query.filter_by(sno=sno).first()
        temp.name=newName
        db.session.commit()
    return redirect("/show-admin")

# DELETE FROM DATABASE
@app.route("/delete/<int:sno>")
def delete_from_DB(sno):
    print(sno)
    temp = Student.query.filter_by(sno=sno).first()

    path = os.path.join('database',temp.sno)
    shutil.rmtree(path, ignore_errors=True)
    print("Very Dangerous test executed")

    db.session.delete(temp)
    db.session.commit()
    return redirect("/show-admin")

@app.route('/logout')
def logout():
    """End the current user session"""
    return "Your session was closed", 401

if __name__=="__main__":
    app.run(debug=True)