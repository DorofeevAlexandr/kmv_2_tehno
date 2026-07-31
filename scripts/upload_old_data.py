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

    def add_counters_record(self,
                               in_time: dt.datetime,
                               lengths: str,
                               connection_counters: str = '{0}',
                           ):
            insert_query = """ INSERT INTO counters (time, lengths, connection_counters) VALUES (%s,%s, %s)"""
            self.cursor.execute(insert_query, (in_time, lengths, connection_counters))
            connection.commit()

    def read_old_data_csv_file(self, file_name):
        date = dt.datetime.strptime(os.path.split(file_name)[1], "Lines_data_%Y_%m_%d.csv")
        # print(date)
        try:
            with open(file_name, newline='',  errors="replace") as f:
                for row in csv.reader(f, delimiter=';', quotechar='"'):
                    if row[0] != 'Time - 7h' and len(row) < 70:
                        # print(row)
                        time = dt.datetime.strptime(row[0], '%H:%M')
                        dtime = dt.timedelta(hours=time.hour,
                                             minutes=time.minute)
                        dtime_8_hours = dt.timedelta(hours=8)
                        date_time = date + dtime + dtime_8_hours
                        # print(date_time)
                        row = [x if x != '' else '0' for x in row]
                        lengths = '{' + ','.join(row[1:]) + '}'
                        # print(lengths)
                        self.add_counters_record(date_time, lengths)
                    else:
                        # print(row)
                        pass
        except Exception as e:
            print('Ошибка', file_name)
            print(e)

    def get_csv_filenames(self, dir_name):
        files = os.listdir(dir_name)
        complete_files = []
        for file in files:
            # print(file)
            path = os.path.join(dir_name, file)
            # print(complete_path)
            if os.path.isdir(path):
                print(path)
                complete_files = complete_files + self.get_csv_filenames(path)
            else:
                if os.path.splitext(path)[1] == '.csv':
                    complete_files.append(path)
        return complete_files

    def load_old_data(self):
        csv_files = self.get_csv_filenames('/home/amd/projects/kmv_2/data_base_csv')
        files = sorted(csv_files)
        for n, file in enumerate(files):
            self.read_old_data_csv_file(file_name=file)
            print(f"Загружено {n + 1} файлов из {len(files)} - {file}")


if __name__ == '__main__':
    load_dotenv()
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user':  os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'),
           #'host': os.environ.get('DB_HOST', 'db'),
           # 'host': '192.168.211.247',
           'host': 'localhost',
           'port': 5432,
           }
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as connection:
        print(connection)
        pdl = PostgresDataLoader(connection)
        pdl.load_old_data()
        print('Записей в таблице counters  = ', pdl.count_records( 'counters'))
