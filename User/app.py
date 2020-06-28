from user import User

from MenuCallbacks import RequestCA, QueryCARequests, ExtendCA, SecureConnection, Terminate

user = User()

# subject = {
#     "countryName" : "kr",
#     "stateOrProvinceName" : "seoul",
#     "localityName" : "user",
#     "organizationName" : "dankook",
#     "organizationalUnitName" : "software dept.",
#     "commonName" : "user-ca",
#     "emailAddress" : "user@ur.se"
# }

subject = {
    "countryName" : "",
    "stateOrProvinceName" : "",
    "localityName" : "",
    "organizationName" : "",
    "organizationalUnitName" : "",
    "commonName" : "",
    "emailAddress" : ""
}

subject["countryName"] = input("countryName(ex : kr) : ")
subject["stateOrProvinceName"] = input("stateOrProvinceName : ")
subject["localityName"] = input("localityName : ")
subject["organizationName"] = input("organizationName : ")
subject["organizationalUnitName"] = input("organizationalUnitName : ")
subject["commonName"] = input("commonName : ")
subject["emailAddress"] = input("emailAddress : ")

user.SetSubject(subject)

print("User가 성공적으로 생성되었습니다.")

def WrapCallback(callback):
    return lambda user: callback(user)
Menus = [
    {
        "menu" : "인증서 신청",
        "callback" : WrapCallback(RequestCA)
    },
    {
        "menu" : "신청 목록 조회",
        "callback": WrapCallback(QueryCARequests)
    },
    {
        "menu" : "인증서 연장",
        "callback": WrapCallback(ExtendCA)
    },
    {
        "menu" : "보안 연결",
        "callback": WrapCallback(SecureConnection)
    },
    {
        "menu" : "종료",
        "callback": WrapCallback(Terminate)
    }
]

def ShowMenu():
    for i in range(len(Menus)):
        print("%d. %s" % (i, Menus[i]["menu"]))

while True:
    ShowMenu()
    menu = input("메뉴를 선택하세요 : ")

    if (not menu.isdigit()):
        print("숫자를 입력해 주세요")
        continue

    menu = int(menu)

    if (not (menu >= 0 and menu < len(Menus))):
        print("잘 못된 메뉴를 선택했습니다.")
        continue

    Menus[menu]["callback"](user)
