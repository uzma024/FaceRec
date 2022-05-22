from flask import Flask, redirect,render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
import pyttsx3
import os, cv2
import datetime
import time

import pandas as pd

# project module
import show_attendance
import takeImage
import trainImage
import automaticAttedance

def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()

app = Flask(__name__)

haarcasecade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
trainimagelabel_path = "/Users/uzmafirozkhan/Desktop/AttendanceFinal/TrainingImageLabel/Trainner.yml"
trainimage_path = "/Users/uzmafirozkhan/Desktop/AttendanceFinal/TrainingImage"
studentdetail_path = "/Users/uzmafirozkhan/Desktop/AttendanceFinal/StudentDetails/studentdetails.csv"
attendance_path = "/Users/uzmafirozkhan/Desktop/AttendanceFinal/Attendance"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Student.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    # age = db.Column(db.Integer,nullable=False)
    # date_created = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.name}"


@app.route("/",methods=['GET','POST'])
def hello_world():
    
    return render_template("index.html")

@app.route("/capture",methods=['GET','POST'])
def take_image():
    if request.method=="POST":
        sno= (request.form['sno'])
        name = request.form['name']
        takeImage.TakeImage(
            sno,
            name,
            haarcasecade_path,
            trainimage_path,
            text_to_speech
        )
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            text_to_speech,
        )
        newStd =Student(sno=sno, name=name)
        db.session.add(newStd)
        db.session.commit()
    return redirect("/show")

@app.route("/mark",methods=['GET','POST'])
def mark_attendance():
    print("inside Mark Att Function")
    sub= (request.form['subject'])
    automaticAttedance.subjectChoose(text_to_speech,sub)
    return redirect("/")


@app.route("/show")
def show():
    allToStudents = Student.query.all()
    return render_template("show.html",allToStudents=allToStudents)

@app.route("/delete",methods=['GET','POST'])
def delete():
    if request.method=="POST":
        sno= (request.form['sno'])
        temp = Student.query.filter_by(sno=sno).first()
        db.session.delete(temp)
        db.session.commit()
        print(sno+" Deleted")
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)