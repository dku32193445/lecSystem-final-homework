import requests

# r = requests.post("http://localhost:5000/admin/login", data={
#     "id" : "root",
#     "pw" : "43b72ee5aa0d4ee09d22249ad276847a"
# })
# print(r.text)

# r = requests.post("http://localhost:5000/admin/create-root-ca", data={
#     "issCountryName" : "kr",
#     "issStateOrProvinceName" : "seoul",
#     "issLocalityName" : "root",
#     "issOrganizationName" : "dankook",
#     "issOrganizationalUnitName" : "software dept.",
#     "issCommonName" : "root-ca",
#     "issEmailAddress" : "root@rt.oo",

#     "subCountryName" : "kr",
#     "subStateOrProvinceName" : "seoul",
#     "subLocalityName" : "root",
#     "subOrganizationName" : "dankook",
#     "subOrganizationalUnitName" : "software dept.",
#     "subCommonName" : "root-ca",
#     "subEmailAddress" : "root@rt.oo"
# })
# r = requests.get("http://localhost:5000/admin/create-root-ca")
# print(r.text)

# r = requests.get("http://localhost:5000/admin/ca/request")
# print(r.text)

r = requests.get("http://localhost:5000/admin/ca/confirm/8")
print(r.text)
# r = requests.get("http://localhost:5000/admin/ca/reject/2")
# print(r.text)