"""
Serial protocol decoder for UNI-T UT61C (GS).
"""

import serial
import time

BV = lambda x: 1 << x

FLAGS = {
    BV(0): 'BPN', # Bargraph rule
    BV(1): 'HOLD',
    BV(2): 'REL',
    BV(3): 'AC',
    BV(4): 'DC',
    BV(5): 'AUTO',
    # Bits 6 and 7 are always zero
    BV(8): 'Z3',
    BV(9): 'n',
    BV(10): 'Bat',
    BV(11): 'APO',
    BV(12): 'MIN',
    BV(13): 'MAX',
    BV(14): 'Z2',
    BV(15): 'Z1',
    BV(16): 'Z4',
    BV(17): '%',
    BV(18): 'Diode',
    BV(19): 'Beep',
    BV(20): 'M',
    BV(21): 'k',
    BV(22): 'm',
    BV(23): 'µ',
    BV(24): '°F',
    BV(25): '°C',
    BV(26): 'F',
    BV(27): 'Hz',
    BV(28): 'hFE',
    BV(29): 'Ohm',
    BV(30): 'A',
    BV(31): 'V',
    
}

# Open the serial port
# FS9922-DMM4 use 2400bps 8N1 serial
#with serial.Serial('/dev/ttyUSB0', 2400) as ser:
ser = serial.Serial('/dev/ttyUSB0', 2400)
for i in range(0,1):
    print(i)

    # DTR/RTS is used as power lines
    ser.dtr = True
    ser.rts = False
    x = 0 
    # Until end of time
    while True:
        print(x)
        x +=1
        if x == 20:
            break
        flags = set()

        # Read a line of data
        line = ser.read(14)
        if not line:
            continue

        # Line must be 14 bytes long
        if len(line) != 14:
            print('ERROR: Bad line', line.hex())
            continue

        # Decode DMM data
        # Byte 0: Sign
        if line[0] == 0x2B:
            sign = 1
        elif line[0] == 0x2D:
            sign = -1
        else:
            print('ERROR: Sign is', hex(line[0]))
            continue
            
        # Byte 1-4: Digits
        if line[1:5] == b'?0:?':
            digits = 0
            flags.add('O.L')
        else:
            try:
                digits = int(line[1:5])
            except ValueError:
                print('ERROR: Data is', line[1:5].hex())
                continue
            
        # Byte 5: Space
        if line[5] != 0x20:
            print('ERROR: Space is', hex(line[5]))
            
        # Byte 6: Decimal point position
        if line[6] == 0x30:
            point = 0
            flags.add('BLANK')
        elif line[6] == 0x31:
            point = 1.0
        elif line[6] == 0x32:
            point = 0.001
        elif line[6] == 0x33:
            point = 0.01
        elif line[6] == 0x34:
            point = 0.1
        else:
            print('ERROR: Point is', hex(line[6]))
            continue
            
        # Byte 7-10: Flags
        raw_flags = int.from_bytes(line[7:11], byteorder='little')
        if raw_flags & 0b11000000:
            print('ERROR: SB1~4 is', line[7:11].hex())
            continue
        for bitmask, flag in FLAGS.items():
            if raw_flags & bitmask:
                flags.add(flag)
            
        # Byte 11: Bargraph
        raw_bargraph = line[11]
        bargraph = raw_bargraph & 0b111111
        if raw_bargraph & 128:
            bargraph *= -1
        
        # Byte 12-13: End-of-frame
        if line[12] != 0x0D:
            print('ERROR: EOF is', hex(line[12]))
            continue
        if line[13] != 0x0A:
            print('ERROR: NEWLINE is', hex(line[13]))
            continue

        # Print info
        print('Data:', sign * digits * point)
        print('Bargraph:', bargraph)
        print('Flags:', flags)
    time.sleep(2)