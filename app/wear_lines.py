from datetime import datetime

from models import Lines, LinesCurrentParams, Counters
from read_counter import (read_input_registers_modbus_device, get_connection, get_indicator_value,
                          get_plc_indicator_value, get_plc_connection, get_plc_diskret_input_counters,
                          read_discrete_inputs_modbus_device)


COUNTER_SIMULATION = False

def get_speed(dt_old, length, old_length):
    if dt_old is None:
        return None
    dt = datetime.now() - dt_old
    seconds = dt.total_seconds()
    if seconds == 0:
        return 0
    else:
        return 60.0 * (length - old_length) / seconds


def ind_value_vapour_generator(bits):
    if bits:
        try:
            ind_value = 10 if bits[0] != 0 else 1
            if bits[1] != 0:
                ind_value += 100
        except:
            ind_value = 0
    else:
        ind_value = 0
    return ind_value


def read_serial_port_counters(session, lines_params):
    for line in lines_params:
        if line['port'] == 'ttyS0':
            port = '/dev/ttyS0'
        elif line['port'] == 'ttyS1':
            port = '/dev/ttyS1'
        else:
            continue

        if COUNTER_SIMULATION:
            ind_value = datetime.now().second
            conected = False
        else:
            registers = read_input_registers_modbus_device(port=port,
                                                           slave_adr=line['modbus_adr'])
            ind_value = get_indicator_value(registers)
            conected = get_connection(registers)
            # Исключение для вальцов
            if line['line_number'] == 57:
                bits = read_discrete_inputs_modbus_device(port=port,
                                                               slave_adr=line['modbus_adr'])
                # print(57, bits)
                if bits:
                    try:
                        ind_value = 1 if (bits[0] != 0 or bits[1] != 0) else 0
                    except:
                        ind_value = 0
                else:
                    ind_value = 0
                # print(57, ind_value)

            # Исключение для парогенераторов
            if line['line_number'] == 75 or line['line_number'] == 76:
                bits = read_discrete_inputs_modbus_device(port=port,
                                                          slave_adr=line['modbus_adr'])
                ind_value = ind_value_vapour_generator(bits)



        length = ind_value * line['k'] 
        update_line_in_base(session, line,
                            ind_value=ind_value,
                            conected=conected,
                            length=length)

def read_plc_counters(session, lines_params, registers):
    for line in lines_params:
        if line['port'] == 'SL1' or line['port'] == 'SL2':
            if COUNTER_SIMULATION:
                ind_value = datetime.now().second
                conected = False
                if line['line_number'] == 57:
                    ind_value = 1
            else:
                ind_value = get_plc_indicator_value(registers, line['line_number'])
                conected = get_plc_connection(registers, line['line_number'])
                # Исключение для вальцов
                if line['line_number'] == 57:
                    if get_plc_diskret_input_counters(registers, line['line_number']):
                        ind_value = 1

            length = ind_value * line['k']
            update_line_in_base(session, line,
                                ind_value=ind_value,
                                conected=conected,
                                length=length)
        else:
            continue

def read_lines_params_in_base(session):
    params = []
    lines = session.query(Lines).all()
    for line in lines:
        params.append({
            'id' : line.id,
            'line_number' : line.line_number,
            'name' : line.name,
            'pseudonym' : line.pseudonym,
            'port' : line.port,
            'modbus_adr' : line.modbus_adr,
            'department' : line.department,
            'number_of_display' : line.number_of_display,
            'cable_number' : line.cable_number,
            'cable_connection_number' : line.cable_connection_number,
            'k' : line.k,
            'created_dt' : line.created_dt,
            'description' : line.description,
            })
    return params

def read_current_lengths_in_base(session):
    return (session.query(LinesCurrentParams.length).
            order_by(LinesCurrentParams.line_number).all())

def read_current_connections_in_base(session):
    return (session.query(LinesCurrentParams.connection_counter).
            order_by(LinesCurrentParams.line_number).all())

def read_lines_name(session):
    return session.query(Lines.name).order_by(Lines.line_number).all()

def read_lines_current_params_in_base(session, line_number):
    line = session.query(LinesCurrentParams).filter(LinesCurrentParams.line_number==line_number).first()
    if line:
        params = {
            'id' : line.id,
            'line_number' : line.line_number,
            'connection_counter' : line.connection_counter,
            'indicator_value' : line.indicator_value,
            'length' : line.length,
            'speed_line' : line.speed_line,
            'updated_dt' : line.updated_dt,
            }
        return params

def update_line_in_base(session, line_params, ind_value=0, conected=False, length=0):
    line_number = line_params['line_number']
    if current_params := read_lines_current_params_in_base(session, line_number):
        speed_line = get_speed(current_params['updated_dt'], length, current_params['length'])
    else:
        speed_line = 0
    # # Исключение для вальцов
    if line_number == 57 and ind_value == 1:
        if current_params and (current_params['length'] is not None):
            length = current_params['length'] + length
        else:
            length = 0

    # # Исключение для парогенераторов
    if (line_number == 75 or line_number==76) and ind_value != 0:
        if current_params and (current_params['length'] is not None):
            length = current_params['length'] + length
        else:
            length = 0

    line = session.query(LinesCurrentParams).filter(LinesCurrentParams.line_number==line_number).first()
    if line:
        line.indicator_value = ind_value
        line.connection_counter = conected
        line.length = length
        line.speed_line = speed_line
        line.updated_dt = datetime.now()
    else:
        line = LinesCurrentParams(line_number=line_params['line_number'])
    session.add(line)
    session.commit()

def add_in_base_counters(session, current_lengths: list, current_connections: list):
    counters = Counters(time=datetime.now(),
                        lengths=[int(c_l[0] * 1000) for c_l in current_lengths],
                        connection_counters=[c_c[0] for c_c in current_connections]
                        )
    session.add(counters)
    session.commit()
