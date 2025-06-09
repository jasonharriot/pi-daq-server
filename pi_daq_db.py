import configparser
from sqlalchemy import create_engine, text

class PiDAQDB:
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read('config_client.ini')   #Read sensitive parameters from the configuration file.

        mysql_config = self.cfg['mysql']
        user=mysql_config['user']
        password = mysql_config['password']
        host = mysql_config['host']
        database = mysql_config['database']

        connection_str = f'mysql://{user}:{password}@{host}/{database}'

        #print(connection_str)

        self.engine = create_engine(connection_str)

        self.reconnect()

    def get_connection(self):
        return self.connection

    def reconnect(self):
        self.connection = self.engine.connect()

    def execute(self, str):
        ret = self.connection.execute(text(str))

        return ret
        
    def commit(self):
        self.connection.commit()
