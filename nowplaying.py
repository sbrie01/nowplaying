import urllib.request
import json, time
import base64, sys
import webbrowser as wb
import threading

from flask import Flask
from flask import request

from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk

access_token = None
refresh_token = None

# client id, from registered app on spotify developer
client_id = b"0e0a0623956e4b78ab1cd3e3c0ef2078"

def get_tokens(auth_code):
    # encode client details
    client_code = client_id + b":" + client_secret
    encoded_header = base64.urlsafe_b64encode(client_code).decode("utf-8")
    print(encoded_header)
    
    # create parameters
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": "http://127.0.0.1:5000"
    }).encode()
    
    print (data)
    
    # create request
    req = urllib.request.Request(
        url="https://accounts.spotify.com/api/token",
        data=data,
        method="POST"
    )

    # add client info header
    req.add_header("Authorization", "Basic " + encoded_header)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    # resp = urllib.request.urlopen(req)
    # print (resp)
    
    with urllib.request.urlopen(req) as f:
        resp = json.loads(f.read().decode("utf-8"))
        print (resp)

        global access_token
        access_token = resp["access_token"]

def get_song_info():
    if access_token == None:
        time.sleep(1)
        get_song_info()
        
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

def run_backend():
    # start flask endpoint for receiving auth
    f_app = Flask(__name__)

    @f_app.route('/')
    def index():
        # get code from parameters
        auth_code = request.args.get("code")
        get_tokens(auth_code)
        
        return """
        <html>
        <head><title>nowplaying</title></head>
        <body>
        Thanks for logging in to nowplaying! You may now close this browser window.
        </body>
        </html>
        """

    @f_app.route('/auth')
    def auth():
        return "Auth endpoint"
    
    f_app.run(debug=False, use_reloader=False)
    
class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#212121")
        self.master = master
        self.pack()

        self.authenticate()
        # self.start_server()
        self.update_song_info()
        self.create_widgets()
        self.run_interval()
        
    def authenticate(self):
        baseurl = "https://accounts.spotify.com/authorize?"
        params = urllib.parse.urlencode({
            'client_id': client_id, 
            'response_type': 'code',
            'redirect_uri': 'http://127.0.0.1:5000',
            'scope': 'user-read-currently-playing'
        })

        endpoint = baseurl + params
        print (endpoint)

        wb.open_new_tab(endpoint)
        # sys.exit(0)

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

# read client_secret from file (don't commit this!)
csf = open("client_secret.key", "rb")
client_secret = csf.readline().strip()

t = threading.Thread(target=run_backend)
t.daemon = True
t.start()

# start GUI application
root = Tk()
gui = Application(master=root)
gui.mainloop()
