import urllib.request
import json, time
import base64, sys

from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk

# Paste your access token here! (User auth is a WIP)
access_token = ""

def get_song_info():            
    req = urllib.request.Request(url='https://api.spotify.com/v1/me/player/currently-playing')
    req.add_header("Authorization", "Bearer " + access_token)

    with urllib.request.urlopen(req) as f:
        resp = json.loads(f.read().decode('utf-8'))

        info = {
            "title": resp["item"]["name"],
            "artist": resp["item"]["artists"][0]["name"],
            "img": resp["item"]["album"]["images"][1]["url"]
        }

        return info

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#212121")
        self.master = master
        self.pack()

        self.update_song_info()
        self.create_widgets()
        self.run_interval()

    def update_song_info(self):
        info = get_song_info()
        self.songtitle = info["artist"] + " - " + info["title"]
        self.songimg = ImageTk.PhotoImage(Image.open(BytesIO(urllib.request.urlopen(info["img"]).read())))

    def run_interval(self):
        # set refresh interval
        self.update_song_info()
        self.songinfo.config(text=self.songtitle)
        self.albumart.config(image=self.songimg)

        self.master.after(2000, self.run_interval)

    def create_widgets(self):
        # set widow parameters
        self.master.title("nowplaying")
        self.master.iconbitmap("nowplaying.ico")
        self.master.configure(bg="#212121")

        # set album artwork
        self.albumart = Label(self, 
            image=self.songimg,
            bg="#212121")
        self.albumart.pack(side="top")

        # set song info variables and display
        self.songinfo = Label(self, 
            text=self.songtitle,
            fg="#dddddd",
            bg="#212121",
            font="{Proxima Nova} 11")
        self.songinfo.pack(side="bottom")

# # get auth stuff (DON'T UPLOAD/SHOW YOUR CODE WITH KEYS IN PLAINTEXT)
# client_id = b""
# client_secret = b""
# client_code = client_id + b":" + client_secret
# encoded_header = base64.urlsafe_b64encode(client_code).decode("utf-8")

# # create request
# req = urllib.request.Request(
#     url="https://accounts.spotify.com/api/token",
#     data=b"grant_type=client_credentials"
# )
# req.add_header("Content-Type", "application/x-www-form-urlencoded")
# req.add_header("Authorization", "Basic " + encoded_header)

# # obtain access token
# response = urllib.request.urlopen(req)
# response = json.loads(response.read())
# access_token = response["access_token"]
# print (access_token)

# start application
root = Tk()
app = Application(master=root)
app.mainloop()