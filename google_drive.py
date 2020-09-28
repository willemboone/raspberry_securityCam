from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os


class G_Drive(object):
    
    def __init__(self):
        
        # authentication
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)
    
    def upload(self, file, fid):
        f = self.drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": fid}]})
        f.SetContentFile(file)  # Read local file
        f.Upload()
        f = None
        