from passlib.context import CryptContext
import uuid

class PasswordEncryptContext:
    def __init__(self):
        self.context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=30000
        )

    def Encrypt(self, password):
        return self.context.encrypt(password)

    def Verify(self, password, hashed):
        return self.context.verify(password, hashed)

if __name__ == "__main__":
    cxt = PasswordEncryptContext()
    password = "".join(str(uuid.uuid4()).split("-"))
    encryptPW = cxt.Encrypt(password)
    print(encryptPW, len(encryptPW))
    print(cxt.Verify(password, encryptPW))