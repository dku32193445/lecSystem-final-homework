def FillX509Name(x509Name, object):
    x509Name.countryName = object["countryName"]
    x509Name.stateOrProvinceName = object["stateOrProvinceName"]
    x509Name.localityName = object["localityName"]
    x509Name.organizationName = object["organizationName"]
    x509Name.organizationalUnitName = object["organizationalUnitName"]
    x509Name.commonName = object["commonName"]
    x509Name.emailAddress = object["emailAddress"]