# import the required libraries
from __future__ import print_function
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
  
class DriveAPI:
    global SCOPES
    
      
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
  
    def __init__(self):
        self.file_list = []
        # Variable self.creds will
        # store the user access token.
        # If no valid token found
        # we will create one.
        self.creds = None
  
        # The file token.pickle stores the
        # user's access and refresh tokens. It is
        # created automatically when the authorization
        # flow completes for the first time.
  
        # Check if file token.pickle exists
        if os.path.exists('token.pickle'):
  
            # Read the token from the file and
            # store it in the variable self.creds
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
  
        # If no valid credentials are available,
        # request the user to log in.
        if not self.creds or not self.creds.valid:
  
            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
  
            # Save the access token in token.pickle
            # file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
  
        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)
  
        # request a list of first N files or
        # folders with name and id from the API.
        results = self.service.files().list(
            pageSize=100, fields="files(id, name)").execute()
        items = results.get('files', [])

        self.file_list = items
        # print a list of files
  
        #print("Here's a list of files: \n")
        #print(*items, sep="\n", end="\n\n")
  
    def FileDownloadNonWorkspace(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        #request = self.service.files().export_media(fileId=file_id, mimeType='application/pdf')
        fh = io.BytesIO()
          
        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
  
        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()
  
            fh.seek(0)
              
            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)
  
            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except:
            # Return False if something went wrong
            raise Exception

    def FileDownloadWorkspace(self, file_id, file_name):

        request = self.service.files().export_media(fileId=file_id, mimeType='text/csv')
        fh = io.BytesIO()
          
        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
  
        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()
  
            fh.seek(0)
              
            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)
  
            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except:
            print("File Unable to be Downloaded")
            return False
        
    

class Scraper:
    def __init__(self):
        #self.lst = lst
        self.value = None

    def setList(self, lst):
        self.lst = lst

    def findByName(self,name):
        while len(self.lst) > 0:
            if(name == list(self.lst[0].values())[1]):
                self.value = self.lst[0]
                return True
            else:
                del self.lst[0]
        
        
    def findByID(self,ID):
        while len(self.lst) > 0:
            if(ID == list(self.lst[0].values())[0]):
                self.value = self.lst[0]
                return True
            else:
                del self.lst[0]

    def getValue(self, clean = False):
        if self.value != None and clean == False:
            return self.value
        elif clean == True:
            return tuple(self.value.values())
        return False

    def printValue(self):
        if self.getValue() != False:
            print(self.getValue())
        else:
            print("No Value Found")

def callbackFunction(val):
    obj = DriveAPI()
    scraper = Scraper()
  
    try:
        k = val
            
        scraper.setList(obj.file_list)

        check1 = scraper.findByName(k)
 
        check2 = scraper.getValue()

        if(check1 == False or check2 == False):
            raise NameError
        obj.FileDownloadNonWorkspace(scraper.getValue(clean = True)[0], scraper.getValue(clean = True)[1])
            
    except NameError:
        print("File Name Incorrect, Please Try Again")
    except:
        obj.FileDownloadWorkspace(scraper.getValue(clean = True)[0], scraper.getValue(clean = True)[1])

        
#if __name__ == "__main__":
    


