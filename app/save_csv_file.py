import csv
from datetime import datetime, timedelta
import os


def append_in_csv(lines_name: list, current_lengths: list):
    shift_hours = 8
    file_name = create_dir(shift_hours=8)
    write_header = not os.path.exists(file_name)
    with open(file_name, mode="a", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\r")
        st_time = str((datetime.now() - timedelta(hours=shift_hours)).hour) + ':' + str(datetime.now().minute)
        if write_header:
            file_writer.writerow(['Time - 7h'] + [line[0] for line in lines_name])
        file_writer.writerow([st_time] + [str(int(c_length[0] * 1000)) for c_length in current_lengths])

def create_dir(shift_hours=0):
    dt = datetime.now() - timedelta(hours=shift_hours)
    year = str(dt.year)
    month = str(dt.month)
    day = str(dt.day)
    file_name = 'Lines_data_' + year + '_' + month + '_' + day + '.csv'
    # basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = '/var/data_base_csv'
    path = os.path.join(basedir,'USER1','sd0' , year, month)
    file_name = os.path.join(path, file_name)
    if not os.path.isdir(path):
        os.makedirs(path)   
    return file_name
