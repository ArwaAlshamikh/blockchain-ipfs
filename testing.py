import requests,os

projectId = "2HarP2jRgTNfgmV1o7EXT5v03HX"
projectSecret = "577c1d25a117435530be5495e14bca02"
endpoint = "https://ipfs.infura.io:5001"

### CREATE AN ARRAY OF TEST FILES ###

upload_file  = open('upload/20221116-145805about.png','rb')

### ADD FILE TO IPFS AND SAVE THE HASH ###
response1 = requests.post(endpoint + '/api/v0/add', files={"file":upload_file}, auth=(projectId, projectSecret))
print(response1)
hash = response1.text.split(",")[1].split(":")[1].replace('"','')
print(hash)

### READ FILE WITH HASH ###
params = {
    'arg': hash,
    'archive': True
}
response2 = requests.post(endpoint + '/api/v0/cat', params=params, auth=(projectId, projectSecret))
# print(response2.headers['content-type'])
# print(response2.content)
# file_path = os.path.join("download/", hash + ".png")
# user_file = open(file_path, 'ab+')
# user_file.write(response2)
# user_file.close()
# print(response2.json())
print(response2.body)

### REMOVE OBJECT WITH PIN/RM ###
response3 = requests.post(endpoint + '/api/v0/pin/rm', params=params, auth=(projectId, projectSecret))

