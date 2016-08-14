#!/usr/bin/python

"""
Author:    GSSMahadevan
Use   :    Python script to query 9$ Chip's I2C module AXP209
Documents :

http://www.raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2


http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/plain/Documentation/i2c/smbus-protocol
http://wiki.erazor-zone.de/wiki:linux:python:smbus:doc

root@chip:~# i2cdetect -y 0
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- UU -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --        

http://dl.linux-sunxi.org/AXP/AXP209_Datasheet_v1.0en.pdf

"""

import smbus
from uuid import getnode as get_mac
import time
import argparse
import os

DEVICE_ADDRESS = 0x34      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MODE1 = 0x00

tm_fmt='%-24s'
dev_fmt='%-20s'
name_fmt='%-24s'
unit_fmt='%-10s'

show_name=False
show_time=False
show_dev=False
show_unit=False
show_csv=False

dev_str = hex(get_mac())[2:14]
time_str = time.ctime()

def getFmt(valFmt):
	fmt=''
	if show_time: fmt += tm_fmt
	if show_dev:  fmt += (' ',',')[show_csv]  + dev_fmt
	if show_name: fmt += (' ',',')[show_csv]  + name_fmt
	fmt += (' ',',')[show_csv]  + valFmt
	if show_unit: fmt += (' ',',')[show_csv]  + unit_fmt
	#print "DEBUG-------------- Fmt:", fmt
	return fmt

def getVal(val,name,unit):
	vals=[]
	if show_time: vals.append(time_str)
	if show_dev:  vals.append(dev_str)
	if show_name: vals.append(name)
	vals.append(val)
	if show_unit: vals.append(unit)
	tups=tuple(vals)
	#print "DEBUG------------- Vals:", tups
	return tups

def  axp209_read_address(addr):
	#i2cget -f -y 0 0x34 $@
	return bus.read_byte_data(DEVICE_ADDRESS,addr)

def axp209_write_addresses(addresses):
	#i2cset -f -y 0 0x34 $@
	bus.write_block_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, addresses)

def axp209_write_address(addr):
	#i2cset -f -y 0 0x34 $@
	bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, addr)

def axp209_bit_register_value(addr,mask):
	osb_register=axp209_read_address(addr)
	bit_mask=(1 << mask)
	return  (osb_register & bit_mask) / bit_mask 

def axp209_2byte_register_value(addr1,addr2,mask):
	msb_register=axp209_read_address(addr1)
	lsb_register=axp209_read_address(addr2)
	lbit_mask=1 << mask
	value = (msb_register * lbit_mask) | ((lsb_register & 240) / lbit_mask)
	return  value

def temperature():
	v= axp209_2byte_register_value( 0x5E, 0x5F,  4)
	fmt=getFmt('%5.1f')
	print fmt % getVal((v * 0.1 - 144.7), 'temperature','oC')

def ac_voltage():
	v=axp209_2byte_register_value( 0x56, 0x57, 4 )
	fmt=getFmt('%5.1f')
	print fmt %  getVal((v * 1.7), 'ac_voltage','mV')

def vbus_power():
	v=axp209_read_address(0x30)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'vbus_power','')

def irq_enable():
	v=axp209_read_address(0x42)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'irq_enable','')

def blink(num):
	for i in range(num):
		axp209_write_addresses([0x93,0x01])		
		time.sleep(.5)	
		axp209_write_addresses([0x93,0x00])		
		time.sleep(.5)	

def no_limit():
	axp209_write_addresses([ 0x30, 0x03])

def fuel_gauge():
	v=axp209_read_address (0xB9)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'fuel_gauge','')

def shutdown_voltage():
	v=axp209_read_address( 0x46)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'shutdown_voltage','')

def shutdown():
	axp209_write_addresses([ 0x32, 0xC6])

def set_500ma():
	axp209_write_addresses([ 0x30, 0x61])

def no_voltage_drop():
	axp209_write_addresses([ 0x30, 0x35])

def ac_current():
	v=axp209_2byte_register_value( 0x58, 0x59, 4 )
	fmt=getFmt('%6.2f')
	print fmt %  getVal((v * 0.625), 'ac_current','mA')

def battery_voltage():
	v=axp209_2byte_register_value( 0x78, 0x79, 4 )
	fmt=getFmt('%6.2f')
	print fmt %  getVal((v * 1.1), 'battery_voltage','mV')

def charge_current():
	v=axp209_2byte_register_value( 0x7A, 0x7B, 4 )
	fmt=getFmt('%6.2f')
	print fmt %  getVal((v * 0.5), 'charge_current','mA')

def discharge_current():
	v=axp209_2byte_register_value( 0x7C, 0x7D, 5 )
	fmt=getFmt('%6.2f')
	print fmt %  getVal((v * 0.5), 'dicharge_current','mA')

def ac_present():
	v=axp209_bit_register_value (0x00, 7)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'ac_present','')

def reg_0x00_bit2():
	v=axp209_bit_register_value( 0x00, 2)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'reg_0x00_bit2','')

def battery_charging():
	v=axp209_bit_register_value (0x01, 6)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'battery_charging','')

def battery_connected():
	v=axp209_bit_register_value (0x01, 5)
	fmt=getFmt('0x%02x')
	print fmt % getVal(v,'battery_connected','')

def auto_int(x):
    return int(x, 0)


parser = argparse.ArgumentParser(description='AXP209 I2C Command Helper')
parser.add_argument('-t','--temperature', help='Show temperature of axp209',  action='store_true',  required=False)
parser.add_argument('-a','--ac-voltage', help='Show  ac voltage of axp209',  action='store_true',  required=False)
parser.add_argument('-A','--ac-current', help='Show  ac current of axp209',  action='store_true',  required=False)
parser.add_argument('-c','--charge-current', help='Show  charge current of axp209',  action='store_true',  required=False)
parser.add_argument('-d','--discharge-current', help='Show  discharge current of axp209',  action='store_true',  required=False)
parser.add_argument('-v','--vbus-power', help='Show  vbus power of axp209',  action='store_true',  required=False)
parser.add_argument('-i','--irq-enable', help='Enable IRQ of axp209',  action='store_true',  required=False)
parser.add_argument('-B','--blink', help='Blink Chip status LED for 3 times',  action='store_true',  required=False)
parser.add_argument('-n','--no-limit', help='Set no limit on axp209',  action='store_true',  required=False)
parser.add_argument('-f','--fuel-gauge', help='Show battery fuel gauge',  action='store_true',  required=False)
parser.add_argument('-s','--shutdown-voltage', help='Show  shutdown voltage of axp209',  action='store_true',  required=False)
parser.add_argument('-b','--battery-voltage', help='Show  battery voltage of axp209',  action='store_true',  required=False)
parser.add_argument('-p','--ac-present', help='Show  AC presence in axp209',  action='store_true',  required=False)
parser.add_argument('-z','--battery-charging', help='Show  status of battery charging in axp209',  action='store_true',  required=False)
parser.add_argument('-Z','--battery-connected', help='Show  connection status of battery  in axp209',  action='store_true',  required=False)
parser.add_argument('-r','--reg-0x00-bit2', help='Show  status of reg-0x00-bit2  in axp209',  action='store_true',  required=False)

parser.add_argument('-T','--show-time', help='Show  time in output',  action='store_true',  required=False, default=False)
parser.add_argument('-D','--show-device', help='Show  device in output',  action='store_true',  required=False, default=False)
parser.add_argument('-N','--show-name', help='Show  name of sensor in output',  action='store_true',  required=False, default=False)
parser.add_argument('-U','--show-unit', help='Show  unit  of sensor in output',  action='store_true',  required=False, default=False)
parser.add_argument('-F','--force-open', help='Force Open I2C device in case of Device or resource busy',  action='store_true',  required=False, default=False)
parser.add_argument('-C','--csv', help='Separate fields with csv',  action='store_true',  required=False, default=False)

parser.add_argument('-y','--i2c-bus', help='i2c device bus as per /dev/i2c-X',type=int,    required=False, default=0)
parser.add_argument('-Y','--i2c-device', help='i2c device for chip axp209',type=auto_int,    required=False, default=0x34)


parser.add_argument('-l','--loops', help='Number of  loops. Zero means infinite. Default loops=1 ',type=int,    required=False, default=1)
parser.add_argument('-w','--loop-wait', help='Number of seconds during loops. Default loop-wait=60 ',type=int,    required=False, default=60)

args = parser.parse_args()

if  args.show_time :  show_time=True
if  args.show_device :  show_dev=True 
if  args.show_name :  show_name=True
if  args.show_unit :  show_unit=True
if  args.csv :  show_csv=True

if  args.force_open: os.putenv("PY_SMBUS","1") # without this statement and corresponding i2tools C-fix, python code wil not run

loops=args.loops
num_loops=0
while True:
	bus = smbus.SMBus(args.i2c_bus)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
	DEVICE_ADDRESS=args.i2c_device
	time_str = time.ctime()

	if  args.temperature:  temperature()
	if  args.ac_voltage:  ac_voltage()
	if  args.vbus_power  : vbus_power()
	if  args.irq_enable  :  irq_enable()
	if  args.blink  :  blink(3)
	if  args.no_limit  :  no_limit()
	if  args.fuel_gauge  :  fuel_gauge()
	if  args.shutdown_voltage  : shutdown_voltage ()
	if  args.ac_current  :  ac_current()
	if  args.battery_voltage  : battery_voltage ()
	if  args.charge_current  : charge_current ()
	if  args.discharge_current  : discharge_current ()
	if  args.ac_present  :  ac_present()
	if  args.reg_0x00_bit2  :  reg_0x00_bit2()
	if  args.battery_charging  : battery_charging ()
	if  args.battery_connected  : battery_connected()
		
	bus.close()
	if loops != 0:
		num_loops += 1
		if num_loops >= loops : break
	
	time.sleep(args.loop_wait)

		
