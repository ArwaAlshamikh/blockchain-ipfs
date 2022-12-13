# blockchain-ipfs
This is a simple secure file sharing system based on the IPFS which is build on the blockchain concept.

# System Depedencies
This application requires the following
	- python 3.6 or higher
	- sqlite to be installed

# Installation & Running
1. Clone this repository `git clone https://github.com/ArwaAlshamikh/blockchain-ipfs.git`
2. navigate to the folder 'blockchain-ipfs'
3. create a virtual environment `python3 -m venv .venv"`
4. Run `python3 setup.py`. This will:
	- install all the depedencies
	- create a database
4. Activate the virtual environment:
	- windows `.venv\Scripts\activate.bat` 
	- linux `. .venv/bin/activate`
5. run the app `flask --app client.py  --debug run`
