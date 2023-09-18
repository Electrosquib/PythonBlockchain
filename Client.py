import rsa
import json
from datetime import datetime
import binascii
import random
import requests
import pandas as pd
from IPython.display import display, HTML

api_url = "http://127.0.0.1:5000"

class Client:
    def __init__(self, file_name):
        self.file_name = file_name

    def generate_RSA(self, file_name):
        """
        Generates a new RSA public/private key pair and saves it to a .PEM file
        Returns: pubkey, privkey
        """
        (pubkey, privkey) = rsa.newkeys(2048)
        # Export public key in PKCS#1 format, PEM encoded 
        publicKeyPkcs1PEM = pubkey.save_pkcs1().decode('utf8')
        # Export private key in PKCS#1 format, PEM encoded 
        privateKeyPkcs1PEM = privkey.save_pkcs1().decode('utf8')
        with open(file_name, "w") as file:
            file.write(publicKeyPkcs1PEM)
            file.write(privateKeyPkcs1PEM)
        return pubkey, privkey

    def get_keys(self):
        """
        Gets RSA key pair from a .PEM-formatted file.
        This should get run first to ensure the keys are here before signing or verifying.
        Generates self.pk, self.sk (string formatted private and secret(private) key)
        Also generates self.privkey, self.pubkey (python-rsa objects)
        Returns: publickey, privatekey (both as python-rsa objects)
        """
        with open(self.file_name, mode='rb') as privatefile:
            keydata = privatefile.read()
        privkey = rsa.PrivateKey.load_pkcs1(keydata)
        pubkey = rsa.PublicKey.load_pkcs1(keydata)
        self.pk = pubkey.save_pkcs1()[31:-30].decode('utf8') # String Public Key Representation
        self.sk = privkey.save_pkcs1()[32:-31].decode('utf8')  # String Private Key Representation
        self.privkey = privkey # PrivateKey object, which is used for other RSA functions (sign, verify)
        self.pubkey = pubkey # PublicKey object, which is used for other RSA functions (sign, verify)
        return pubkey, privkey

    def sign_transaction(self, amount, recipient):
        """
        Generates the SHA-256 digital signature of a transaction (created by amount and recipient)
        Uses the client's private key retrieved by get_keys()
        Saves as self.signed_transaction

        Returns (str): "{transaction: {...}, signature: {...}}"
        """
        self.transaction = json.dumps({"timestamp":datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), "sender":self.pk, "recipient":recipient, "amount":amount})
        signature = rsa.sign(self.transaction.encode("utf-8"), self.privkey, "SHA-256")
        self.signed_transaction = json.dumps({"transaction": json.loads(self.transaction), "signature": binascii.hexlify(signature).decode("utf-8")})
        return self.signed_transaction

    def post_transaction(self):
        """
        Posts transaction to API to be verified and added to block
        """
        url = api_url+"/new-transaction"
        headers = {'Content-Type': 'application/json'}
        requests.post(url, headers=headers, data=self.signed_transaction)


file_path = input("File path to key pair '.PEM' file (input random text to skip): ")
try:
    client = Client(file_path)
    client.get_keys()
except:
    print("File does not exist! Please generate a key pair")

print("           Menu            ")
print("---------------------------\n")
print("S | Send Coins\nB | View Current Balance\nG | Generate Key Pair\nV | View Blockchain\n")
choice = input("Enter command: ")
while choice.lower() != "quit" or choice.lower() != "q":
    if choice.lower() == "g":
        name = input("Enter your desired file name ('.PEM' will automatically be appended): ")
        client.generate_RSA(name+".pem")
        print(f"-- {name}.pem generated --")
        client.file_name = name+".pem"
        client.get_keys()
        print(f"Your Public Key is {client.pubkey}")
    elif choice.lower() == "s":
        receiver = input("Enter the Public Key of the recipient: ")
        amount = input("Enter amount of coins to send: ")
        num = random.randint(1000, 10000)
        if int(input(f"Code: {num} | Confirm Transaction by entering the code: ")) == num:
            client.sign_transaction(amount, receiver)
            client.post_transaction()
            print("-- Transaction confirmed --")
        else: 
            print("-- Verification Failed --")
    elif choice.lower() == "q":
        break

    elif choice.lower() == "v":
        bc = requests.get(api_url+"/blockchain").text
        df = pd.read_json(bc)
        df.to_html("bc.html")
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.colheader_justify', 'center')
        pd.set_option('display.precision', 3)

    choice = input("Enter command: ")