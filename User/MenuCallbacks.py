import requests
from OpenSSL import crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64

def RequestCA(user):
    r = requests.post("http://localhost:5000/ca/request", data=user.GetQuerySubject())
    if (r.status_code == 200):
        print("인증서 요청이 성공했습니다.")
    else:
        print("인증서 요청에 실패했습니다.")

def QueryCARequests(user):
    r = requests.post("http://localhost:5000/ca/query-ca", data=user.GetQuerySubject())
    if (r.status_code == 200):
        requestList = r.json()["list"]
        if len(requestList) == 0:
            print("신청한 인증서 요청이 없습니다.")
        else:
            print("인증서 요청 목록")
            for i in range(len(requestList)):
                state = ""
                if requestList[i][1] == "confirm":
                    state = "승인"
                elif requestList[i][1] == "reject":
                    state = "거부"
                elif requestList[i][1] == "issued":
                    state = "발행된 인증서"
                elif requestList[i][1] == "wait":
                    state = "승인 대기 중인 인증서"

                print("%d. 상태 : %s" % (i, state))

            seq = requestList[int(input("발행할 승인된 인증서를 고르시오 : "))][0]

            r = requests.post("http://localhost:5000/ca/issue-ca", data={
                **user.GetQuerySubject(), 
                "seq" : seq
            })
            result = r.json()

            if (r.status_code == 200):
                encryptedCert = result["encryptedCert"]
                cert = result["cert"]
                privateKey = result["privateKey"]
                pubKey = result["pubKey"]

                file = open("key.pem", "w")
                file.write(privateKey)
                file.close()

                file = open("key.pub", "w")
                file.write(pubKey)
                file.close()

                file = open("ca.crt", "w")
                file.write(cert)
                file.close()

                file = open("encrypt_ca.crt", "w")
                file.write(encryptedCert)
                file.close()

                print("인증서 발급에 성공했습니다.")
            else:
                print("인증서 발급에 실패했습니다.")
                print("사유 : %s" % result["message"])
    else:
        print("신청 목록 조회에 실패했습니다.")

def ExtendCA(user):
    file = open("ca.crt", "r")
    cert = file.read()
    file.close()

    file = open("encrypt_ca.crt", "r")
    encryptedCert = file.read()
    file.close()

    r = requests.post("http://localhost:5000/ca/extend-ca", data={
                **user.GetQuerySubject(), 
                "encryptedUserCert" : encryptedCert,
                "originUserCert" : cert
    })
    result = r.json()

    if (r.status_code == 200):
        encryptedCert = result["encryptedCert"]
        cert = result["cert"]

        file = open("ca.crt", "w")
        file.write(cert)
        file.close()

        file = open("encrypt_ca.crt", "w")
        file.write(encryptedCert)
        file.close()

        print("인증서 갱신에 성공했습니다.")
    else:
        print("인증서 갱신에 실패했습니다.")
        print("사유 : %s" % result["message"])

def SecureConnection(user):
    file = open("key.pub", "r")
    pubKey = file.read()
    file.close()

    file = open("key.pem", "r")
    privateKey = file.read()
    file.close()

    file = open("ca.crt", "r")
    cert = file.read()
    file.close()

    file = open("encrypt_ca.crt", "r")
    encryptedCert = file.read()
    file.close()

    r = requests.post("http://localhost:5000/ca/secure-connect", data={
        **user.GetQuerySubject(), 
        "encryptedUserCert" : encryptedCert,
        "originUserCert" : cert
    })
    result = r.json()

    if (r.status_code is not 200): 
        print("보안 연결에 실패했습니다.")
        print("사유 : %s" % result["message"])
        return

    print("인증서 검증에 성공했습니다.")

    encryptedSecurePrivateKeyChunk = result["encryptedSecurePrivateKeyChunk"]

    k = RSA.importKey(privateKey)
    cipher = PKCS1_OAEP.new(k)

    securePrivateKeyChunk = []
    for chunk in encryptedSecurePrivateKeyChunk:
        b64decodedChunk = base64.b64decode(chunk)
        decryptChunk = cipher.decrypt(b64decodedChunk).decode()
        securePrivateKeyChunk.append(decryptChunk)

    securePrivateKey = "".join(securePrivateKeyChunk)
    securePubKey = result["securePubKey"]

    file = open("secure-key.pem", "w")
    file.write(securePrivateKey)
    file.close()

    file = open("secure-key.pub", "w")
    file.write(securePubKey)
    file.close()

    print("보안 연결 키가 생성되었습니다.")

def Terminate(user):
    exit()