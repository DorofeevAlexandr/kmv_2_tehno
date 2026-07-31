import csv
import datetime as dt
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import Error
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as _connection
from time import sleep


class PostgresDataLoader:
    def __init__(self, connection: _connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def count_records(self, table_name) -> int:
        query = f'SELECT COUNT(*) FROM {table_name};'
        self.cursor.execute(query)
        return int(self.cursor.fetchall()[0][0])

    def load_record(self, table_name, id):
        query = f"SELECT * FROM {table_name} WHERE id='{str(id)}';"
        self.cursor.execute(query)
        data = self.cursor.fetchall()[0]
        return data

    def add_line_params_record(self, params:dict):
        insert_query = """ INSERT INTO lines (line_number, name, pseudonym, port, modbus_adr, department, 
                       number_of_display, cable_number, cable_connection_number, k, created_dt, description) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(insert_query, (params.get('line_number', '0'),
                                           params.get('name', 'name'),
                                           params.get('pseudonym', 'pseudonym'),
                                           params.get('port', ''),
                                           params.get('modbus_adr', '0'),
                                           params.get('department', '0'),
                                           params.get('number_of_display', '0'),
                                           params.get('cable_number', '0'),
                                           params.get('cable_connection_number', '0'),
                                           params.get('k', '1'),
                                           params.get('created_dt', str(dt.datetime.now())),
                                           params.get('description', ''),
                                           ))
        connection.commit()

    def upload_line_params(self, file_name):
        with open(file_name, newline='') as f:
            for row in csv.reader(f, delimiter=';', quotechar='"'):
                print(row)
                params = {}
                row = [x if x != '' else '0' for x in row]
                params['line_number'] = row[1]
                params['name'] = row[2]
                params['pseudonym'] = row[10]
                params['port'] = row[3]
                params['modbus_adr'] = row[4]
                params['department'] = '1'
                params['number_of_display'] = 10
                params['cable_number'] = 10
                params['cable_connection_number'] = 0
                params['k'] = row[5]
                params['created_dt'] = dt.datetime.now()
                params['description'] = 'description'
                print(params)
                self.add_line_params_record(params=params)


if __name__ == '__main__':
    load_dotenv()
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user':  os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'),
           # 'host': os.environ.get('DB_HOST', 'db'),
           'host': '192.168.211.247',
           # 'host': 'localhost',
           'port': os.environ.get('DB_PORT', 5432),
           }
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as connection:
        print(connection)
        pdl = PostgresDataLoader(connection)
        pdl.upload_line_params(file_name='/home/amd/projects/kmv_2_tehno/scripts/lines_202607311024.csv')
        print('Записей в таблице lines  = ', pdl.count_records( 'lines'))
