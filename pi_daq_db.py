import configparser
from sqlalchemy import create_engine, text

class PiDAQDB:
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read('config_client.ini')   #Read sensitive parameters from the configuration file.

        mysql_config = self.cfg['mysql']

        connection_str = f'mysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}/{mysql_config['database']}'

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