import sqlite3
import uuid

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("cert.db", check_same_thread=False)

    def __del__(self):
        self.conn.close()    
    
    def InitDatabase(self):
        print("Initialize Database")

        self.__CreateDatabaseScheme()
        root = self.__CreateRoot()

        return root

    def InsertCertRequest(self, issuer, subject):
        issuerSeq = self.__FindIssuerSeq(issuer)
        if issuerSeq is None:
            issuerSeq = self.__InsertX509Name(issuer)

        subjectSeq = self.__FindSubjectSeq(subject)
        if subjectSeq is None:
            subjectSeq = self.__InsertX509Name(subject)

        sql = '''
        INSERT INTO CertRequest (issuer_seq, subject_seq, state) VALUES(?,?, 'wait')
        '''
        c = self.conn.cursor()
        c.execute(sql, (issuerSeq, subjectSeq))

        self.conn.commit()

    def InsertCertLog(self, issuer, subject, action):
        issuerSeq = self.__FindIssuerSeq(issuer)
        if issuerSeq is None:
            issuerSeq = self.__InsertX509Name(issuer)

        subjectSeq = self.__FindSubjectSeq(subject)
        if subjectSeq is None:
            subjectSeq = self.__InsertX509Name(subject)

        sql = '''
        INSERT INTO CertLog (issuer_seq, subject_seq, date, action) VALUES(?,?,datetime('now'),?)
        '''
        c = self.conn.cursor()
        c.execute(sql, (issuerSeq, subjectSeq, action))

        self.conn.commit()

    def GetAdminHashedPassword(self, id):
        selectPwSQL = '''
            SELECT pw, grade FROM admin WHERE id=?
        '''

        c = self.conn.cursor()
        for row in c.execute(selectPwSQL, (id,)):
            return row

    def InsertNewAdmin(self, id, password, grade):
        insertRootSQL = '''
            INSERT INTO admin (id, pw, grade) VALUES(?, ?, ?)
        '''

        c = self.conn.cursor()
        c.execute(insertRootSQL, (id, password, grade))

        self.conn.commit()

    def GetCARequests(self):
        selectCertRequestsSQL = '''
            SELECT
                CR.seq AS seq, 
                N1.countryName AS issCountryName, N1.stateOrProvinceName AS issStateOrProvinceName, 
                N1.localityName AS issLocalityName, N1.organizationName AS issOrganizationName,
                N1.organizationalUnitName AS issOrganizationalUnitName, N1.commonName AS issCommonName, 
                N1.emailAddress AS issEmailAddress,

                N2.countryName AS subCountryName, N2.stateOrProvinceName AS subStateOrProvinceName, 
                N2.localityName AS subLocalityName, N2.organizationName AS subOrganizationName,
                N2.organizationalUnitName AS subOrganizationalUnitName, N2.commonName AS subCommonName, 
                N2.emailAddress AS subEmailAddress
            FROM CertRequest AS CR
            INNER JOIN X509Name AS N1 ON CR.issuer_seq=N1.seq
            INNER JOIN X509Name AS N2 ON CR.subject_seq=N2.seq
            WHERE state="wait"
        '''

        c = self.conn.cursor()
        c.execute(selectCertRequestsSQL)
        return c.fetchall()

    def QueryUserCARequests(self, issuer, subject):
        issuerSeq = self.__FindIssuerSeq(issuer)
        subjectSeq = self.__FindSubjectSeq(subject)

        selectCertRequestsSQL = '''
            SELECT
                seq, state 
            FROM CertRequest
            WHERE 
                issuer_seq = ? AND
                subject_seq = ? 
        '''

        c = self.conn.cursor()
        c.execute(selectCertRequestsSQL, (issuerSeq, subjectSeq))
        return c.fetchall()

    def UpdateCARequest(self, seq, state):
        sql = '''
            UPDATE CertRequest 
            SET state = ? 
            WHERE seq = ?;
        '''

        c = self.conn.cursor()
        c.execute(sql, (state, seq))

        self.conn.commit()

    def __CreateDatabaseScheme(self):
        dropAdmin = '''
            DROP TABLE IF EXISTS admin
        '''
        dropX509Name = '''
            DROP TABLE IF EXISTS X509Name
        '''
        dropCertLog = '''
            DROP TABLE IF EXISTS CertLog
        '''
        dropCertRequest = '''
            DROP TABLE IF EXISTS CertRequest
        '''

        adminScheme = '''
            CREATE TABLE admin(
                `seq` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `id` TEXT NOT NULL,
                `pw` TEXT NOT NULL,
                `grade` INTEGER NOT NULL
            )
        '''

        x509NameScheme = '''
            CREATE TABLE X509Name(
                `seq` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `countryName` TEXT,
                `stateOrProvinceName` TEXT,
                `localityName` TEXT,
                `organizationName` TEXT,
                `organizationalUnitName` TEXT,
                `commonName` TEXT,
                `emailAddress` TEXT
            )
        '''

        certLogScheme = '''
            CREATE TABLE CertLog(
                `seq` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `issuer_seq` INTEGER NOT NULL,
                `subject_seq` INTEGER NOT NULL,
                `date` TEXT NOT NULL,
                `action` TEXT NOT NULL
            )
        '''

        certRequestScheme = '''
            CREATE TABLE CertRequest(
                `seq` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `issuer_seq` INTEGER NOT NULL,
                `subject_seq` INTEGER NOT NULL,
                `state` TEXT NOT NULL
            )
        '''

        c = self.conn.cursor()
        c.execute(dropAdmin)
        c.execute(dropCertLog)
        c.execute(dropCertRequest)
        c.execute(dropX509Name)

        c.execute(adminScheme)
        c.execute(x509NameScheme)
        c.execute(certLogScheme)
        c.execute(certRequestScheme)
        
        self.conn.commit()

    def __CreateRoot(self):
        rootId = "root"
        rootPw = "".join(str(uuid.uuid4()).split("-")) #generate random string
    
        self.InsertNewAdmin(rootId, rootPw, 1)

        return (rootId, rootPw)
    
    def __FindIssuerSeq(self, issuer):
        sql = '''
        SELECT seq FROM X509Name 
        WHERE
            countryName = ? AND
            stateOrProvinceName = ? AND 
            localityName = ? AND
            organizationName = ? AND 
            organizationalUnitName = ? AND
            commonName = ? AND
            emailAddress = ?
        '''

        c = self.conn.cursor()
        c.execute(sql, (
            issuer["countryName"], 
            issuer["stateOrProvinceName"], 
            issuer["localityName"], 
            issuer["organizationName"], 
            issuer["organizationalUnitName"], 
            issuer["commonName"], 
            issuer["emailAddress"]
        ))

        fetch = c.fetchone()
        if fetch is None:
            return None
        else:
            return fetch[0] 
    
    def __FindSubjectSeq(self, subject):
        sql = '''
        SELECT seq FROM X509Name 
        WHERE
            countryName = ? AND
            stateOrProvinceName = ? AND
            localityName = ? AND
            organizationName = ? AND 
            organizationalUnitName = ? AND
            commonName = ? AND
            emailAddress = ?
        '''

        c = self.conn.cursor()
        c.execute(sql, (
            subject["countryName"], 
            subject["stateOrProvinceName"], 
            subject["localityName"], 
            subject["organizationName"], 
            subject["organizationalUnitName"], 
            subject["commonName"], 
            subject["emailAddress"]
        ))

        fetch = c.fetchone()
        if fetch is None:
            return None
        else:
            return fetch[0] 

    def __InsertX509Name(self, x509):
        sql = '''
        INSERT INTO X509Name 
            (countryName, 
            stateOrProvinceName, 
            localityName, 
            organizationName, 
            organizationalUnitName, 
            commonName, 
            emailAddress)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        '''

        c = self.conn.cursor()
        c.execute(sql, (
            x509["countryName"], 
            x509["stateOrProvinceName"], 
            x509["localityName"], 
            x509["organizationName"], 
            x509["organizationalUnitName"], 
            x509["commonName"], 
            x509["emailAddress"]
        ))

        self.conn.commit()

        sql = '''
            SELECT last_insert_rowid()
        '''
        c.execute(sql)

        fetch = c.fetchone()
        if fetch is None:
            return None
        else:
            return fetch[0] 
