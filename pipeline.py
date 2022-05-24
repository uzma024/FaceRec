from PIL import Image
import os
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
from torch.utils.data import DataLoader
# from sp_model import realvfake
from torchvision import datasets
import matplotlib.pyplot as plt
import torch

import datetime
import time
import pandas as pd

#n_faces_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
mtcnn = MTCNN(image_size=240, margin=20,  post_process=False, keep_all=True, min_face_size=20) #initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval()
mtcnn2 = MTCNN(image_size=240, margin=0, min_face_size=20) 

def face_match(img): 
    face, prob = mtcnn2(img, return_prob=True) 
    emb = resnet(face.unsqueeze(0)).detach() # detech is to make required gradient false
    
    saved_data = torch.load('data.pt') # loading data.pt file
    embedding_list = saved_data[0] # getting embedding data
    name_list = saved_data[1] # getting list of names
    dist_list = [] # list of matched distances, minimum distance is used to identify the person
     
    for emb_db in embedding_list:
        dist = torch.dist(emb, emb_db).item()
        dist_list.append(dist)
    
    data = [embedding_list, name_list]
    torch.save(data, 'data.pt') 

    idx_min = dist_list.index(min(dist_list))
    for name, dist in zip(name_list, dist_list):
        print('Name: '+name+' Distance: '+str(dist))
    #print(name_list[idx_min], min(dist_list))
    if min(dist_list) <0.80: #0.84 is the min threshold for face recognition
        return (name_list[idx_min], min(dist_list))
    else:
        return False

def register(image, user):  
    update_embeddings()
    faces, probs = mtcnn(image, return_prob=True) #Face Detection
    #Checking number of face detections
    if faces == None:
        return 'No Face Detected'
    #print("Faces tensor shape: ", faces.shape)
    for face, prob in zip(faces, probs):
        if prob<0.80:
            faces.remove(face)

    if faces == None:
        return 'No Face Detected'        
    elif faces.shape[0] > 1:
        return 'Multiple Faces Detected'

    face = faces[0]
    fname = 'temp.jpg'
    img = face.permute(1, 2, 0).int().numpy().astype('uint8')
    plt.imsave(fname, img)
    # if realvfake(fname):
    if not face_match(image):
        directory = os.path.join('database',user)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        plt.imsave(os.path.join(directory,'crop'+'.jpeg'), img)
        return 'User was successfully registered'
    else:
        print("exiting user:",image)
        return 'Face Matched with existing user'
    # else:
    #     return 'Fake Face Detected'


def update_embeddings():
    dataset=datasets.ImageFolder('database')
    idx_to_class = {i:c for c,i in dataset.class_to_idx.items()} 

    def collate_fn(x):
        return x[0]

    loader = DataLoader(dataset, collate_fn=collate_fn)

    name_list = [] 
    embedding_list = [] 

    for img, idx in loader:
        face, prob = mtcnn2(img, return_prob=True) 
        if face is not None and prob>0.90: 
            emb = resnet(face.unsqueeze(0)) 
            embedding_list.append(emb.detach()) 
            name_list.append(idx_to_class[idx]) 

    data = [embedding_list, name_list]
    torch.save(data, 'data.pt')

def add_to_csv(subject,user_sno,user_name):
    # Add name to attendance list
    print("Subject:",subject)
    path=os.path.join('/Users/uzmafirozkhan/Desktop/AttendanceFinal/Attendance/',subject)
    if not os.path.isdir(path):
        os.mkdir(path)
    # GET DATE AND TIME
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    Hour, Minute, Second = timeStamp.split(":")
    # Assuming each class is of not more than 1 hr
    # i.e. different hr means different class of same day
    fileName = (
        f"{path}/"
        + subject
        + "_"
        + date
        + "_"
        + Hour
        + ".csv"
    )
    # take out student name
    # studentdetail_path = "/Users/uzmafirozkhan/Desktop/AttendanceFinal/StudentDetails/studentdetails.csv"
    # df = pd.read_csv(studentdetail_path)
    # Student_sno = df.loc[df["Enrollment"] == Student_sno]["Name"].values
    # Data of file
    col_names = ["Enrollment number", "Name","Date", "Time"]
    attendance = pd.DataFrame(columns=col_names)
    attendance.loc[len(attendance)] = [user_sno,user_name,date,timeStamp]
    attendance.to_csv(fileName, index=False)


def log(image, user_sno ,user_name,subject):
    faces, probs = mtcnn(image, return_prob=True)
    update_embeddings()

    if faces == None:
        return 'No Face Detected'

    for face, prob in zip(faces, probs):
        if prob<0.80:
            faces.remove(face)

    if faces == None:
        return 'No Face Detected'        
    elif faces.shape[0] > 1:
        return 'Multiple Faces Detected'

    face = faces[0]
    fname = 'temp.jpg'
    img = face.permute(1, 2, 0).int().numpy().astype('uint8')
    plt.imsave(fname, img)
    # if realvfake(fname):
    out = face_match(image)
    if out == False:
        return 'No Match Found'
    else:
        if out[0] != user_sno:
            return 'No Match Found'
        else:
        # Add name to attendance list
            add_to_csv(subject,user_sno,user_name)
            return out
    # else:
    #     return 'Fake Face Detected'