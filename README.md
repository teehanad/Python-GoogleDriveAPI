# Python-GoogleDriveAPI
Command line Google Drive tool to manage your drive and encrypt files to share with peoplem for CS3031

Firstly there should be no files in your directory apart from main.py and keygen.py. The user will first have to go to here and generate a credentials.json file 
https://developers.google.com/drive/api/v3/quickstart/python

This will anable the user to establish and auth flow and allow the cloud storage app permissions for their google drive account. This auth flow saves in a file called token.pickle to keep user signed in upon returning sessions. 

The user will be prompted by the program first time around saying no key. The user can then type gen to create the AES key. The system will quit and ask the user to restart so it can load the key. Now you have a key to encrypt your files with. 

Next the user can switch over to keygen.py and generate their public and private key to share this AES key with other users in the group. the user can generate their keys by running the program with command line argument gen

**python keygen.py gen**

This tells the system to generate new keys. They can then share this public key with the group users and  can receive other group users public keys. Once received they can encrypt the AES key using another users public key like so

**python keygen.py key.key publickey.txt enc**

This tells the system to encrypt the file key.key using the file publicly.txt. This file can then be transmitted to the user who owns the public key so they can decrypt it using their private key like so

**python keygen.py encryption.txt privately.txt dec**

This will create a text file called decryption.txt containing the AES key used for the google drive encryption. 

Congratulations! You and the other users are now set up to start sharing encrypted files with each other on Google Drive.
