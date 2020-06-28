import requests

def AddAdmin(admin):
    id = input("새 관리자 ID : ")
    pw = input("새 관리자 PW : ")

    r = requests.post("http://localhost:5000/admin/signup", data={
        "id" : id,
        "pw" : pw
    })

    if r.status_code == 200:
        print("관리자 생성에 성공했습니다.")
    else:
        print("관리자 생성에 실패했습니다.")

def CreateRootCA(admin):
    r = requests.get("http://localhost:5000/admin/create-root-ca")
    if r.status_code == 200:
        print("Root CA 생성에 성공했습니다.")
    else:
        print("Root CA 생성에 실패했습니다.")

def QueryCARequests(admin):
    r = requests.get("http://localhost:5000/admin/ca/request")
    if (r.status_code == 200):
        requestList = r.json()["list"]
        if len(requestList) == 0:
            print("신청한 인증서 요청이 없습니다.")
        else:
            print("인증서 요청 목록")

            for i in range(len(requestList)):
                print("%d. commomName : %s" % (i, requestList[i][13]))
            
            index = int(input("승인 또는 거부할 인증서를 고르시오 : "))
            seq = requestList[index][0]

            print("countryName : ", requestList[index][8])
            print("stateOrProvinceName : ", requestList[index][9])
            print("localityName : ", requestList[index][10])
            print("organizationName : ", requestList[index][11])
            print("organizationalUnitName : ", requestList[index][12])
            print("commonName : ", requestList[index][13])
            print("emailAddress : ", requestList[index][14])

            s = int(input("1. 승인 2. 거부 : "))
            if s == 1:
                r = requests.get("http://localhost:5000/admin/ca/confirm/%d" % (seq))
                if (r.status_code == 200):
                    print("승인에 성공했습니다.")
                else:
                    print("승인에 실패했습니다.")
            else:
                r = requests.get("http://localhost:5000/admin/ca/reject/%d" % (seq))
                if (r.status_code == 200):
                    print("거부에 성공했습니다.")
                else:
                    print("거부에 실패했습니다.")
    else:
        print("신청 목록 조회에 실패했습니다.")

def Terminate(admin):
    exit()