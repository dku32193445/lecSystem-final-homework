class User:
    def __init__(self):
        self.subject = { }
    
    def GetSubject(self):
        return self.subject

    def GetQuerySubject(self):
        return {
            "subCountryName" : self.subject["countryName"],
            "subStateOrProvinceName" : self.subject["stateOrProvinceName"],
            "subLocalityName" : self.subject["localityName"],
            "subOrganizationName" : self.subject["organizationName"],
            "subOrganizationalUnitName" : self.subject["organizationalUnitName"],
            "subCommonName" : self.subject["commonName"],
            "subEmailAddress" : self.subject["emailAddress"]
        }

    def SetSubject(self, subject):
        self.subject = subject

    