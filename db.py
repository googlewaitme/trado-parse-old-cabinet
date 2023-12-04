"""
develop by googlewaitme
04.12.2023
"""
import logging
import psycopg2
from psycopg2 import OperationalError


class DBConnector:
    '''Connect to remote database'''
    def __init__(self, host, database, user, password) -> None:
        try:
            self.conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.conn.cursor()
            logging.info("database is connected")
        except OperationalError as e:
            logging.error(str(e))
            raise e
        self._create_table()

    def __del__(self) -> None:
        if self.conn:
            self.conn.close()
            logging.info("database is closed")

    def save(self, var_name: str, value: str) -> None:
        "save variable in database by string name and string value"
        if self.is_exists(var_name):
            self._update_var(var_name, value)
        else:
            self._create_var(var_name, value)

    def get(self, var_name: str) -> str:
        "return value of variable"
        return self._get_var(var_name)[0][2]

    def is_exists(self, variable: str) -> bool:
        "check variable is exists in database"
        data = self._get_var(variable)
        return len(data) > 0

    def _create_var(self, variable: str, value: str) -> None:
        self.cursor.execute(
            f"INSERT INTO Vars(name, value) VALUES ('{variable}', '{value}')"
        )
        self.conn.commit()

    def _update_var(self, variable: str, value: str) -> None:
        self.cursor.execute(
            f"UPDATE Vars SET value = '{value}' WHERE name = '{variable}'"
        )
        self.conn.commit()

    def _get_var(self, variable: str) -> str:
        self.cursor.execute(
            f"SELECT * FROM Vars WHERE name = '{variable}'"
        )
        return self.cursor.fetchall()

    def _create_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vars (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            value TEXT NOT NULL
        )""")
        self.conn.commit()
