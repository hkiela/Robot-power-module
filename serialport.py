__author__ = 'henk'
# serial port module connecting to power module
# Oct 2015
# This module implements the class containing status data, sends regular commands from thread do_update
# and handles requests from the user.

# import section
import serial
import io
import threading
import comportconfig_support
import PM2_support
import logging
import time

# ---- constants ----------------
logfilename = 'log.txt'

# refresh time for status
statusrefreshtime = 0.3   # sec

# -------- class definitions --------------
# class with hardware abstrated variable model ---------
class tpm:
    outputstatus = [0, 0, 0, 0, 0, 0]                   # output ststua: 0=off 1 = on
    batterystatus = [0, 0]                              # battery statys 0 = off 1 = on
    adclabels = ['1','2','3','4','5','6','7','8', '9','10','11','12','13','14','15','16']       # annotation strings for ADC values. Filled from Power Module
    adc_avg = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # actual ADC values
    adc_max = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    adc_min = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    adc_cntr = 0                                        # adc counter in power module signalling health in data qacquisition
    adc_time = 0.0                                      # and the time it takes
    version = ['0', '0', '0']                           # firm ware version in Power module

#---------- global variable with initialisation if needed -----
pmstatus = tpm()

connected = False
parselist = ['1','2','3','4','5','6','7','8']       # list with separated string sections

#======================= functions ======================
# commands for battery control
cmd_bat1 = '$11'
cmd_bat2 = '$12'
cmd_bat_off = '$10'

def do_bat1():
    send(cmd_bat1)
    print('bat1' + cmd_bat1)

def do_bat2():
    send(cmd_bat2)
    print('bat2' + cmd_bat2)

def do_bat_off():
    send(cmd_bat_off)
    print('bat_off' + cmd_bat_off)

#Commands for output control
cmd_out1_on = '$21'
cmd_out2_on = '$22'
cmd_out3_on = '$23'
cmd_out4_on = '$24'
cmd_out5_on = '$25'
cmd_out6_on = '$26'

cmd_out_off = '$30'

cmd_out1_off = '$31'
cmd_out2_off = '$32'
cmd_out3_off = '$33'
cmd_out4_off = '$34'
cmd_out5_off = '$35'
cmd_out6_off = '$36'

# status commands
cmd_get_avg             = '$50'
cmd_get_max             = '$51'
cmd_get_min             = '$52'
cmd_get_output_status   = '$53'
cmd_get_version         = '$58'
cmd_get_counters        = '$59'
cmd_get_adc_labels      = '$60'

# reset commands
cmd_reset_minmax        = '$9'
cmd_reset               = '$8'

# process reset commands
def do_reset():
    send(cmd_reset)
    print('reset' + cmd_reset)

def do_reset_minmax():
    send(cmd_reset_minmax)
    print('reset minmax' + cmd_reset_minmax)

# Process outputs to on/off state
def do_out1():
    if pmstatus.outputstatus[0]:
        send(cmd_out1_off)
        print('out1 off')
    else:
        send(cmd_out1_on)
        print('out1 on')

def do_out2():
    if pmstatus.outputstatus[1]:
        send(cmd_out2_off)
        print('out2 off')
    else:
        send(cmd_out2_on)
        print('out2 on')

def do_out3():
    if pmstatus.outputstatus[2]:
        send(cmd_out3_off)
        print('out3 off')
    else:
        send(cmd_out3_on)
        print('out3 on')

def do_out4():
    if pmstatus.outputstatus[3]:
        send(cmd_out4_off)
        print('out4 off')
    else:
        send(cmd_out4_on)
        print('out4 on')

def do_out5():
    if pmstatus.outputstatus[4]:
        send(cmd_out5_off)
        print('out5 off')
    else:
        send(cmd_out5_on)
        print('out5 on')

def do_out6():
    if pmstatus.outputstatus[5]:
        send(cmd_out6_off)
        print('out6 off')
    else:
        send(cmd_out6_on)
        print('out6 on')

def do_all_off():
    send(cmd_out_off)
    print('all out off')

# Interpret separated string parts
def parse_strings():
    global parselist

# define constants for command recognition of strings from Power module
    reset = 8
    resetminmax = 9
    get_avg = 50
    get_max = 51
    get_min = 52
    get_output_status = 53
    get_version = 58
    get_counters = 59
    get_adc_labels = 60

# first string part indication type of message from Power Module
    if parselist[0].isdecimal():
        received_command = int(float(parselist[0]))
        print("command : {0:d}".format(received_command))

# switch case to detect the kind of packet from Power Module
    if received_command == get_avg:
        handle_get_avg()
    if received_command == get_max:
        handle_get_max()
    if received_command == get_min:
        handle_get_min()
    if received_command == get_output_status:
        handle_get_status()
    if received_command == get_version:
        handle_get_version()
    if received_command == get_counters:
        handle_get_counters()
    if received_command == get_adc_labels:
        handle_get_adc_labels()

def handle_get_avg():           # parse average adc values
    global parselist, pmstatus
    for index in range(15):
        pmstatus.adc_avg[index] = float(parselist[index + 1])/1000
    print('get avg')

def handle_get_max():           # parse max adc values
    global parselist, pmstatus
    for index in range(15):
        pmstatus.adc_max[index] = float(parselist[index + 1])/1000
    print('get mx')

def handle_get_min():           # Parse min value adc
    global parselist, pmstatus
    for index in range(15):
        pmstatus.adc_min[index] = float(parselist[index + 1])/1000
    print('get min')

def handle_get_status():        # parse output status
    global parselist, pmstatus
    pmstatus.batterystatus[0] = int(float(parselist[1]))
    pmstatus.batterystatus[1] = int(float(parselist[2]))
    pmstatus.outputstatus[0] = int(float(parselist[3]))
    pmstatus.outputstatus[1] = int(float(parselist[4]))
    pmstatus.outputstatus[2] = int(float(parselist[5]))
    pmstatus.outputstatus[3] = int(float(parselist[6]))
    pmstatus.outputstatus[4] = int(float(parselist[7]))
    pmstatus.outputstatus[5] = int(float(parselist[8]))
    print(pmstatus.batterystatus[0])
    print('processed output status :')

def handle_get_version():       # parse version
    global parselist, pmstatus
    pmstatus.version[0] = parselist[1]
    pmstatus.version[1] = parselist[2]
    pmstatus.version[2] = parselist[3]
    print('got version info')

def handle_get_counters():      # parse counters
    global parselist, pmstatus
    pmstatus.adc_cntr = int(float(parselist[1]))
    pmstatus.adc_time = int(float(parselist[2]))

    print('get cntrs')

def handle_get_adc_labels():    # parse adc labels
    global parselist, pmstatus
    pmstatus.adclabels[0] = parselist[2]
    pmstatus.adclabels[1] = parselist[3]
    pmstatus.adclabels[2] = parselist[4]
    pmstatus.adclabels[3] = parselist[5]
    pmstatus.adclabels[4] = parselist[6]
    pmstatus.adclabels[5] = parselist[7]
    pmstatus.adclabels[6] = parselist[8]
    pmstatus.adclabels[7] = parselist[9]
    pmstatus.adclabels[8] = parselist[10]
    pmstatus.adclabels[9] = parselist[11]
    pmstatus.adclabels[10] = parselist[12]
    pmstatus.adclabels[11] = parselist[13]
    pmstatus.adclabels[12] = parselist[14]
    pmstatus.adclabels[13] = parselist[15]
    pmstatus.adclabels[14] = parselist[16]
    pmstatus.adclabels[15] = parselist[17]
    print('got adc labels')

# Check and parse incoming string into separated parts
def separate_string(instr):
    global parselist
    # search for $.
    dollarpos = instr.find("$")
    print (instr)
    print("$ found at: ", (dollarpos))
    if dollarpos > -1:
        instr = instr[dollarpos+1:] # strip left part of string including dollar sign
        parselist = instr.split(",")
        print('Separated strings: ')
        print(parselist)
        for item in range(len(parselist)):      # strip spaces from string items
            parselist[item] = parselist[item].strip(" ")
        parse_strings()    # interpret data in string parts
    else:
        print("!!! $ sign missing")

# ----------------- Serial port handling routines ---------------------------------
# thread function reading lines from comport
def reader():
    global connected, ser
    # loop forever and copy serial->console
    while 1:
        if (connected):
            data = ser.readline()
            if len(data) > 0:
                data_decoded = data.decode('utf-8')             # decode to ascii
                print('in:' + data_decoded)
#                PM2_support.dumpline('in:' + data_decoded)      # sghow line in debug window of main form
                separate_string(data_decoded)       # parse incoming string into a separated list

# Send line to serial port
def send(linput):
    global ser
    outstr = linput + '\r\n'        # add cr lf to string
    ser.write(outstr.encode('utf-8'))
    print("out> " + outstr )

# initialize program and variables
def init_vars():
#    global received_command
#    global connected, logger
    global connected, r, logger
    logging.basicConfig(format='%(asctime)s %(message)s')           # initialize logging
    logging.basicConfig(filename=logfilename,level=logging.INFO)     # open log file for debug
    logger = logging.getLogger('start log')

    t = threading.Thread(target=do_update)             # create read thread
    t.setDaemon(1)
    t.start()

    connected = False
    r = threading.Thread(target=reader)             # create read thread
    r.setDaemon(1)
    r.start()

    print('init serialport' + ' logging to: ' + logfilename )

def open_serial():
    global logger, ser, connected
    init_vars()   # init variables
    ''' open serial port with timeout '''
#    global ser, connected, r      #global to allow read and write functions access
    serialconfig = comportconfig_support.Readconfig()
    print(serialconfig)
#    ser = serial.Serial(port='COM3', baudrate=250000, parity=serial.PARITY_NONE,
#                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
#                        timeout=0.1)
#    ser.close()
    ser = serial.Serial(port=serialconfig['comport'], baudrate=serialconfig['baudrate'], parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                        timeout=0.1)
    connected = True
    logger.info('serial port open ' + serialconfig['comport'] + ' ' + serialconfig['baudrate'] )
    print('serial port open ' + serialconfig['comport'] + ' ' + serialconfig['baudrate'] )
    run_once()  # run some commands at the start of communication to get version, labels, etc from power module

def close_serial():
    global ser, connected
    print('close serialport')
    connected = False
    ser.close()             # close port

# Check if port is open
def isportopen():
    global connected
    if connected:
        print('connected status True')
    else:
        print('connected status False')

    return connected

#------------- Run once after initialisation -----------------
def run_once():
    if isportopen():
        send(cmd_get_version)
        send(cmd_get_adc_labels)
        send(cmd_reset_minmax)

#------------- Run periodic functions-----------------
# send periodic command to power module for status update
def do_update():
    global t
    while 1:
        print('Thread update PM status')
        time.sleep(statusrefreshtime)
        if isportopen():
            send(cmd_get_avg)
            send(cmd_get_min)
            send(cmd_get_max)
      #      time.sleep(0.5)
            send(cmd_get_output_status)