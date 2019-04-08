import Crypto
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import sys

#RSA enxryption protocol
#This program can generate a pair of public and private keys that can be used to encrypt and decrypt the AES key used
#by the cloud storage program to encrypt files for the google drive.
#To add a user to the cloud storge group you must
#-Get there public key
#-Encrypt the AES key for the cloud storage app using the public key and share it with them
#-They must then decrypt it using their private key
#-Add file permissions on google drive for the user using the cloud storgae app
#If you want to generate new keys just do python keygen.py gen
#If you want to encrypt a message just do python keygen.p fileToEncrypt.txt personsPublicKeyYouWillSendTo.txt enc
#If you have recived a file and want to decrypt just do python keygen.py fileToDecrypt.txt yourPrivateKey.txt dec



def main():
    #Booleans to check mode of program
    enc = False
    dec = False
    gen = False
    #Modes are passed in as command line args as described above
    if (sys.argv[1] == 'gen'):
        gen = True
    elif (sys.argv[3]== 'dec'):
        dec = True
    elif(sys.argv[3] == 'enc'):
        enc = True
    
    if(gen == False):
        #take in a filename as a command line arg and then read that file in to our secretString string
        filePassed = sys.argv[1]
        file = open(filePassed, 'r')
        secretString =file.read()

        #if in encrypt mode, import the users public key from the local dicrectory and run encryption
        if (enc == True):
            publickey = RSA.importKey(open("publicKey.txt", "rb"))
            encryptForSend(secretString, publickey)

        #if in decrypt mode, import the users private key from the local dicrectory and run decryption
        elif (dec == True):
            privatekey = RSA.importKey(open("privateKey.txt", "rb"))
            decryptRecived(secretString, privatekey)
    #else if gen mode set, generate new key pair
    elif(gen == True):
        keyGen()



#Method to generate new key pair using the RSA (Rivest–Shamir–Adleman) cryptosystem
def keyGen():
    key = RSA.generate(1024)

    #write the private key to a file using RSA Export function in pem format
    f = open ('privateKey.txt', 'w')
    f.write(key.exportKey(format='PEM'))
    f.close()

    #write the public key to a file using RSA Export function in pem format
    f = open ('publickey.txt', 'w')
    f.write(key.publickey().exportKey(format='PEM'))
    f.close()

    print("Generated Public and Private Keys")
        

    

def encryptForSend(string, key):
    #encrypt passed in string data using RSA encryption method
    #Note according to documentation the value 32 is a random value
    #for compatability that will be ignored
    encrypted = key.encrypt(string, 32)

    #write the encrypted data to a txt file so it can be shared
    f = open ('encryption.txt', 'w')
    f.write(str(encrypted))
    f.close()

    print("Encrypted data using receiving users public key")


def decryptRecived(string, key):
    #decrypt passed in string data using RSA decryption method
    decrypted = key.decrypt(ast.literal_eval(str(string)))

    #Write decrypted data to a text file so it can be used and viewed
    f = open ('decrypted.txt', 'w')
    f.write(str(decrypted))
    f.close()

    print("Decrypted recived data using your private key")

if __name__ == '__main__':
    main()