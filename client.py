from flask import Flask, redirect, url_for, render_template, request, flash
from my_constants import app
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
import time, ipfshttpclient, os, requests, socketio, sqlite3, hashlib

# sio = socketio.Client()
# client_ip = app.config['NODE_ADDR']
# connection_status = False


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route("/download")
def download():
    return render_template('download.html')


@app.route("/upload")
def upload():
    return render_template('upload.html')


@app.route("/my_peers")
def my_peers():
    return render_template('my_peers.html')


@app.route("/signup", method=['GET'])
def signup_get():
    return render_template('signup.html')


@app.route("/signup", method=['POST'])
def signup_post():
    if request.method == 'POST':
        username = request.files['usernaem']
        password = request.files['password']
        conf_pass = request.files['conf_password']
        if password == conf_pass:
            #save to db
            save_to_db(username, password)

            return render_template('signup.html',
                                   message='Account created successfully')
        else:
            return render_template('signup.html',
                                   message='Your passwords do not match')


@app.route('/add_file', methods=['POST'])
def add_file():
    if request.method == 'POST':
        error_flag = True
        if 'file' not in request.files:
            response = 'No file part'
        else:
            user_file = request.files['file']
            if user_file.filename == '':
                response = 'No file selected for uploading'
            if user_file:
                error_flag = True
                # add a timestamp
                timestr = time.strftime("%Y%m%d-%H%M%S")
                filename = timestr + secure_filename(user_file.filename)
                print(filename)
                user_file.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # filepath from upload
                file_path = os.sep.join(["upload", filename])
                hash = add_a_file(file_path)
            else:
                error_flag = True
                response = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'

        if error_flag == True:
            return render_template('upload.html', message=response)
        else:
            return render_template(
                'upload.html',
                message="File succesfully uploaded\nFile hash is:" + hash)


@app.route('/retrieve_file', methods=['POST'])
def retrieve_file():
    if request.method == 'POST':

        error_flag = True

        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        else:
            error_flag = False
            file_hash = request.form['file_hash']
            try:
                file_path = get_a_file(file_hash)
            except Exception as err:
                message = str(err)
                error_flag = True
                if "ConnectionError:" in message:
                    message = "Gateway down or bad Internet!"

        if error_flag == True:
            return render_template('download.html', message=message)
        else:
            return render_template('download.html',
                                   message=file_path +
                                   " File successfully downloaded")


###########################################################
###                                                     ###
###                   BLOCKCHAIN PART                   ###
###                                                     ###
###########################################################


# add a file to the blockchain
def add_a_file(filename):
    # declare
    # filename = os.sep.join([app.config["UPLOAD_FOLDER"],filename])
    url = app.config["END_POINT"] + '/api/v0/add'
    upload_file = {}
    upload_file['file'] = open(filename, 'rb')

    # make a dictionary of the file

    ### ADD FILE TO IPFS AND SAVE THE HASH ###
    response1 = requests.post(url,
                              files=upload_file,
                              auth=(app.config["PROJECT_ID"],
                                    app.config["SECRET_KEY"]))
    hash = response1.text.split(",")[1].split(":")[1].replace('"', '')

    return hash


# downloaad a file
#   returns a file path of the file
def get_a_file(file_hash):
    # declare
    url = app.config["END_POINT"] + '/api/v0/cat'
    arguments = {}
    arguments['arg'] = file_hash
    response2 = requests.post(url,
                              params=arguments,
                              auth=(app.config["PROJECT_ID"],
                                    app.config["SECRET_KEY"]))
    print(response2)
    return response2.text

    # client = ipfshttpclient.connect(url)
    # file_content = client.cat(file_hash)
    # file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_hash)
    # user_file = open(file_path, 'ab+')
    # user_file.write(file_content)
    # user_file.close()


# **********************************************************
# **                                                      **
# **                    SQL CODE                          **
# **                                                      **
# **********************************************************

#set the path to the database
db_url = os.sep.join([app.config['CURRENT_FOLDER'], 'users_db'])
connection = sqlite3.connect(db_url)
cur = connection.cursor()


def save_to_db(username, password):
    #generate user key
    public_key = 'gen_key'
    password = hashlib.md5(password.encode())
    signup_query = f"insert into users(username,password,public_key)VALUES('{username}','{password}','{public_key}');"
    cur.execute(signup_query)


#log in a user
def login(username, password):
    password = hashlib.md5(password.encode())
    login_query = f"SELECT user_id from users WHERE username='{username}' AND Password = '{password}';"
    user_id = cur.execute(login_query)

    if not cur.fetchone():
        return 0
    else:
        return user_id


if __name__ == '__main__':
    app.run()
