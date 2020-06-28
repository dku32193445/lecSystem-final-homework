class Admin:
    def __init__(self):
        self.id = ""
        self.pw = ""
        self.grade = ""
    
    def Login(self, id, pw, grade):
        self.id = id
        self.pw = pw
        self.grade = grade

    def GetGrade(self):
        return self.grade