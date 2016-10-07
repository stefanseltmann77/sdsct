# -*- coding: utf-8 -*-
from sdsct.dbinterfaces.con2database import Con2Database
import pymssql


class Con2MSSql(Con2Database):
    """Basic class for access to a Python2MSSql-database."""

    DEFAULT_PORT = 1433

    def connect(self, dsn: str = None,
                user: str = None, password: str = None,
                host: str = None, database: str = None, port: int = DEFAULT_PORT) -> None:
        """Establish a connection to a database

        :param dsn: complete dsn string or name
        :param user: username
        :param password: password for username
        :param host: ip or address of host
        :param database: name of database schema
        :param port: port if not default port of db application
        """
        self.conn = pymssql.connect(server=host, user=user, password=password, database=database, port=port)
        self._cursor = self.conn.cursor()
        if not self._cursor:
            raise Exception("No connection established to {}".format(host))
