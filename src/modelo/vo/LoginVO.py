

class LoginVO:
    def __init__(self, email, password_hash):
        self.__email = email
        self.__password_hash = password_hash

    @property
    def email(self):
        return self.__email

    @property
    def password_hash(self):
        return self.__password_hash
