import os
from flask import Flask, request, jsonify
from db import DB
from cert import Certificate
from utils.PasswordEncrypt import PasswordEncryptContext
from utils.ParseX509Name import ParseX509FromForm
from utils.chunkstring import chunkstring
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

app = Flask(__name__)
DB = DB()
cert = Certificate()
encryptContext = PasswordEncryptContext()

workingDir = os.getcwd()
onceFilePath = os.path.join(workingDir, ".once")
if (not os.path.isfile(onceFilePath)):
    print("First boot up the Logging System")
    print("Initialize Logging System")

    rootID, rootPW = DB.InitDatabase()
    print("Root Account is shown once, if you forgot root pw, delete the .once file and logging system will be reset")
    print("Root ID : ", rootID)
    print("Root PW : ", rootPW)

    onceFile = open(".once", "w")
    onceFile.write("If the .once file has deleted, the logging system will reset")
    onceFile.close()
    

@app.route("/")
def HelloWorld():
    return "Hello, World!"

@app.route("/admin/login", methods=["POST"])
def AdminLogin():
    id = request.form["id"]
    pw = request.form["pw"]
    grade = -1

    hashedPw, adminGrade = DB.GetAdminHashedPassword(id)
    if hashedPw is not None:
        if encryptContext.Verify(pw, hashedPw):
            grade = adminGrade

    res = jsonify({
        "grade" : grade
    })

    return res

@app.route("/admin/signup", methods=["POST"])
def AdminSignup():
    id = request.form["id"]
    pw = request.form["pw"]
    grade = 2

    hashedPw = encryptContext.Encrypt(pw)
    DB.InsertNewAdmin(id, hashedPw, grade)

    res = jsonify({
        "grade" : grade
    })

    return res  

@app.route("/admin/create-root-ca", methods=["GET"])
def AdminCreateRootCA():
    # Root CA는 발급자와 소유자 둘 다 본인이다.
    issuer = Certificate.RootX509Name
    subject = Certificate.RootX509Name

    # Create Root CA
    key = cert.CreateKey()
    cert.SavePrivateKey(key, Certificate.RootPrivateKeyFileName)
    cert.SavePubKey(key, Certificate.RootPubKeyFileName)

    # Self Sign
    rootCert = cert.CreateCert(issuer, subject, key, key)
    cert.SaveCert(rootCert, Certificate.RootCertFileName)

    cert.LoadCAFiles()

    DB.InsertCertLog(issuer, subject, "new")

    res = jsonify({})

    return res

@app.route("/admin/ca/request", methods=["GET"])
def AdminQueryCARequests():
    requests = DB.GetCARequests()

    res = jsonify({
        "list" : requests
    })

    return res

@app.route("/admin/ca/confirm/<int:requestSeq>", methods=["GET"])
def AdminConfirmRequest(requestSeq):
    DB.UpdateCARequest(requestSeq, "confirm")
    
    res = jsonify({})

    return res 

@app.route("/admin/ca/reject/<int:requestSeq>", methods=["GET"])
def AdminRejectRequest(requestSeq):
    DB.UpdateCARequest(requestSeq, "reject")

    res = jsonify({})

    return res 

@app.route("/ca/request", methods=["POST"])
def RequestCA():
    issuer = Certificate.RootX509Name
    subject = ParseX509FromForm(request.form, "sub")

    DB.InsertCertRequest(issuer, subject)

    res = jsonify({})

    return res 

@app.route("/ca/query-ca", methods=["POST"])
def QueryCARequests():
    subject = ParseX509FromForm(request.form, "sub")

    requests = DB.QueryUserCARequests(Certificate.RootX509Name, subject)

    res = jsonify({
        "list" : requests
    })

    return res

@app.route("/ca/issue-ca", methods=["POST"])
def IssueCA():
    subject = ParseX509FromForm(request.form, "sub")
    requestSeq = int(request.form["seq"])

    message = ""
    statusCode = 200

    encryptedUserCert = ""
    userPrivateKey = ""
    userPublicKey = ""
    userCert = ""

    requests = DB.QueryUserCARequests(Certificate.RootX509Name, subject)
    filteredReqests = list(filter(lambda element: element[0]==requestSeq, requests))

    if (len(filteredReqests) == 0):
        statusCode = 400
        message = "Can't find CA request"
    else:
        if filteredReqests[0][1] == "confirm":
            statusCode = 200

            userKey = cert.CreateKey()
            userCert = cert.CreateCert(Certificate.RootX509Name, subject, userKey, cert.GetPrivateKey())

            userPrivateKey = cert.DumpPrivateKey(userKey)
            userPublicKey = cert.DumpPubKey(userKey)
            userCert = cert.DumpCert(userCert)
            encryptedUserCert = cert.Sign(cert.GetPrivateKey(), userCert)
            encryptedUserCert = base64.b64encode(encryptedUserCert).decode()

            DB.UpdateCARequest(requestSeq, "issued")
            DB.InsertCertLog(Certificate.RootX509Name, subject, "new")
        else:
            statusCode = 400
            message = "The request is not confirm"

    res = jsonify({
        "message" : message,
        "privateKey" : userPrivateKey,
        "pubKey" : userPublicKey,
        "cert" : userCert,
        "encryptedCert" : encryptedUserCert
    })
    return res, statusCode

@app.route("/ca/extend-ca", methods=["POST"])
def ExtendCA():
    subject = ParseX509FromForm(request.form, "sub")
    encryptedUserCert = request.form["encryptedUserCert"]
    originUserCert = request.form["originUserCert"]

    message = ""
    statusCode = 200

    newUserCert = ""
    newEncryptedUserCert = ""

    oldEncryptedUserCert = base64.b64decode(encryptedUserCert)
    if cert.Verify(cert.GetRootCert(), oldEncryptedUserCert, originUserCert):
        oldUserCert = cert.LoadCertFromString(originUserCert)
        if oldUserCert.has_expired():
            statusCode = 400
            message = "CA has expired"
        else:
            userPubKey = oldUserCert.get_pubkey()

            newUserCert = cert.CreateCert(Certificate.RootX509Name, subject, userPubKey, cert.GetPrivateKey())
            newUserCert = cert.DumpCert(newUserCert)
            newEncryptedUserCert = cert.Sign(cert.GetPrivateKey(), newUserCert)
            newEncryptedUserCert = base64.b64encode(newEncryptedUserCert).decode()

            DB.InsertCertLog(Certificate.RootX509Name, subject, "extend")
    else:
        statusCode = 400
        message = "Failed to decrypt the cert"

    res = jsonify({
        "message" : message,
        "cert" : newUserCert,
        "encryptedCert" : newEncryptedUserCert
    })
    return res, statusCode

@app.route("/ca/secure-connect", methods=["POST"])
def SecureConnect():
    encryptedUserCert = request.form["encryptedUserCert"]
    originUserCert = request.form["originUserCert"]

    statusCode = 200
    message = ""
    
    securePubKey = ""
    encryptedSecurePrivateKeyChunk = ""

    encryptedUserCert = base64.b64decode(encryptedUserCert)
    if cert.Verify(cert.GetRootCert(), encryptedUserCert, originUserCert):
        userCert = cert.LoadCertFromString(originUserCert)
        userPubKey = userCert.get_pubkey()
        
        secureKey = cert.CreateKey()
        securePubKey = cert.DumpPubKey(secureKey)
        securePrivateKey = cert.DumpPrivateKey(secureKey)

        # pyopenssl은 공개키 암호화를 지원하지 않으므로 pycrypto 라이브러리를 이용해 공개키 암호화 진행
        rsaUserPubKey = RSA.importKey(cert.DumpPubKey(userPubKey))
        cipher = PKCS1_OAEP.new(rsaUserPubKey)

        spkChunk = list(chunkstring(securePrivateKey, 128))
        encryptSPKChunk = []
        for chunk in spkChunk:
            encryptChunk = cipher.encrypt(chunk.encode())  
            encryptChunk = base64.b64encode(encryptChunk).decode()
            encryptSPKChunk.append(encryptChunk)

        encryptedSecurePrivateKeyChunk = encryptSPKChunk
    else:
        statusCode = 400
        message = "Failed to decrypt the cert"

    res = jsonify({
        "message" : message,
        "securePubKey" : securePubKey,
        "encryptedSecurePrivateKeyChunk" : encryptedSecurePrivateKeyChunk
    })
    return res, statusCode
