from src.modelo.dao.UserDAO import UserDAO

class Logica():
  def ejemploSelect(self):
    userDAO = UserDAO()
    usuarios = userDAO.select()

    for user in usuarios:
      print(user.__nombre)
