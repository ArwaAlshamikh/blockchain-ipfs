import os
import sqlite3

def database_init():
    #set the path to the database
    print("connecting to the database")
    db_path= "."+ os.sep + "ipfs.db"
    connection = sqlite3.connect(db_path)

    cur = connection.cursor

    with open('schema.sql') as f:
        connection.executescript(f.read())
    print("creating the tables")
    connection.commit()
    connection.close()
    print("Done! You can now run the app 'python3 client.py'")



if __name__ == '__main__':
    os.system("python3 -m pip install -r requirements.txt")
    database_init()

