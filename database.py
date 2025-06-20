import os
import dotenv

# import engine to load database data
from sqlalchemy import create_engine


dotenv.load_dotenv()


MYSQL_USER = os.getenv("MYSQL_USER", default="root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", default="<PASSWORD>")


class Connection:
    engine = None

    @staticmethod
    def connect(host: str = 'localhost'):
        connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{host}/statlog?charset=utf8"

        Connection.engine = create_engine(connection_string)

    @staticmethod
    def disconnect():
        if Connection.engine is not None:
            Connection.engine.dispose()