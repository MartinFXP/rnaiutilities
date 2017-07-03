# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of rnaiutilities.
#
# rnaiutilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rnaiutilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rnaiutilities. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import logging

from ._db_query import DatabaseQuery
from ._db_setup import DatabaseInserter
from ._postgres_connection import PostgresConnection
from ._sqlite_connection import SQLiteConnection

logging.basicConfig(
  level=logging.WARNING,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DBMS:
    _postgres_ = "postgres"
    _sqlite_ = "sqlite"

    def __init__(self, db=None):
        self._db_path = db
        if db is None:
            self._db = DBMS._postgres_
        else:
            self._db = DBMS._sqlite_

    def __enter__(self):
        try:
            if self._db != DBMS._sqlite_:
                self.__connection = PostgresConnection()
            else:
                self.__connection = SQLiteConnection(self._db_path)
        except Exception as e:
            logger.error("Could not connect" + str(e))
            exit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__connection.close()

    def query(self, **kwargs):
        q = DatabaseQuery(self.__connection)
        return q.query(**kwargs)

    def insert(self, path):
        d = DatabaseInserter(self.__connection)
        d.insert(path)

    def select(self, select):
        q = DatabaseQuery(self.__connection)
        return q.select(select)