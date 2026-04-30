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
            return self.conexion
        except Exception as e:
            print("Error creando conexión:", e)
            return None

  
