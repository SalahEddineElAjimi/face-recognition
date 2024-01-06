from flask import Flask, render_template, Response
import cv2
import os
import numpy as np
import pickle
import face_recognition
import cvzone
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, storage
import pandas as pd

app = Flask(__name__)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-734e7-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-734e7.appspot.com"
})

ref = db.reference('Students')

data = {
    "152345": {"name": "Yasser Sorouri", "major": "IDIA", "starting_year": 2020, "total_attendance": 1,
               "standing": "G", "year": 4, "last_attendance_time": "2022-12-11 00:54:34"},
    "412356": {"name": "Zouhair Elamrani", "major": "Proffesor", "starting_year": 2022,
               "total_attendance": 1, "standing": "B", "year": 1, "last_attendance_time": "2022-12-11 00:54:34"},
    "789412": {"name": "Abdenbi Nassereddine", "major": "IDIA", "starting_year": 2020, "total_attendance": 1,
               "standing": "G", "year": 4, "last_attendance_time": "2022-12-11 00:54:34"}
}

for key, value in data.items():
    ref.child(key).set(value)

attendance_df = pd.DataFrame(columns=["Student ID", "Name", "Major", "Year", "Attendance Time"])

def generate_frames():
    folderPath = 'Images'
    pathList = os.listdir(folderPath)
    imgList = []
    studentIds = []

    for path in pathList:
        imgList.append(cv2.imread(os.path.join(folderPath, path)))
        studentIds.append(os.path.splitext(path)[0])

        fileName = f'{folderPath}/{path}'
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)

    def findEncodings(imagesList):
        encodeList = []
        for img in imagesList:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img)

            if face_locations:
                encode = face_recognition.face_encodings(img, face_locations)[0]
                encodeList.append(encode)
            else:
                print("No face found in one or more images.")

        return encodeList

    encodeListKnown = findEncodings(imgList)
    encodeListKnownWithIds = [encodeListKnown, studentIds]

    file = open("EncodeFile.p", "wb")
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

    bucket = storage.bucket()

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    imgBackground = cv2.imread('Resources/background.png')
    folderModePath = 'Resources/Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = []

    for path in modePathList:
        imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

    file = open('EncodeFile.p', 'rb')
    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown, studentIds = encodeListKnownWithIds

    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    while True:
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                blob = bucket.get_blob(f'Images/{id}.png')

                if blob is not None:
                    blob_content = blob.download_as_bytes()
                    imgStudent = cv2.imdecode(np.frombuffer(blob_content, np.uint8), cv2.COLOR_BGRA2BGR)

                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                       
                        attendance_df.loc[len(attendance_df)] = [id,
                                                                 studentInfo['name'],
                                                                 studentInfo['major'],
                                                                 studentInfo['year'],
                                                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                else:
                    print(f'Blob for student {id} does not exist.')

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    if isinstance(imgStudent, list):
                        imgStudent = np.array(imgStudent)

                    if imgStudent.size != 0:
                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

            counter += 1

            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        else:
            modeType = 0
            counter = 0

        ret, jpeg = cv2.imencode('.jpg', imgBackground)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/export_attendance')
def export_attendance():
    attendance_df.to_excel("attendance_logn.xlsx", index=False)
    return "Attendance exported to attendance_login.xlsx"
    

if __name__ == '__main__':
    app.run(debug=True, port=8080)
