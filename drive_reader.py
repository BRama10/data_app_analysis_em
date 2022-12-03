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
    #note that was overwritten when I deployed to webserver by client-server OAuth2 relationship
    #this may pose problems later but I haven't ran into any yet
    SCOPES = ['https://www.googleapis.com/auth/drive']

        
    def __init__(self, creds):
        self.file_list = []
        
        #credentials for user account
        self.creds = creds
  
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
        #calls request method specific to non-WorkSpace files (excel, pdf, jpg, etc)
        request = self.service.files().get_media(fileId=file_id)
        #request = self.service.files().export_media(fileId=file_id, mimeType='application/pdf')
        
        #creates a a bytes object to write raw file to
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
  
            # Return True if file Downloaded successfully
            return True
        except:
            # Return False if something went wrong
            raise Exception

    #note that there are a lot of print statements | this method is used to download our survey results
    #I ran into many problems regarding authentication so I added debugger statements to find out where problems went wrong
    #they only print to server however, so users aren't impacted by these
    def FileDownloadWorkspace(self, file_id, file_name):
        #request to download G Workspace files (such as docs, sheets, etc)
        request = self.service.files().export_media(fileId=file_id, mimeType='text/csv')
        print("Stage 1 Done")
        fh = io.BytesIO()
        print("Stage 2 Done")
        
        
        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
        print("Stage 3 Done")
        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()
            print("Stage 4 Done")
            fh.seek(0)
            
            #fn = os.path.dirname(__file__) + "nf.file" | don't worry about this line
            # Write the received data to the file
            print("Stage 5 Done")
            
            #write the downloaded data to an actual file (bytes)
            with open('/tmp/datafile.file', 'wb') as f:
                shutil.copyfileobj(fh, f)
  
            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except BaseException as e:
            return 'Didn\'t Work'
  
            print("File Downloaded")
        
    
#connecting to DriveAPI requires both file id (unaccessible to user without extra work, and file name
#this function makes process easy by scraping Drive, automatically finding id based on name
class Scraper:
    def __init__(self):
        #self.lst = lst
        self.value = None

    def setList(self, lst):
        self.lst = lst

    #find file by name
    def findByName(self,name):
        while len(self.lst) > 0:
            if(name == list(self.lst[0].values())[1]):
                self.value = self.lst[0]
                return True
            else:
                del self.lst[0]
        
    #finds file by id
    def findByID(self,ID):
        while len(self.lst) > 0:
            if(ID == list(self.lst[0].values())[0]):
                self.value = self.lst[0]
                return True
            else:
                del self.lst[0]

    #gets id-value (name) pair if clean = True, otherwise just gets id
    def getValue(self, clean = False):
        if self.value != None and clean == False:
            return self.value
        elif clean == True:
            return tuple(self.value.values())
        return False
      
    #prints value (name) | used for debugging
    def printValue(self):
        if self.getValue() != False:
            print(self.getValue())
        else:
            print("No Value Found")
            
            
#function that is called by main.py , connects to GDrive and downloads file
#vars val = name of file, c = credentials for Google Account
def callbackFunction(val, c):
  
    #creates DriveAPI & Scraper object
    obj = DriveAPI(c)
    scraper = Scraper()
  
    #tries downloading files nonWorkSpace file.... if it doesn't work (meaning file is WorkSpace), then downloads as WorkSpace file
    try:
        k = val
            
        scraper.setList(obj.file_list)

        check1 = scraper.findByName(k)
 
        check2 = scraper.getValue()
        print(check1, check2)
        if(check1 == False or check2 == False):
            raise NameError
        obj.FileDownloadNonWorkspace(scraper.getValue(clean = True)[0], scraper.getValue(clean = True)[1])
  
    except NameError:
        print("File Name Incorrect, Please Try Again")
    except:
        obj.FileDownloadWorkspace(scraper.getValue(clean = True)[0], scraper.getValue(clean = True)[1])

        
#if __name__ == "__main__":
    


