<img src="brand.jpg" width="400" align="right" />

## CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Requirements
 * Recommended modules
 * Installation
 * Configuration
 * Troubleshooting
 * FAQ
 * Maintainers

## INTRODUCTION
------------

> When i first saw the attendance management system as a topic for the Engage program, instantly the picture of my professors consuming our whole break to take attendance clicked in mind.
> Attendance system through face recognition not only automates the entire process and saves time, but it also reduces the chances of unfare advantage and proxy and can also be further extended to avoid spoof detection.

 MODEL SELECTION
------------
After my initial open cv model failed to differentiate between me and my sister, i went on a quest to search a better model.
After a bit of research on working of open cv and long discussions with ML enthusiasts following points came into my view:
  - Open CV uses machine learning algorithms as old as 7 years.  
  - It does not support fine-tuning and training.
  - It is generally better to let the algorithms determine the intermediate features than to use algorthims to define them explicitly. 

So i choose a model that utilised resnet and MTCNN of pytorch library, which actually did gave me better accuracy at face recognition. After adding and editing functions i was able to utilise the modules of this already developed face recognition model.

I removed the spoof detection utility for smooth functioning and also for judges to be able to login through admin portal through my photo.

 * For a full description of the model, visit the project page:
   https://github.com/hashes-jmi/HackJMI2-CheemsGamg


--------------

SETUP
------------
To run this module on your local device, follow these procedures:

1. Clone this repository by running this command in your terminal/powershell/command prompt
    ```
    git clone https://github.com/uzma024/FaceRec.git
    ```
2. Open the FaceRec folder in vscode and or cd through terminal

3. Now create a virtual environment and activate it
    ```
    python3 -m venv venv (for mac/linux)
    ```
    ```
    . venv/bin/activate  (for mac/linux)
    ```
    or
    ```
    py -3 -m venv venv (for windows)
    ```
    ```
    venv\Scripts\activate  (for windows)
    ```
4. Install the dependencies mentioned in requirement files using conda or pip
    ```
    pip install -r rquirements.txt
    ```
5. run the app.py file using 
    ```
    python app.py (if you are on windows)
    ``` 
     or 
    ```
    python3 app.py (if you are on linux or mac)
    ```
5. cmd + Click on the link to run app server in the browser

--------------
CONFIGURATIONS
------------
 * All files and depencies were made/tested/are functional on mac os and visual studio code ide.
 * But special care was taken to make the app functional in other configurations too.
 * And the testing for same is under progress.

--------------
APP FEATURES
-----------
 * Automation of attendance system.

 * High accuracy of face recognition through deep learning models.

 * It has dual login setup:
    - Student/Public portal for everyone.
    - It gives students access to enter their roll number in database.
    - It then recognises faces corresponding to the roll number and saves it.
    - Able student to view their details in data base through show database.
    - Student can mark their attendance using Face recognition.
    - Date and time of attendance is also recorded.
    - Check attendance of a particular class using class details like Time and Subject.

 * It also has admin portal:
    - Special serial numbers exclusive for admin login.
    - Acess to admin portal is granted using the face recognition. 
    - (Spoof detection was not added so judges can access admin portal through photo)

 * Admin portal has additional functionalities:
    - Student database access, admin can update names and delete students details from database in just one click.
    - Manual Attendence in-case of emergencies, exceptions etc.

 * Attendance management:
    - All the attendance is added in csv files for easy transfer and management.
    - No need to manually check files, one can check them on portal too.
--------------