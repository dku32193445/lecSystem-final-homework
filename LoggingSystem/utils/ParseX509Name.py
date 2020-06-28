def ParseX509FromForm(form, prefix):
    x509NameList = [
        "CountryName", "StateOrProvinceName", 
        "LocalityName", "OrganizationName", 
        "OrganizationalUnitName", "CommonName", "EmailAddress"]

    data = {
        "countryName" : "", 
        "stateOrProvinceName" : "", 
        "localityName": "", 
        "organizationName" : "", 
        "organizationalUnitName" : "", 
        "commonName" : "", 
        "emailAddress" : ""
    }

    for name in x509NameList:
        data["".join([name[0:1].lower(), name[1:]])] = form["".join([prefix,name])]

    return data