import socket
import pickle
import os
from AES import *
from KeyGenerator import *

KEY = os.urandom(16)

class Client(object):
    """ creating client """
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 4522))
        self.aes = AESCrypt()
        self.rsa = Cryptonew()
        self.public = ''

    def unpack(self, data):
        return pickle.loads(data.decode('base64'))

    def pack(self, data):
        return pickle.dumps(data).encode('base64')

    def send_key(self):
        """ sends encryption key with the public key """
        self.public = self.client_socket.recv(1024)  # receiving public
        self.public = self.unpack(self.public)  # unpacking
        encrypted_key = self.rsa.encrypt(KEY, self.public)  # encrypting key with public
        self.client_socket.send(encrypted_key)  # sending key
        response = self.client_socket.recv(1024)  # receiving server's confirmation
        print response

    def encrypt_request(self, request):
        """ encrypts client's request """
        return self.aes.encryptAES(KEY, request)

    def decrypt_response(self, response):
        """ decrypts server's response """
        return self.aes.decryptAES(KEY, response)