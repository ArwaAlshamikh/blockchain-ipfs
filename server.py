import sqlite3
import os
from sqlite3 import Error
import hashlib
from server_constants import app
from datetime import datetime   
import requests
import urllib.request 
import socketio
from flask_socketio import SocketIO, send, emit


socketio = SocketIO(app)

#set the path to the database
db_url = os.sep.join([app.config['CURRENT_FOLDER'],'users_db'])
connection = sqlite3.connect(db_url)
cur = connection.cursor()

   
# get all files shared to a user 
def load_sent_files(user_id):
    files_query = f"SELECT * from user_files WHERE user_id={user_id};"
    user_files =  cur.execute(files_query)
    
    if not cur.fetchone():  
        return ''
    else:
        return user_files

# get all my peers 
def load_my_peers(user_id):
    peers_query = f"SELECT * from user_peers WHERE user_id={user_id};"
    user_peers =  cur.execute(peers_query)
    
    if not cur.fetchone():  
        return ''
    else:
        return user_peers

# save user details
def signup(username, password):
    #generate user key
    password = hashlib.md5(password.encode())

# get their key for file encryption
def get_personal_key(user_id):
    get_personal_key_query = f"SELECT user_key where user_id={user_id};"
    personal_token =  cur.execute(get_personal_key_query)
    
    if not cur.fetchone():  
        return ''
    else:
        return personal_token

# save a transaction
def save_file_share_transaction(sender_user_id,receiver_user_id,file_name,file_hash):
    current_date_time = datetime.now()
    save_transaction_query = f"INSERT INTO user_files VALUES('{sender_user_id}','{receiver_user_id}','{file_name}','{file_hash}','{current_date_time}');"
    cur.execute(save_transaction_query)
    if not cur.commit():
        return "some error occured"
    else:
        return "transaction recorded successfully"
        



    
