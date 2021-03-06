from __future__ import print_function
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from cryptography.fernet import Fernet
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import io


#https://developers.google.com/drive/api/v3/about-sdk - GoogleDriveAPI


#A dictionary of someGoogleDriveAPI supported MIME types for setting file type on upload bassed on file exstension
#Can add more if needs be
mimeTypes={
    "xls":'application/vnd.ms-excel',
    "xlsx":'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    "xml":'text/xml',
    "ods":'application/vnd.oasis.opendocument.spreadsheet',
    "csv":'text/plain',
    "tmpl":'text/plain',
    "pdf": 'application/pdf',
    "php":'application/x-httpd-php',
    "jpg":'image/jpeg',
    "png":'image/png',
    "gif":'image/gif',
    "bmp":'image/bmp',
    "txt":'text/plain',
    "doc":'application/msword',
    "js":'text/js',
    "swf":'application/x-shockwave-flash',
    "mp3":'audio/mpeg',
    "zip":'application/zip',
    "rar":'application/rar',
    "tar":'application/tar',
    "arj":'application/arj',
    "cab":'application/cab',
    "html":'text/html',
    "htm":'text/html',
    "default":'application/octet-stream',
    "folder":'application/vnd.google-apps.folder'
}


# If modifying these scopes, delete the file token.pickle.
# Setting scope of API
SCOPES = ['https://www.googleapis.com/auth/drive']

#Main class that calls all other functions
def main():
    os.system('clear') #clear terminal
    Key = importKey() #Import the current AES key from working directory created using fernet


    userExit = False #Boolean value to determine of menu loop should keep going
    establishAuthFlow()
    #If there is no token.pickle file in directory this will establish an auth flow for your google drive
    #Bassically you have to give my program permission to veiw, edit and delete everything in your google drive
    #This auth flow will be saved in a token.pickle file so yiu dont have to auth everytime you run

    #Print a list of acctions and the command to do that action
    print("------------------------")
    print("!List of actions!")
    print("Search Files: search")
    print("Upload a file: upload")
    print("Download a file: download")
    print("Encrypt a file: enc")
    print("Decrypt a file: dec")
    print("Share with user: share")
    print("Check users a file is shared with: perm")
    print("Delete user: unshare")
    print("Delete a file: del")
    print("Regen key !WARNING ANY FILE CURRENLTY ENCRYPTED WILL NOT BE ABLE TO BE DECRYPTED! : gen")
    print("Exit: exit")
    print("------------------------")
    print('\n')
    while userExit == False:
        #biiiiiiiggggggg loooooonnnnggggg if elif else statment to cover calling every function possible for user
        nextAction = (str(raw_input("What would you like to do next? ")))
        if(nextAction == 'search'):
            fileName = (str(raw_input("Enter a file name to search for: ")))
            search(fileName)
        elif(nextAction == 'upload'):
            fileName = (str(raw_input("Enter full file name for upload: ")))
            fileType = (str(raw_input("Enter the file exstension without a dot: ")))
            fileType = mimeTypes[fileType]
            upload(fileName, fileType)
        elif(nextAction == 'download'):
            fileName = (str(raw_input("Enter a file name for download: ")))
            download(getID(fileName), fileName)
        elif(nextAction =='enc'):
            fileName = (str(raw_input("Enter a file name with exstension to encrypt: ")))
            encryptFile(fileName, Key)
        elif(nextAction == 'dec'):
            fileName = (str(raw_input("Enter a file name with exstension to decrypt: ")))
            decryptFile(fileName, Key)
        elif (nextAction == 'exit'):
            userExit = True
            print('System exiting....')
            exit()
        elif(nextAction == 'gen'):
            print('Regening key, Program will quit. Please restart to use new key')
            keyGen()
            print("Shutting down, Please restart")
            exit()
        elif(nextAction == 'share'):
            fileName = (str(raw_input("Enter a file name to share:  ")))
            userEmail = (str(raw_input("Enter users email address to share with: ")))
            shareFile(getID(fileName), userEmail)
        elif(nextAction == 'perm'):
            fileName = (str(raw_input("Enter a file name to check permissions:  ")))
            listPerm(getID(fileName))
        elif(nextAction == 'unshare'):
            fileName = (str(raw_input("Enter a file name to unshare:  ")))
            permissionID = (str(raw_input("Enter a the id of the permission for the file name to unshare:  ")))
            removeUser(getID(fileName),permissionID)
        elif(nextAction =='del'):
            fileName = (str(raw_input("Enter a file name to delete:  ")))
            deleteFile(getID(fileName))
        else:
            print("Try again: ")

    
#This is the key that we will encrypt the files going into the google drive with
#Generate a new key using fernet and save it to a .key file
def keyGen():
    try:
        key = Fernet.generate_key()
        file = open('key.key', 'w+')
        file.write(key.decode()) 
        return key
    except:
        print('No idea what to tell you, should have worked')

#Method used at start of program to import the current key in the working diredtory
#Opens the .key file and sets our key to the contents
def importKey():
    try:
        file = open("key.key", 'r')
        key = file.read()
        return key
    except:
        print("No key file")

#function that is passed in a file name and our key and creates an encrypted string of our data
#Using fernet encryption and then writes the contents back to the file passed in
def encryptFile(fileName, Key):
    try:
        data = open(fileName, "r")
        data = data.read()
        fernet = Fernet(Key)
        encrypted = fernet.encrypt(data)
        file = open(fileName, "w")
        file.write(encrypted)
        print("File Encrypted")
    except:
        print("encryption failed")


#Function that is passed in a file name and our key and creates an decrypted strimg of our data
#Using fernet decryption and then writes the contents back to the file passed in
def decryptFile(fileName, Key):
    try:
        data = open(fileName, "r")
        data = data.read()
        fernet = Fernet(Key)
        decrypted = fernet.decrypt(data)
        file = open(fileName, "w")
        file.write(decrypted)
        print("File Decrypted")
    except:
        print("Decryption failes, might not actually be encrypted in the first place")

#Function to create an instance of the GoogleDriveAPI and get permission to use users Google Drive
def establishAuthFlow():
    try:
        global service
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token) #imports current token file creds
        # If there are no (valid) credentials available procced to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run by writing them to a token.pickle file
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds) #Creates instance of GoogleDriveAPI
        print("Auth Flow Established")
    except:
        print("Establish Auth Flow Failed")

#Function to search for a file in your google drive to a max page size of 15 that contains the name passed in
def search(fileName):
    try:
        global service
        results = service.files().list(
        #Search for files that contain the word(s) passed in fileName
        pageSize=15, q="name contains '" + fileName +"'", fields="files(id, name)").execute() #list up to 15 items names and file ID's
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
    except:
        print("Search Failed")


#Function to search for a file in your google drive by exact name
#Same as the function above just only returns the item id instead of the name and id formated
def getID(fileName):
    try:
        global service
        results = service.files().list(
        #search for a file with the exact name
        pageSize=1, q="name='" + fileName +"'", fields='*').execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            for item in items:
                return item['id']
    except:
        print("Get ID failed")

#Function to upload a file to your google drive 
def upload(fileName, fileType): #Take in a file name and type
    try:
        global service
        file_metadata = {'name': fileName}  #Add file name to metadata
        media = MediaFileUpload(fileName,
                                mimetype=fileType) #Set file type for upload using the mime type dict from above
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute() 
        print ("Upload of "+fileName+" completed")
    except:
        print("Upload Failed")


#Function to download a file from your google drive 
def download(file_id, fileName): #Take a file name and id
    try:
        global service
        request = service.files().get_media(fileId=file_id) 
        fileRequest = io.BytesIO() 
        downloader = MediaIoBaseDownload(fileRequest, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk() 
            print( "Download %d%%." % int(status.progress() * 100))
        with io.open(fileName, 'w+') as file: 
            fileRequest.seek(0)
            file.write(fileRequest.read().decode())
    except:
        print("Downlaod Failed")


#Function to add permissions to a file in your google drive in batchs if needs be
#So that the file can be shared with people
def shareFile(fileID, userEmail):
    try:
        global service
        batch = service.new_batch_http_request(callback=callback) 
        user_permission = { #create a user permissions list to assign to a file using users type, role, and emailAddress for identification
            'type': 'user',
            'role': 'writer',
            'emailAddress': userEmail,
        }
        batch.add(service.permissions().create( 
                fileId=fileID,  
                body=user_permission,   #set permission body to the permission list we crated
                fields='id',   
        ))
        batch.execute() 
        print("File ws shared with "+userEmail)
    except:
        print("Share file failed")

#Function to list permissions of a file in your google drive so get permissionID to possibly remove a user later
#So that the file can be shared with people
def listPerm(fileID):
    try:
        global service
        #query the current instance of the GoogleDriveAPI for the permissions list of the passed in fileID and get
        #the permamters outlines in the fields query as we did with file search above just not for all items this time
        permissions = service.permissions().list(fileId=fileID,fields='permissions(id, emailAddress, displayName)').execute() 
        result = permissions.get('permissions', [])
        print(result)
    except:
        print("Permission list failed")

#Function to delete permissions of a file in your google drive using permissionID to esentially remove a user
#So that the file is no longer shared with this person
def removeUser(fileID, permissionID):
    try:
        global service
        service.permissions().delete(
                fileId=fileID,
                permissionId=permissionID   #create a permission delete request for a fileID and permissionID usimg the current
        ).execute()                         #instance of the GoogleDriveAPI
        print("User removed")
    except:
        print("Failed to remove user")

def callback(request_id, response, exception):
    if exception:

        print (exception)
    else:
        print ("Permission Id: %s" % response.get('id'))

#Function to delete a google drive file
def deleteFile(fileid):
    try:
        service.files().delete(fileId=fileid).execute()
        print("file deleted")
    except:
        print("Failed to delete file")


if __name__ == '__main__':
    main()