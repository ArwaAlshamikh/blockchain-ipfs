import os
import sqlite3

def database_init():
    #set the path to the database
    connection = sqlite3.connect("ipfs.db")
    cur = connection.cursor

    with open('schema.sql') as f:
        connection.executescript(f.read())

    connection.commit()
    connection.close()




if __name__ == '__main__':
    os.system("python3 -m pip install -r requirements.txt")
    database_init()

