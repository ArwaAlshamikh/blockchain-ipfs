from flask import Flask
import os

CURRENT_FOLDER = os.getcwd()
UPLOAD_FOLDER =  os.sep.join([CURRENT_FOLDER, "upload"])
DOWNLOAD_FOLDER = os.sep.join([CURRENT_FOLDER, "download"])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app = Flask(__name__)
app.secret_key = "secret key"
app.config['CURRENT_FOLDER'] = CURRENT_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['SERVER_IP'] = '127.0.0.1:5111'
app.config['NODE_ADDR'] = {'Host' : '0.0.0.0', 'Port' : 5113}
app.config['BUFFER_SIZE'] = 64 * 1024
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#secret_key("577c1d25a117435530be5495e14bca02")
#project_ID("2HarP2jRgTNfgmV1o7EXT5v03HX")
#end_point("https://ipfs.infura.io:5001")
#end_point("https://securefilesharing.infura-ipfs.io")

