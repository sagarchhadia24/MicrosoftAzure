"""
Routes and views for the flask application.
"""

from flask import render_template
# from FlaskWebProject import app
# from pymongo import MongoClient
import mysql.connector
from flask import request
import base64
import time
import datetime


fileLimit = 15
sizeLimit = 1
subjectLimit = 100
username = None


# DataBase Connection
class MongoDB():
    def __init__(self):
        client = MongoClient('mongodb://ds011765.mlab.com:11765')
        self.db = client['sagarazuredb']
        self.db.authenticate('sagar','123')

    def get_collection(self,collection_name):
        return self.db[collection_name]


print "DB Connected Successfully"


@app.route('/')
def index():
    return render_template('login.html')


# Login Page
@app.route('/login', methods=['GET','POST'])
def do_admin_login():

    startTime = timeBeforeEvent()
    if request.method == 'GET':
        return render_template('login.html')
    global username
    User_Name = request.form['username']
    Password = request.form['password']
    username = User_Name
    client=MongoDB()
    ImageCol=client.get_collection('Users')
    query = ImageCol.find({"username": User_Name})
    for post in query:
        if post['password'] == Password:
            # data = User_Name
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Login : ' + totalTimeTaken

            return render_template('index.html', Time = message, user = username)
            #return render_template('welcome.html', Time = message)

        else:
            data = "Invalid Login"
            return render_template('login.html')


# Index (Home) Page
@app.route('/home')
def home():
    """Renders the home page."""
    global username
    return render_template('index.html',title='Home Page',  user = username)


# About Page
@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html', title='About', message='Project description page.')


# Upload Image/Document
@app.route('/uploadimage', methods=['POST', 'GET'])
def uploadimage():
    if request.method == 'POST':
        try:
            global username
            username1 = request.form['username']
            startTime = timeBeforeEvent()
            currentDate1 = datetime.datetime.now()
            currentDate = str(currentDate1)
            file_name = request.files['file_upload'].filename
            content = request.files['file_upload'].read()
            FileExtensionTxt = file_name.endswith(".txt")
            sizeOfFileTmp = str(content)
            sizeOfFile = len(sizeOfFileTmp)/1048567
            print sizeOfFile
            Subjecttmp = request.form['Subject']
            Subject = str(Subjecttmp)
            Prioritytmp = request.form['PriorityNumber']
            Priority = int(Prioritytmp)

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            count = ImageCollection.find({"username": username}).count()

            # Setting Content field according to Image/Text file
            if count < fileLimit and sizeOfFile < sizeLimit:
                if not FileExtensionTxt:
                    ImgData = base64.b64encode(content)
                    postfile = {
                        "username" : username1,
                        "ImgContent" : ImgData,
                        "DocContent" : None,
                        "filename" : file_name,
                        "Date" : currentDate,
                        "Subject" : Subject,
                        "Priority" : Priority}
                else:
                    DocData = content
                    postfile = {
                        "username": username1,
                        "ImgContent": None,
                        "DocContent": DocData,
                        "filename": file_name,
                        "Date": currentDate,
                        "Subject": Subject,
                        "Priority": Priority}

                client = MongoDB()
                ImageCollection = client.get_collection('AllFiles')
                post_id = ImageCollection.insert(postfile)
                endTime = timeAfterEvent()
                totalTimeTaken = totalTime(startTime, endTime)
                message = 'Time to Upload File : ' + totalTimeTaken
                result = "File Successfully Uploaded"
                return render_template("index.html", output = result, Time = message, user = username1)
            else:
                result = "Limit Exceeded\Too Large File"
                return render_template("index.html", output = result, user = username1)
        except:
            result = "Upload failed"
        return render_template("index.html", output = result)


# Display All Files
@app.route('/getallfiles', methods=['POST', 'GET'])
def getallfiles():
    try:
        global username
        if request.method == 'POST':
            username = request.form['username']
        else:
            username = username
        startTime = timeBeforeEvent()

        # Initializing object of the database class
        client = MongoDB()
        ImageCollection = client.get_collection('AllFiles')
        query = ImageCollection.find({"username": username})

        # Fetching data from the query and sending it to HTML file in Json format
        returnString = []
        for post in query:
            IMGData = post['ImgContent']
            DocData = post['DocContent']
            ImgSubject = post['Subject']
            ImgPriority = post['Priority']
            user_name = post['username']
            File_name = post['filename']
            Current_DateTime = post['Date']
            if IMGData == None:
                picdata = None
            else:
                picdata = "data:image/jpeg;base64," + IMGData

            SendData = {"ImageData": picdata,
                        "DocData": DocData,
                        "Subject": ImgSubject,
                        "Priority": ImgPriority,
                        "User Name": user_name,
                        "File Name": File_name,
                        "TimeStamp": Current_DateTime}
            returnString.append(SendData)
        endTime = timeAfterEvent()
        totalTimeTaken = totalTime(startTime, endTime)
        message = 'Time to Fetch All Files From DataBase : ' + totalTimeTaken
        return render_template("getallfiles.html", output=returnString, Time=message)
    except:
        result = "Fail to list images"
        return render_template("index.html", output=result)


# Sort All Files As Option Selection
@app.route('/sortallfiles', methods=['POST', 'GET'])
def sortallfiles():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            sortCategory = request.form['sortCat']
            sortType = int(request.form['sortOrder'])

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"username": username}).sort([(sortCategory, sortType)])

            # Fetching data from the query and sending it to HTML file in Json format
            returnString = []
            for post in query:
                IMGData = post['ImgContent']
                DocData = post['DocContent']
                ImgSubject = post['Subject']
                ImgPriority = post['Priority']
                user_name = post['username']
                File_name = post['filename']
                Current_DateTime = post['Date']
                if IMGData == None:
                    picdata = None
                else:
                    picdata = "data:image/jpeg;base64," + IMGData

                SendData = {"ImageData": picdata,
                            "DocData": DocData,
                            "Subject": ImgSubject,
                            "Priority": ImgPriority,
                            "User Name": user_name,
                            "File Name": File_name,
                            "TimeStamp": Current_DateTime}
                returnString.append(SendData)
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Sort All Files : ' + totalTimeTaken
            return render_template("getallfiles.html", output=returnString, Time=message)
        except:
            result = "Fail to list images"
            return render_template("index.html", output=result)


# View Image Page
@app.route('/getmypictures', methods=['POST', 'GET'])
def getmypictures():
    try:
        global username
        if request.method == 'POST':
            username = request.form['username']
        else:
            username = username
        startTime = timeBeforeEvent()
        client = MongoDB()
        ImageCollection = client.get_collection('AllFiles')
        query = ImageCollection.find({"username": username})

        returnString = []
        for post in query:
            IMGData = post['ImgContent']
            DocData = post['DocContent']
            ImgSubject = post['Subject']
            ImgPriority = post['Priority']
            user_name = post['username']
            File_name = post['filename']
            Current_DateTime = post['Date']
            if IMGData == None:
                picdata = None
            else:
                picdata = "data:image/jpeg;base64," + IMGData
                SendData = { "ImageData" : picdata,
                         "DocData" : DocData,
                         "Subject" : ImgSubject,
                         "Priority" : ImgPriority,
                         "User Name" : user_name,
                         "File Name" : File_name,
                         "TimeStamp" : Current_DateTime }
                returnString.append(SendData)
        endTime = timeAfterEvent()
        totalTimeTaken = totalTime(startTime, endTime)
        message = 'Time to Fetch All Images From DataBase : ' + totalTimeTaken
        return render_template("getallimages.html", output = returnString, Time = message)
    except:
        result = "Fail to list images"
        return render_template("index.html", output = result)


# Sort Image As option selection
@app.route('/sortmypictures', methods=['POST', 'GET'])
def sortmypictures():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            sortCategory = request.form['sortCat']
            sortType = int(request.form['sortOrder'])

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"username": username}).sort([(sortCategory , sortType)])

            returnString = []
            for post in query:
                IMGData = post['ImgContent']
                DocData = post['DocContent']
                ImgSubject = post['Subject']
                ImgPriority = post['Priority']
                user_name = post['username']
                File_name = post['filename']
                Current_DateTime = post['Date']
                if IMGData == None:
                    picdata = None
                else:
                    picdata = "data:image/jpeg;base64," + IMGData
                    SendData = {"ImageData": picdata,
                                "DocData": DocData,
                                "Subject": ImgSubject,
                                "Priority": ImgPriority,
                                "User Name": user_name,
                                "File Name": File_name,
                                "TimeStamp": Current_DateTime}
                    returnString.append(SendData)
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Sort All Images : ' + totalTimeTaken
            return render_template("getallimages.html", output=returnString, Time=message)
        except:
            result = "Fail to list images"
            return render_template("index.html", output=result)

# View Document Page
@app.route('/getmydocuments', methods=['POST', 'GET'])
def getmydocuments():
    try:
        global username
        if request.method == 'POST':
            username = request.form['username']
        else:
            username = username
        startTime = timeBeforeEvent()

        # Initializing object of the database class
        client = MongoDB()
        ImageCollection = client.get_collection('AllFiles')
        query = ImageCollection.find({"username": username})

        returnString = []
        for post in query:
            IMGData = post['ImgContent']
            DocData = post['DocContent']
            ImgSubject = post['Subject']
            ImgPriority = post['Priority']
            user_name = post['username']
            File_name = post['filename']
            Current_DateTime = post['Date']
            if IMGData == None:
                picdata = None
                SendData = {"ImageData": picdata,
                            "DocData": DocData,
                            "Subject": ImgSubject,
                            "Priority": ImgPriority,
                            "User Name": user_name,
                            "File Name": File_name,
                            "TimeStamp": Current_DateTime}
                returnString.append(SendData)
            else:
                picdata = "data:image/jpeg;base64," + IMGData

        endTime = timeAfterEvent()
        totalTimeTaken = totalTime(startTime, endTime)
        message = 'Time to Fetch All Documents From DataBase : ' + totalTimeTaken
        return render_template("getalldocuments.html", output=returnString, Time=message)
    except:
        result = "Fail to list images"
        return render_template("index.html", output=result)


# Sort Documents As option selection
@app.route('/sortmydocuments', methods=['POST', 'GET'])
def sortmydocuments():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            sortCategory = request.form['sortCat']
            sortType = int(request.form['sortOrder'])

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"username": username}).sort([(sortCategory , sortType)])

            returnString = []
            for post in query:
                IMGData = post['ImgContent']
                DocData = post['DocContent']
                ImgSubject = post['Subject']
                ImgPriority = post['Priority']
                user_name = post['username']
                File_name = post['filename']
                Current_DateTime = post['Date']
                if IMGData == None:
                    picdata = None
                    SendData = {"ImageData": picdata,
                                "DocData": DocData,
                                "Subject": ImgSubject,
                                "Priority": ImgPriority,
                                "User Name": user_name,
                                "File Name": File_name,
                                "TimeStamp": Current_DateTime}
                    returnString.append(SendData)
                else:
                    picdata = "data:image/jpeg;base64," + IMGData

            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Sort All Documents : ' + totalTimeTaken
            return render_template("getalldocuments.html", output=returnString, Time=message)
        except:
            result = "Fail to list images"
            return render_template("index.html", output=result)


# Delete All Image/Document
@app.route('/deleteall', methods=['POST', 'GET'])
def deleteall():
    if request.method == 'POST':
        try:
            print "Entered into Del All"
            global username
            startTime = timeBeforeEvent()

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            #query = ImageCollection.remove({"username": username})
            print "query executed"

            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Delete All : ' + totalTimeTaken
            result = "Deleted All "
            return render_template("index.html", output = result, Time = message)
        except:
            result = "Fail to delete images"
            return render_template("index.html", output = result)


# Delete Single Image/Document
@app.route('/deletepicture', methods=['POST', 'GET'])
def deletepicture():
    startTime = timeBeforeEvent()
    User_Name = request.form['username']
    File_Name = request.form['filename']
    try:
        if User_Name == username:
            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.remove({"username": User_Name, "filename": File_Name})
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Delete File : ' + totalTimeTaken
            result = 'File Deleted'
            return render_template("index.html", output = result, Time = message)
        else:
            result = 'Cannot delete file of other user'
            return render_template("index.html", output = result)
    except:
        result = "Fail to delete file"
        return render_template("index.html", output = result)


# Update Subject
@app.route('/updateSubject', methods=['POST', 'GET'])
def updateSubject():
    try:
        User_Name = request.form['username']
        File_Name = request.form['filename']
        Subject_Update = request.form['updatesubject']

        # Initializing object of the database class
        client = MongoDB()
        ImageCollection = client.get_collection('AllFiles')
        query = ImageCollection.update({"username": User_Name, "filename": File_Name},{"$set": {"Subject": Subject_Update}})
        result = "Subject Successfully Updated"
    except:
        result = "Failed to update subject"
    return render_template("index.html", output = result)


# Update Priority
@app.route('/updatePriority', methods=['POST', 'GET'])
def updatePriority():
    try:
        User_Name = request.form['username']
        File_Name = request.form['filename']
        Priority_Update = request.form['updatepriority']

        client = MongoDB()
        ImageCollection = client.get_collection('AllFiles')
        query = ImageCollection.update({"username": User_Name, "filename": File_Name},{"$set": {"Priority": Priority_Update}})
        result = "Priority Successfully Updated"
    except:
        result = "Failed to update Priority"
    return render_template("index.html", output = result)


# Search a specific word in all the .txt file in database
@app.route('/wordsearch', methods=['POST', 'GET'])
def wordsearch():
    if request.method == 'POST':
        try:
            startTime = timeBeforeEvent()
            Docs = []

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"DocContent" : {"$regex" : request.form['WordInput']}})

            for post in query:
                Data = post['DocContent']
                Docs.append(Data)
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time taken to search word in all files : ' + totalTimeTaken + "<br><br><br><br>"
            return  message + str(Docs)
        except:
            result = "Fail to list Words"
            return render_template("index.html", output= result)


# Search files based on subjects
@app.route('/subjectsearch', methods=['POST', 'GET'])
def subjectsearch():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            fileSub = request.form['SubInput']
            print fileSub


            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"Subject": fileSub})

            # Fetching data from the query and sending it to HTML file in Json format
            returnString = []
            for post in query:
                IMGData = post['ImgContent']
                DocData = post['DocContent']
                ImgSubject = post['Subject']
                ImgPriority = post['Priority']
                user_name = post['username']
                File_name = post['filename']
                Current_DateTime = post['Date']
                if IMGData == None:
                    picdata = None
                else:
                    picdata = "data:image/jpeg;base64," + IMGData

                SendData = {"ImageData": picdata,
                            "DocData": DocData,
                            "Subject": ImgSubject,
                            "Priority": ImgPriority,
                            "User Name": user_name,
                            "File Name": File_name,
                            "TimeStamp": Current_DateTime}
                returnString.append(SendData)
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Fetch All Files : ' + totalTimeTaken
            return render_template("getallfiles.html", output=returnString, Time=message)
        except:
            result = "Fail to list images"
            return render_template("index.html", output=result)


# Search files greater than/equal to given priority
@app.route('/prioritysearch', methods=['POST', 'GET'])
def prioritysearch():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            filePrio = int(request.form['PrioInput'])

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            #query = ImageCollection.find({"Priority": filePrio})
            query = ImageCollection.find({"username": username})

            # Fetching data from the query and sending it to HTML file in Json format
            returnString = []
            for post in query:
                IMGData = post['ImgContent']
                DocData = post['DocContent']
                ImgSubject = post['Subject']
                ImgPriority = post['Priority']
                user_name = post['username']
                File_name = post['filename']
                Current_DateTime = post['Date']
                if IMGData == None:
                    picdata = None
                else:
                    picdata = "data:image/jpeg;base64," + IMGData

                if ImgPriority >= filePrio:
                    SendData = {"ImageData": picdata,
                                "DocData": DocData,
                                "Subject": ImgSubject,
                                "Priority": ImgPriority,
                                "User Name": user_name,
                                "File Name": File_name,
                                "TimeStamp": Current_DateTime}
                    returnString.append(SendData)
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Fetch All Files : ' + totalTimeTaken
            return render_template("getallfiles.html", output=returnString, Time=message)
        except:
            result = "Fail to list images"
            return render_template("index.html", output=result)


# Display files less than/equal to given time (in Minutes)
@app.route('/displayfilesgiventime', methods=['POST', 'GET'])
def displayfilesgiventime():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            userInputMin = int(request.form['DisplayMinInput'])

            currentTimeMin = datetime.datetime.now().minute
            print "currentTimeMin %d" % currentTimeMin

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"username": username})

            # Fetching data from the query and sending it to HTML file in Json format
            returnString = []
            for post in query:
                IMGData = post['ImgContent']
                DocData = post['DocContent']
                ImgSubject = post['Subject']
                ImgPriority = post['Priority']
                user_name = post['username']
                File_name = post['filename']
                Current_DateTime = post['Date']
                if IMGData == None:
                    picdata = None
                else:
                    picdata = "data:image/jpeg;base64," + IMGData

                uploadTimeMin = int(Current_DateTime[14:16])
                print "uploadTimeMin %d" % uploadTimeMin
                timeDiffMin = currentTimeMin - uploadTimeMin
                print "timeDiffMin %d" % timeDiffMin

                if 0 <= timeDiffMin <= userInputMin:
                    print "Display File"
                    SendData = {"ImageData": picdata,
                                "DocData": DocData,
                                "Subject": ImgSubject,
                                "Priority": ImgPriority,
                                "User Name": user_name,
                                "File Name": File_name,
                                "TimeStamp": Current_DateTime}
                    returnString.append(SendData)
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Display All Files : ' + totalTimeTaken
            return render_template("getallfiles.html", output=returnString, Time=message)
        except:
            result = "Fail to list images"
            return render_template("index.html", output=result)


# Delete files less than/equal to given time (in Minutes)
@app.route('/deletefilesgiventime', methods=['POST', 'GET'])
def deletefilesgiventime():
    if request.method == 'POST':
        try:
            global username
            startTime = timeBeforeEvent()
            userInputMin = int(request.form['DeleteMinInput'])

            currentTimeMin = datetime.datetime.now().minute
            print "currentTimeMin %d" % currentTimeMin

            # Initializing object of the database class
            client = MongoDB()
            ImageCollection = client.get_collection('AllFiles')
            query = ImageCollection.find({"username": username})

            # Fetching data from the query and sending it to HTML file in Json format
            returnString = []
            for post in query:
                File_name = post['filename']
                Current_DateTime = post['Date']

                uploadTimeMin = int(Current_DateTime[14:16])
                print "uploadTimeMin %d" % uploadTimeMin
                timeDiffMin = currentTimeMin - uploadTimeMin
                print "timeDiffMin %d" % timeDiffMin

                if timeDiffMin < 0 or timeDiffMin > userInputMin:
                    print "Dellete File"
                    deletequery = ImageCollection.remove({"username": username, "filename": File_name})
            endTime = timeAfterEvent()
            totalTimeTaken = totalTime(startTime, endTime)
            message = 'Time to Delete All Files : ' + totalTimeTaken
            return render_template("getallfiles.html", output=returnString, Time=message)
        except:
            result = "Fail to delete images"
            return render_template("index.html", output=result)

# Calculating time
def timeBeforeEvent():
    Time_Before_Upload = time.time()
    return Time_Before_Upload

def timeAfterEvent():
    Time_After_Upload = time.time()
    return Time_After_Upload

def totalTime(Time_Before_Upload, Time_After_Upload):
    Difference_In_Times = Time_After_Upload - Time_Before_Upload
    Minutes = datetime.datetime.fromtimestamp(Difference_In_Times).minute
    Seconds = datetime.datetime.fromtimestamp(Difference_In_Times).second
    MicroSeconds = datetime.datetime.fromtimestamp(Difference_In_Times).microsecond
    returnTime = '{} min {} sec {} microsec'.format(Minutes, Seconds, MicroSeconds)
    return returnTime