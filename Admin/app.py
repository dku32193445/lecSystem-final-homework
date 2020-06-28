from Admin import Admin
import requests

from MenuCallbacks import AddAdmin, CreateRootCA, QueryCARequests, Terminate

# id = "root"
# pw = "43b72ee5aa0d4ee09d22249ad276847a"

id = input("관리자 ID : ")
pw = input("관리자 PW : ")

admin = Admin()

r = requests.post("http://localhost:5000/admin/login", data={
    "id" : id,
    "pw" : pw
})

if r.status_code == 200:
    result = r.json()

    admin.Login(id, pw, result["grade"])

def WrapCallback(callback):
    return lambda admin: callback(admin)

Menus = [
    {
        "menu" : "관리자 추가",
        "grade" : 1,
        "callback" : WrapCallback(AddAdmin)
    },
    {
        "menu" : "Root CA 생성",
        "grade" : 1,
        "callback": WrapCallback(CreateRootCA)
    },
    {
        "menu" : "신청 목록 조회",
        "grade" : 2,
        "callback": WrapCallback(QueryCARequests)
    },
    {
        "menu" : "종료",
        "grade" : 2,
        "callback": WrapCallback(Terminate)
    }
]

Menus = list(filter(lambda element: admin.GetGrade() <= element["grade"], Menus))

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

    Menus[menu]["callback"](admin)
