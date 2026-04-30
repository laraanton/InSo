import jaydebeapi

class Conexion:
  def __init__(self, host='localhost', database='SoftripDB', user= 'sa', password = 'olacaracola'):
    self._host = host
    self._database = database
    self._user = user
    self._password = password
    self.conexion = self.createConnection()

   def createConnection(self):
        try:
            jdbc_driver = "com.microsoft.sqlserver.jdbc.SQLServerDrive"
            jar_file = r".\lib\mssql-jdbc-13.4.0.jre11.jar"
            self.conexion = jaydebeapi.connect(
                url,
                [self._user, self._password],
                jar_file
            )
            print("Conexión realizada con éxito")  
            return self.conexion
          
        except Exception as e:
            print("Error creando conexión:", e)
            return None

def getCursor(self):
  if self.conexion is None:
    self.createConnection()
  return self.conexion.cursor()

def clonseConnection(self):
  try:
    if self.conexion:
      self.conexion.close()
      self.conexion = None
except Exception as e:
print("Error cerrando conexión ->", e)

if__name__ == "__main__":
print("Comenzando conexión con SoftripBD ->")
db = Conexion()

  
