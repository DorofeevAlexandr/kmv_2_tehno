from pymodbus import pymodbus_apply_logging_config
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.transaction import (
    #    ModbusAsciiFramer,
    #    ModbusBinaryFramer,
    ModbusRtuFramer,
    ModbusSocketFramer,
    ModbusTlsFramer,
)

def read_input_registers_modbus_device(port='/dev/ttyS0', slave_adr=16,
                                       offset=0, length=9):
    client = ModbusSerialClient(
        method='rtu',
        port=port,
        baudrate=9600,
        framer=ModbusRtuFramer,
        timeout=2,
        retries=3,
        retry_on_empty=False,
        close_comm_on_error=False,
        strict=True,
        bytesize=8,
        parity="N",
        stopbits=1,
        handle_local_echo=False,
    )

    client.connect()
    try:
        rr = client.read_input_registers(offset, length, slave=slave_adr)
    except ModbusException as exc:
        client.close()
        return
    if rr.isError():
        client.close()
        return
    if isinstance(rr, ExceptionResponse):
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()
        return
    # print(rr.registers)
    client.close()
    return rr.registers

def read_discrete_inputs_modbus_device(port='/dev/ttyS0', slave_adr=57,
                                       offset=0, length=2):
    client = ModbusSerialClient(
        method='rtu',
        port=port,
        baudrate=9600,
        framer=ModbusRtuFramer,
        timeout=2,
        retries=3,
        retry_on_empty=False,
        close_comm_on_error=False,
        strict=True,
        bytesize=8,
        parity="N",
        stopbits=1,
        handle_local_echo=False,
    )

    client.connect()
    try:
        rr = client.read_discrete_inputs(offset, length, slave=slave_adr)
        # print(offset, length, slave_adr)
        # print(rr)
        # print(rr.bits)
    except ModbusException as exc:
        client.close()
        return
    if rr.isError():
        client.close()
        return
    if isinstance(rr, ExceptionResponse):
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()
        return
    # print(rr.registers)
    client.close()
    return rr.bits

def get_indicator_value(registers):
    try:
        if registers:
            w0 = registers[0]
            w1 = registers[1]
            return w0 * 65536 + w1
        return 0
    except:
        return 0

def get_connection(registers):
    try:
        if registers:
            w7 = registers[7]
            w8 = registers[8]
            return w7 != 0 and w8 != 0
        return False
    except:
        return False

def get_plc_indicator_value(registers, line_number):
    try:
        offset = (line_number) * 12
        if registers:
            w0 = registers[offset + 0]
            w1 = registers[offset + 1]
            return w0 * 65536 + w1
        return 0
    except:
        return 0

def get_plc_connection(registers, line_number):
    try:
        offset = (line_number) * 12
        if registers:
            w7 = registers[offset + 2]
            w8 = registers[offset + 3]
            return w7 != 0 and w8 != 0
        return False
    except:
        return False

def get_plc_diskret_input_counters(registers, line_number):
    try:
        offset = (line_number) * 12
        if registers:
            return registers[offset + 4] != 0
    except:
        return False

def run_sync_client(host=None, port=None):
    """Run sync client."""

    # activate debugging
    pymodbus_apply_logging_config("DEBUG")


    client = ModbusSerialClient(
        method='rtu',
        port='/dev/ttyS0',
        baudrate=9600,
        framer=ModbusRtuFramer,
        timeout=10,
        retries=3,
        retry_on_empty=False,
        close_comm_on_error=False,
        strict=True,
        bytesize=8,
        parity="N",
        stopbits=1,
        handle_local_echo=False,
    )

    print("connect to server")
    client.connect()
    print('------------------')

    print("get and verify data")
    try:
        rr = client.read_input_registers(0, 9, slave=101)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if rr.isError():
        print(f"Received Modbus library error({rr})")
        client.close()
        return
    if isinstance(rr, ExceptionResponse):
        print(f"Received Modbus library exception ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("close connection")
    client.close()


if __name__ == "__main__":
    run_sync_client()
    reg = read_input_registers_modbus_device(port='/dev/ttyS0', slave_adr=101,
                                             offset=0, length=9)
    print(reg)
