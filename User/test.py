import requests
from OpenSSL import crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
import datetime

now = datetime.datetime.now()
five_yeas_laters = now.replace(year=now.year + 5)

print(now.strftime("%Y%m%d%H%M%SZ"))
print(five_yeas_laters.strftime("%Y%m%d%H%M%SZ"))


subject = {
    "subCountryName" : "kr",
    "subStateOrProvinceName" : "seoul",
    "subLocalityName" : "user",
    "subOrganizationName" : "dankook",
    "subOrganizationalUnitName" : "software dept.",
    "subCommonName" : "user-ca",
    "subEmailAddress" : "user@ur.se"
}

# r = requests.post("http://localhost:5000/ca/request", data=subject)
# print(r.text)

# r = requests.post("http://localhost:5000/ca/issue-ca", data={**subject, "seq" : 5})
# print(r.text)
# result = r.json()
# encryptedCert = result["encryptedCert"]
# cert = result["cert"]
# privateKey = result["privateKey"]
# pubKey = result["pubKey"]
# print(encryptedCert)
# print(cert)
# print(privateKey)
# print(pubKey)

# file = open("key.pem", "w")
# file.write(privateKey)
# file.close()
# file = open("key.pub", "w")
# file.write(pubKey)
# file.close()
# file = open("ca.crt", "w")
# file.write(cert)
# file.close()
# file = open("encrypt_ca.crt", "w")
# file.write(encryptedCert)
# file.close()

# file = open("key.pub", "r")
# pubKey = file.read()
# file.close()

# file = open("key.pem", "r")
# privateKey = file.read()
# file.close()

# file = open("ca.crt", "r")
# cert = file.read()
# file.close()

# file = open("encrypt_ca.crt", "r")
# encryptedCert = file.read()
# file.close()

# k = RSA.importKey(pubKey)
# cipher = PKCS1_OAEP.new(k)
# en = cipher.encrypt("test".encode())

# r = requests.post("http://localhost:5000/ca/secure-connect", data={
#     **subject, 
#     "encryptedUserCert" : encryptedCert,
#     "originUserCert" : cert
# })
# result = r.json()
# encryptedSecurePrivateKeyChunk = result["encryptedSecurePrivateKeyChunk"]

# k = RSA.importKey(privateKey)
# cipher = PKCS1_OAEP.new(k)

# securePrivateKeyChunk = []
# for chunk in encryptedSecurePrivateKeyChunk:
#     b64decodedChunk = base64.b64decode(chunk)
#     decryptChunk = cipher.decrypt(b64decodedChunk).decode()
#     securePrivateKeyChunk.append(decryptChunk)

# securePrivateKey = "".join(securePrivateKeyChunk)
# securePubKey = result["securePubKey"]

# print(securePrivateKey)
# print(securePubKey)

# file = open("secure-key.pem", "w")
# file.write(securePrivateKey)
# file.close()

# file = open("secure-key.pub", "w")
# file.write(securePubKey)
# file.close()