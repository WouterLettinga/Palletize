#TODO Look at pickup function! (Weird with parameters)
#TODO Look at dropoff function!
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
from snap7.util import *
from snap7.snap7types import *
import serial
import socket
import time

import xmlrpc.client

import snap7.client as c

#Connect to the PLC

#plc = c.Client()
#plc.connect('192.168.0.3', 0, 1)

Start = [0.00, 0.00, 0.00, -179.64, -1.06, -95.31]

Size = [1200, 800, 2100]

#Function to read a variable out of the PLC
def ReadMemory(plc, byte, bit, datatype):
    result = plc.read_area(areas['DB'], 3, byte, datatype)
    if datatype == S7WLByte:
        return get_int(result, 0)
    else:
        return None

#Function to write a variable to the PLC
def WriteMemory(plc,byte,bit,datatype,value):
    result = plc.read_area(areas['DB'],3,byte,datatype)
    if datatype==S7WLByte:
        set_int(result,0,value)
    plc.write_area(areas["DB"],3,byte,result)

#Function to read the boxtype out of the PLC
def GetBoxtype():
    _boxtype = 1 #ReadMemory(plc, 2, 0, S7WLByte)
    return {
        1: [1, 315, 220, 175, 13.8, 12],
        2: [2, 410, 310, 295, 9.4, 7],
    }[_boxtype]

#Creates a class of the box properties
class Box:
    def __init__(self, Boxparam):
        self.BoxID = Boxparam[0]
        self.Length = Boxparam[1]
        self.Width = Boxparam[2]
        self.Height = Boxparam[3]
        self.Mass = Boxparam[4]
        self.Layers = Boxparam[5]

#Creates a class of the pallet properties
class Pallet:
    def __init__(self, _palletstart, _palletdimension):
        self.palletStart(_palletstart)
        self.palletSize(_palletdimension)

    def palletStart(self, _palletStart):
        self.x = _palletStart[0]
        self.y = _palletStart[1]
        self.z = _palletStart[2]
        self.rx = _palletStart[3]
        self.ry = _palletStart[4]
        self.rz = _palletStart[5]

    def palletSize(self, _palletSize):
        self.PalletLength = _palletSize[0]
        self.PalletWidth = _palletSize[1]
        self.palletHeight = _palletSize[2]


# Connect with Modbus
class FloatModbusClient(ModbusClient):
    def read_float(self, address, number=1):
        reg_l = self.read_holding_registers(address, number * 2)
        if reg_l:
            return [utils.decode_ieee(f) for f in utils.word_list_to_long(reg_l)]
        else:
            return None

    def read_input_registers_float(self, address, number=1):
        reg_1 = self.read_input_registers(address, number * 2)
        if reg_1:
            return [utils.decode_ieee(f) for f in utils.word_list_to_long(reg_1)]
        else:
            return None

    def write_float(self, address, floats_list):
        b32_l = [utils.encode_ieee(f) for f in floats_list]
        b16_l = utils.long_list_to_word(b32_l)
        return self.write_multiple_registers(address, b16_l)

    def write_single_register_float(self, address, floats_list):
        b32_l = [utils.encode_ieee(f) for f in floats_list]
        b16_l = utils.long_list_to_word(b32_l)
        return self.write_single_register(address, b16_l)


# Code for sending the right format to the robot
def send_packet(data, header="TMSCT"):
    if header == "TMSCT":
        data = "1," + str(data)
        package_check = xor_checksum(header, len(data), str(data))
        #        print("$" + header + "," + str(len(data)) + "," + data + "," + package_check + "\r\n")
        return "$" + header + "," + str(len(data)) + "," + data + "," + package_check + "\r\n"
    else:
        package_check = xor_checksum(header, len(data), str(data))
        return "$" + header + "," + str(len(data)) + "," + data + "," + package_check + "\r\n"

# Checksum
def xor_checksum(header, length, data):
    result = 0
    check_package = header + "," + str(length) + "," + data + ","
    for char in check_package:
        result = result ^ ord(char)
    str_hex = "*%0.2X" % result
    return str_hex

#Connection with the robot
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '192.168.0.1'
PORT = 5890

s.connect((HOST, PORT))

Y = xmlrpc.client.ServerProxy('http://localhost:8000')

#Connection with the lift
def liftkit_connect():
    print ("Connecting...")
    Y.com_start('/dev/ttyUSB0', 38400)
    while Y.is_connected() != True:
        print ("Connecting...")
        time.sleep(0.5)
    print ("Connection: ", Y.is_connected())
    print ("Daemon ID: ", Y.get_daemon_id())
    print ("Pillar initialized: ", Y.is_pillar_initialized())
    time.sleep(3)
    return

#Function to read the load cells output, returns output
def mass_payload(mass):
    arduino = serial.Serial('/dev/ttyACM0', 9600)
    data = arduino.readline().decode().rstrip("\r\n")
    line = abs(float(data))

    if mass * 0.7 <= line <= mass * 1.3:
        a = 1
        return a
    else:
        a = 2
        return a

#Returns the liftheight (One boxheight every layer if layer is heigher then 550 mm)
def setLiftheight(stackedLayer, setlift, BoxHeight):
    if BoxHeight * stackedLayer > 550:
        if BoxHeight * setlift > 900 + 650:
            liftheight = 900
            return liftheight
        else:
            liftheight = setlift * BoxHeight
        return liftheight
    else:
        return 0

# Complete pick up function - Move to pick up -> lower -> pick-up -> Go back to pick-up
def pickup_point(stackedLayer, setlift, BoxHeight):
    B = Box(GetBoxtype())
    print ("Box height: ", B.Height)
    print ("Set lift height: ", setLiftheight(stackedLayer, setlift, BoxHeight))
    boxpick = [0.5 * B.Length - 27.5, 0.5 * B.Width + 65, -B.Height + 25 + setLiftheight(stackedLayer, setlift, BoxHeight), 0.00, -4.72, 33.23]
    pickOff = [0.5 * B.Length - 27.5, 0.5 * B.Width + 65, -(2.0 * B.Height) + setLiftheight(stackedLayer, setlift, BoxHeight), 0.00, -4.72, 33.23]
    print ("Box pick: ", boxpick)
    print ("pick: ", pickOff)

    PTP(pickOff)
    checkpoint(pickOff)
    PTP(boxpick)
    checkpoint(boxpick)
    toggle_suck()
    PTP(pickOff)
    checkpoint(pickOff)
    return

# Complete drop function
def drop_point(coords, Layer):
    B = Box(GetBoxtype())

    x = coords[0]
    y = coords[1]
    z = coords[2]
    rx = coords[3]
    ry = coords[4]
    rz = coords[5]

    if Layer % 2 == 0:
        dropOff1 = [x + 100, y + 100, z - 1.5 * B.Height, rx, ry, rz]
    if Layer % 2 != 0:
        dropOff1 = [x + 100, y - 100, z - 1.5 * B.Height, rx, ry, rz]

    dropOff2 = [x, y, z - 0.25 * B.Height, rx, ry, rz]
    drop = [x, y, z - 10, rx, ry, rz]
    dropOff3 = [x, y, z - B.Height, rx, ry, rz]

    PTP(dropOff1)
    checkpoint(dropOff1)
    PTP(dropOff2)
    checkpoint(dropOff2)
    PTP(drop)
    checkpoint(drop)
    toggle_suck()
    PTP(dropOff3)
    checkpoint(dropOff3)
    return


# Safe point (pickup to pallet starting)
def safe_point(_safePoint):
    PTP(_safePoint)
    checkpoint(_safePoint)
    return


# Function for changing the base of the robot
def change_base(basename):
    base_package = 'ChangeBase("' + basename + '")'
    s.send(send_packet(base_package).encode())
    return


# Toggle the end of arm tool
def toggle_suck():
    c = ModbusClient(host="192.168.0.1", auto_open=True)

    stt = c.read_coils(0)
    time.sleep(1)
    if stt == [False]:
        c.write_single_coil(0, 1)
    else:
        c.write_single_coil(0, 0)
    time.sleep(1)
    return


# Check if coordinates of robot are matching the coordinates of the algorithm
def checkpoint(co):
    while True:
        mar = 50  # has to be in mm
        x_pos = int(coords()[0])
        y_pos = int(coords()[1])
        z_pos = int(coords()[2])
        if (float(co[0]) - mar <= x_pos <= float(co[0]) + mar and float(co[1]) - mar <= y_pos <= float(
                co[1]) + mar and float(co[2]) - mar <= z_pos <= float(co[2]) + mar):
            break
        else:
            time.sleep(0.5)
            continue
    return

# Get the realtime coordinates of the robot
def coords():
    c = FloatModbusClient(host='192.168.0.1', port=502, auto_open=True)

    xyz = [c.read_input_registers_float(7025)[0], c.read_input_registers_float(7027)[0],
           (c.read_input_registers_float(7029)[0])]
    return xyz


#Code for sending a point to point to the robot
def PTP(point, head="CPP", speed=35, accel=200, blend=20, precise="false", config="0,2,4"):
    PTP_package = "PTP" + '("' + str(head) + '",'
    for i in range(0, len(point)):
        PTP_package = PTP_package + str(point[i]) + ","
    PTP_package = PTP_package + str(speed) + "," + str(accel) + "," + str(blend) + "," + precise + "," + str(
        config) + ")"
    s.send(send_packet(PTP_package).encode())
    return

#Exit listen node from techman robot
def scriptExit(payload = "scriptExit()"):
    s.send(send_packet(payload).enconde())
    return
