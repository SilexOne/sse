import sys
import shutil
import logging
import sqlite3
from datetime import datetime
from os.path import join, dirname
from settings import DATABASE_NAME


class SqliteDatabase:

    def __init__(self):
        """
        This class initializes a SQLite3 database while moving any
        database named sse.db to a backup folder and stores the connection
        into the class attributes
        """
        # Get the file path and also make a backup file path if it's needed
        self.dir_path = dirname(__file__)
        self.abs_path = join(self.dir_path, DATABASE_NAME)
        self.new_abs_file_path = join(join(dirname(self.dir_path), "backup"),
                                      str(datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + '.db'))

        # Move the database into the backup folder if sse.db already exist, and make a new database
        try:
            shutil.move(self.abs_path, self.new_abs_file_path)
        except OSError:
            pass
        try:
            self.connection = sqlite3.connect(self.abs_path)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.exception("Failed to make a connection to the database: e".format(e))
            sys.exit(1)
        logging.info("The database sse.db was created")

    def init_table(self, service):
        """
        Create a table within the database

        :param service: Name of the table to be created
        """
        # The table structure created
        # |      id       |   epoch    | status |
        # |---------------|------------|--------|
        # | 1             | 1519939251 |   0    |
        # | 2             | 1519939263 |   0    |
        # | 3             | 1519939279 |   1    |
        sql_command = """
            CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY,
            epoch timestamp DEFAULT (strftime('%s', 'now')),
            status INTEGER);""".format(service)
        try:
            self.cursor.execute(sql_command)
            logging.info("Created the {} table".format(service))
        except Exception as e:
            logging.exception("Unable to create the {} table: {}".format(service, e))

    def commit_to_sqlite(self, service, status):
        """
        Insert a value of a 1 or 0 (PASS/FAIL) into the status column of a
        service table, the id and time will be added automatically

        :param service: Table name in the database
        :param status: An integer return status from a service test of either a 0 or 1
        """
        sql_command = """
            INSERT INTO {0} (status)
            VALUES ({1});""".format(service, status)
        try:
            self.cursor.execute(sql_command)
            self.connection.commit()
            logging.debug("Inserted result of {} into the {} table".format(status, service))
        except Exception as e:
            logging.exception("Unable to insert result of {} into the {} table: "
                              "{}".format(status, service, e))

    def query_service_table(self, service):
        """
        Query an entire table from the database

        :param service: Name of table to query from
        """
        try:
            self.cursor.execute("SELECT * FROM {}".format(service))
            all_rows = self.cursor.fetchall()
            for row in all_rows:
                print('{0} | {1} | {2}'.format(row[0], row[1], row[2]))
        except Exception as e:
            logging.exception("Unable to SELECT * FROM {}: {}".format(service, e))

    def query_last_service_table(self, service):
        """
        Query the last entry in the table

        :param service: Name of table to query from
        """
        try:
            self.cursor.execute("SELECT * FROM {}".format(service))
            all_rows = self.cursor.fetchall()
            print('{0} | {1} | {2}'.format(all_rows[-1][0], all_rows[-1][1], all_rows[-1][2]))
        except Exception as e:
            logging.exception("Unable to SELECT * FROM {}: e".format(service, e))

    def close_db(self):
        self.connection.close()
        logging.info("Database connection closed")
        try:
            shutil.move(self.abs_path, self.new_abs_file_path)
        except OSError:
            pass
