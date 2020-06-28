import os
from OpenSSL import crypto
import datetime
from utils.FillX509Name import FillX509Name

class Certificate:
    RootCertFileName = "root-cert.crt"
    RootPrivateKeyFileName = "root-key.pem"
    RootPubKeyFileName = "root-key.pub"

    RootX509Name = {
        "countryName" : "kr", 
        "stateOrProvinceName" : "seoul", 
        "localityName": "root", 
        "organizationName" : "dankook", 
        "organizationalUnitName" : "software dept.", 
        "commonName" : "root", 
        "emailAddress" : "root@rt.oo"
    }

    def __init__(self):
        self.rootPubKey = None
        self.rootPrivateKey = None
        self.rootCert = None

        self.LoadCAFiles()

    def SetPrivateKey(self, privateKey):
        self.rootPrivateKey = privateKey
    
    def SetPubKey(self, pubKey):
        self.rootPubKey = pubKey
    
    def SetRootCert(self, cert):
        self.rootCert = cert
    
    def GetPrivateKey(self):
        return self.rootPrivateKey

    def GetPubKey(self):
        return self.rootPubKey

    def GetRootCert(self):
        return self.rootCert

    def CreateKey(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        return key
    
    def CreateDSAKey(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        return key

    def CreateCert(self, issuer, subject, pubKey, signKey):
        cert = crypto.X509()

        x509Issuer = cert.get_issuer()
        x509Subject = cert.get_subject()

        FillX509Name(x509Issuer, issuer)
        FillX509Name(x509Subject, subject)

        now = datetime.datetime.now()
        five_yeas_laters = now.replace(year=now.year + 5)

        cert.set_notBefore(now.strftime("%Y%m%d%H%M%SZ").encode("ascii"))
        cert.set_notAfter(five_yeas_laters.strftime("%Y%m%d%H%M%SZ").encode("ascii"))
        cert.add_extensions([])
        cert.set_pubkey(pubKey)
        cert.sign(signKey, "sha1")

        return cert
    
    def Sign(self, key, data):
        return crypto.sign(key, data, "sha256")

    def Verify(self, cert, encryptedData, data):
        try:
            crypto.verify(cert, encryptedData, data, "sha256")
            return True
        except:
            return False

    def LoadCert(self, filename):
        file = open(filename, "r")
        certStr = file.read()
        file.close()

        x509Cert = crypto.load_certificate(crypto.FILETYPE_PEM, certStr)
        
        return x509Cert

    def LoadCertFromString(self, certStr):
        x509Cert = crypto.load_certificate(crypto.FILETYPE_PEM, certStr)

        return x509Cert

    def LoadPrivateKey(self, filename):
        file = open(filename, "r")
        privateKeyStr = file.read()
        file.close()

        privateKey = crypto.load_privatekey(crypto.FILETYPE_PEM, privateKeyStr)

        return privateKey
    
    def LoadPubKey(self, filename):
        file = open(filename, "r")
        pubKeyStr = file.read()
        file.close()

        publicKey = crypto.load_publickey(crypto.FILETYPE_PEM, pubKeyStr)

        return publicKey

    def DumpCert(self, cert):
        certStream = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

        return certStream.decode()

    def DumpPubKey(self, key):
        keyStream = crypto.dump_publickey(crypto.FILETYPE_PEM, key)

        return keyStream.decode()

    def DumpPrivateKey(self, key):
        keyStream = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

        return keyStream.decode()
    
    def SaveCert(self, cert, filename):
        certStr = self.DumpCert(cert)
        file = open(filename, "w")
        file.write(certStr)
        file.close()

    def SavePrivateKey(self, key, filename):
        keyStr = self.DumpPrivateKey(key)
        file = open(filename, "w")
        file.write(keyStr)
        file.close()
        
    def SavePubKey(self, key, filename):
        keyStr = self.DumpPubKey(key)
        file = open(filename, "w")
        file.write(keyStr)
        file.close()

    def LoadCAFiles(self):
        workingDir = os.getcwd()
        if (
            os.path.isfile(os.path.join(workingDir, Certificate.RootCertFileName)) and
            os.path.isfile(os.path.join(workingDir, Certificate.RootPrivateKeyFileName)) and
            os.path.isfile(os.path.join(workingDir, Certificate.RootPubKeyFileName))
        ):
            x509Cert = self.LoadCert(Certificate.RootCertFileName)
            privateKey = self.LoadPrivateKey(Certificate.RootPrivateKeyFileName)
            pubKey = self.LoadPubKey(Certificate.RootPubKeyFileName)

            self.SetRootCert(x509Cert)
            self.SetPrivateKey(privateKey)
            self.SetPubKey(pubKey)