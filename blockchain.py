import requests

projectId = "2HarP2jRgTNfgmV1o7EXT5v03HX"
projectSecret = "577c1d25a117435530be5495e14bca02"
endpoint = "https://ipfs.infura.io:5001"


def add_a_file(filename):
    ### ADD FILE TO IPFS AND SAVE THE HASH ###
    response1 = requests.post(endpoint + '/api/v0/add', files=filename, auth=(projectId, projectSecret))
    print(response1)
    hash = response1.text.split(",")[1].split(":")[1].replace('"','')

    return hash

def get_a_file(hash):
    response2 = requests.post(endpoint + '/api/v0/cat', params=hash, auth=(projectId, projectSecret))
    print(response2)
    print(response2.text)
