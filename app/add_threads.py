import datetime as dt
from dotenv import load_dotenv
import os
from pyModbusTCP.client import ModbusClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import time
from threading import Thread, Lock

from save_csv_file import append_in_csv
from wear_lines import (read_current_lengths_in_base, read_current_connections_in_base, read_lines_name,
                        add_in_base_counters)

load_dotenv()
PLC_HOST = os.environ.get('PLC_HOST')
PLC_PORT = 502

# set global
regs = {key: 0 for key in range(0, 800)}
# print(regs)

stack_of_writable_register = []

# init a thread lock
regs_lock = Lock()

# modbus polling thread
def polling_thread():
    global regs
    c = ModbusClient(host=PLC_HOST, port=PLC_PORT)
    # polling loop
    while True:
        # keep TCP open
        if not c.is_open():
            c.open()
        # do modbus reading on socket
        reg_list_0 = c.read_holding_registers(0, 100)
        reg_list_1 = c.read_holding_registers(100, 100)
        reg_list_2 = c.read_holding_registers(200, 100)
        reg_list_3 = c.read_holding_registers(300, 100)
        reg_list_4 = c.read_holding_registers(400, 100)
        reg_list_5 = c.read_holding_registers(500, 100)
        reg_list_6 = c.read_holding_registers(600, 100)
        reg_list_7 = c.read_holding_registers(700, 100)

        # if read is ok, store result in regs (with thread lock synchronization)
        if reg_list_0 and reg_list_1 and reg_list_2 and reg_list_3 and reg_list_4 and reg_list_5 and reg_list_6 and reg_list_7:
            with regs_lock:
                for i in range(0, 100):
                    regs[0 + i] = reg_list_0[i]
                for i in range(0, 100):
                    regs[100 + i] = reg_list_1[i]
                for i in range(0, 100):
                    regs[200 + i] = reg_list_2[i]
                for i in range(0, 100):
                    regs[300 + i] = reg_list_3[i]
                for i in range(0, 100):
                    regs[400 + i] = reg_list_4[i]
                for i in range(0, 100):
                    regs[500 + i] = reg_list_5[i]
                for i in range(0, 100):
                    regs[600 + i] = reg_list_6[i]
                for i in range(0, 100):
                    regs[700 + i] = reg_list_7[i]

                while stack_of_writable_register:
                    regs_addr, regs_values = stack_of_writable_register.pop()
                    print('write->', regs_addr, regs_values)
                    c.write_multiple_registers(regs_addr, regs_values)

        # 5s before next polling
        time.sleep(5)

def get_registers():
    with regs_lock:
         result = regs.copy()
    return result

def write_register(reg_adr: int, new_value: int):
    stack_of_writable_register.append((reg_adr, new_value))


def postgres_engine():
    load_dotenv()
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'db')
    # db_host = 'localhost'
    db_port = str(os.environ.get('DB_PORT', 5432))

    # Connecto to the database
    db_string = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    # print(db_string)
    result_engine = create_engine(db_string)
    print(result_engine)
    return result_engine


def read_current_params_save_in_base(p_engine):
    with Session(autoflush=False, bind=p_engine) as db:
        current_lengths = read_current_lengths_in_base(db)
        # print(current_lengths)
        current_connections = read_current_connections_in_base(db)
        # print(current_connections)
        lines_name = read_lines_name(db)
        # print(lines_name)

        append_in_csv(lines_name=lines_name, current_lengths=current_lengths)
        add_in_base_counters(db, current_lengths=current_lengths, current_connections=current_connections)
        try:
            pass
        except Exception as e:
            print('error', e)

def read_current_params_save_in_base_thread():
    engine = postgres_engine()
    dt_last_save_lengths = dt.datetime.now()
    while True:
        time.sleep(1)

        if ((0 <= dt.datetime.now().second < 30 ) and
                (dt.datetime.now() - dt_last_save_lengths > dt.timedelta(seconds=30))):
            # print(dt_last_save_lengths)
            dt_last_save_lengths = dt.datetime.now()
            # print('dt_last_save_lengths', dt_last_save_lengths)
            read_current_params_save_in_base(p_engine=engine)

# start polling thread
# tp = Thread(target=polling_thread)
read_save_in_base_thread = Thread(target=read_current_params_save_in_base_thread)
# set daemon: polling thread will exit if main thread exit
# tp.daemon = True
read_save_in_base_thread.daemon = True
# tp.start()
read_save_in_base_thread.start()


if __name__ == '__main__':
    while True:
        get_registers()
        write_register(reg_adr=1, new_value=123)
        time.sleep(1)
