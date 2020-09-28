from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os


class G_Drive(object):
    
    def __init__(self):
        
        # authentication
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)
    
    def upload(self, file, fid = "1oZQ20r_IW7kbgCF8OzJN671scfw8oJ8w"):
        f = self.drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": fid}]})
        f.SetContentFile(file)  # Read local file
        f.Upload()
        f = None
        