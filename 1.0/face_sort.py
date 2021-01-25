import cmake
import cv2
import face_recognition
import os
from shutil import copy2

def SortAllImage():
    AllImages = os.listdir('./All')
    result = {}     #{key:(enc,[list of all images that matchs this enc.])}
    for image in AllImages:
        img = face_recognition.load_image_file('./All/'+image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        facedata_list = face_recognition.face_encodings(img)
        for facedata in facedata_list:
            check=0
            for key,value in result.items():
                if face_recognition.compare_faces([facedata,],value[0])[0]:
                    result[key][1].append(image)
                    check =1
                    break
                else:
                    check =0
            if check==0:
                result['face'+str(len(result))]=(facedata,[image,])
    for key in result:
        if not os.path.exists('./'+key+'/'):
            os.mkdir('./'+key+'/')
        for image in result[key][1]:
            copy2('./All/'+image  ,'./'+key+'/')
    print('Done')

def SearchByFaceEncoding(facedata,name):
    AllImages = os.listdir('./All')
    copy_count = 0
    for image in AllImages:
        img = face_recognition.load_image_file('./All/'+image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        facedata_list = face_recognition.face_encodings(img)
        if not os.path.exists('./'+name+'/'):
            os.mkdir('./'+name+'/')
        for face in facedata_list:
            if face_recognition.compare_faces(facedata,face)[0]:
                copy2('./All/'+image  ,'./'+name+'/')
                copy_count+=1
                break
    if copy_count!=0:
        print('Copied...')
    else:
        print('None of files contains this face')
        os.rmdir('./'+name+'/')

def SearchByCam():
    try:
        cam = cv2.VideoCapture(0)                 # later we change it to camera id
        frame = cam.read()[1]
        cam.release()
        cv2.imwrite('temp.jpg',frame)
        img = face_recognition.load_image_file('temp.jpg')
        os.remove('temp.jpg')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        facedata = face_recognition.face_encodings(img) 
        length=len(facedata)
        if length == 1:
            name = input('Enter Folder Name To which copy the Files:  ')
            SearchByFaceEncoding(facedata,name)
        elif length==0:
            print('No Face Found')
        elif length>1:
            print('More Than one Face Detected')
        else:
            print('Some Error Occur')
    except Exception as E:
        print(E.__str__())
        
def SearchByImage(filename):
    try:
        img = face_recognition.load_image_file(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        facedata = face_recognition.face_encodings(img) 
        length=len(facedata)
        if length == 1:
            name = input('Enter Folder Name To which copy the Files:  ')
            SearchByFaceEncoding(facedata,name)
        elif length==0:
            print('No Face Found')
        elif length>1:
            print('More Than one Face Detected')
        else:
            print('Some Error Occur')
    except Exception as E:
        print(E.__str__())
        

def main():
    print('WELCOME FACE_SORTING')
    print('1. Search a Face')
    print('2. Sort all Images')
    print('Enter Your choice')
    choice_1 = int(input())
    if choice_1 == 1:
        print('\nEnter Choice: ')
        print('1. Capture Image')
        print('2. Load a Image file')
        choice_2= int(input())
        if choice_2 == 1:
            SearchByCam()
        elif choice_2 == 2:
            filename = input('Enter Source: ')
            SearchByImage(filename)
        else:
            print('Invalid Choice!!!!!!!!')
    elif choice_1 == 2:
        print('Processing......')
        SortAllImage()
    else:
        print('Invalid Choice!!!!!!!!1')
    
if __name__ == "__main__":
    main()