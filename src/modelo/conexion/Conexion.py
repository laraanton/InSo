import jaydebeapi

class Conexion:
  _instancia = None
  def __new__(cls, *args, **kwargs):
    pass

  def __init__(self, host='localhost', database='SoftripDB', user= 'userST', password = 'passST'):
    if self._inicializado:
      return
    self._host = host
    self._database = database
    self._user = user
    self._password = password
    self.conexion = self.createConnection()

   def createConnection(self):
        try:
            jdbc_driver = "com.mysql.cj.jdbc.Driver"
            jar_file = "./lib/mysql-connector-j-9.2.0.jar"
            self.conexion = jaydebeapi.connect(
                jdbc_driver,
                f"jdbc:mysql://{self._host}/{self._database}",
                [self._user, self._password],
                jar_file
            )
            return self.conexion
        except Exception as e:
            print("Error creando conexión:", e)
            return None

  
