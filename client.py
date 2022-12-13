from flask import Flask, redirect, url_for, render_template, request, flash,session
from my_constants import app
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
import time, ipfshttpclient, os, requests, socketio, sqlite3, hashlib,sqlite3,secrets  


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route("/download")
def download():
    if not session.get('userID'):
        return render_template('login.html',message='login to continue')
    return render_template('download.html',files = get_my_files())


@app.route("/upload")
def upload():
    if not session.get('userID'):
        return redirect(url_for('login'))
    return render_template('upload.html',peers = get_peers())


@app.route("/my_peers")
def my_peers():
    if not session.get('userID'):
        return render_template('login.html',message='login to continue')
    return render_template('my_peers.html',peers = get_peers())

@app.route('/logout')
def logout():
    session.pop('userID', None)
    return hello_world()

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userID = login(username,password)

        if not userID:
            session['userID'] = None  
            return render_template('login.html',message="incorrect username or password")  
        else:
            session['userID'] = userID
            return render_template('index.html')
    else:
        return render_template('login.html')

@app.route("/signup", methods=['GET'])
def signup_get():
    return render_template('signup.html')

@app.route("/signup", methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        names = request.form['names']
        password = request.form['password']
        conf_pass = request.form['conf_password']
        if password == conf_pass:
            #save to db
            save_to_db(username, password, names)

            return render_template('signup.html',
                                   message='Account created successfully, login to continue')
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
                error_flag = False
                filename = secure_filename(user_file.filename)
                sender = session['userID']
                receiver = request.form['Receiver']
                print(filename,sender, receiver) 
                user_file.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # filepath from upload
                file_path = os.sep.join(["upload", filename])
                fileHash = add_a_file(file_path)
                # response = "your file was successfully added to the blockchain\n your has is: "+hash
            else:
                error_flag = True
                response = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'

        if error_flag == True:
            return render_template('upload.html', message=response)
        else:
            # save the record to db
            print(save_a_shared_file(filename,sender,receiver,fileHash))
            return render_template(
                'upload.html',
                message="File succesfully uploaded", userID = session['userID'])


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
            flash(file_path + " File successfully downloaded")
            return render_template('download.html')


###########################################################
###                                                     ###
###                   PEER MANAGEMENT                   ###
###                                                     ###
###########################################################





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
# returns a file path of the file
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


def get_con():
    conn = sqlite3.connect('ipfs.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_my_keys(userID):
    #set the path to the database
    con = get_con()
    myKey = secrets.token_hex(16)
    saveKeyQuery = f"insert into myKeys(userID, userKey)VALUEs({userID},'{myKey}');"
    if con.execute(saveKeyQuery):
        con.commit()
        con.close()
        return True
    return False

def get_peers():
    con = get_con()
    peersQuery = f"select * from peers;"
    peers = con.execute(peersQuery).fetchall()
    con.close()
    return peers

def save_a_shared_file(filename,sender,receiver,fileHash):
    con = get_con()
    saveFileQ = f"insert into userFiles(userID,receiver,fileName,fileHash)VALUES({sender},{receiver},'{filename}','{fileHash}');"
    if con.execute(saveFileQ):
        con.commit()
        con.close()
        return 'file saved'

    con.commit()
    con.close()
    return 'some error coorred while saving'

def get_my_files():
    con = get_con()
    filesQuery = f"SELECT * from userFiles where receiver = {session['userID']};"
    print(filesQuery)
    files = con.execute(filesQuery).fetchall()
    con.close()
    return files

def save_to_db(username, password, names):
    #set the path to the database
    con = get_con()
    password = password.encode()
    password = hashlib.md5(password).hexdigest()
    print(password)
    signup_query = f"insert into peers(username,password,names)VALUES('{username}','{password}','{names}');"
    con.execute(signup_query)
    con.commit()
    con.close()

    # get userID
    userID = login(username,password, True)
    if create_my_keys(userID):           
        return True
    return False


#log in a user
def login(username, password, internal = False):
    con = get_con()
    if not internal:
        hasher = hashlib.md5()
        hasher.update(password.encode())
        password = hasher.hexdigest()
    cur = con.cursor()
    login_query = f"SELECT userID from peers WHERE username='{username}' AND password = '{password}';"
    userIDCrude = cur.execute(login_query).fetchone()
    con.close()
    if userIDCrude:
        for userID in userIDCrude:
            session['username'] = username
            return userID
    else:
        return None


if __name__ == '__main__':
    app.run()
