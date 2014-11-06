#!/usr/bin/env python
# Curses menu for DAS BOOT project
# Written by Brett Yoakum

import curses
import time
from subprocess import *
import signal
import sys



GREEN="\033[92m"
WHITE='\033[01;37m'
RED='\033[01;31m' 
CLEAR='\033[00m'


def signal_handler(signal, frame):
	pass


#returns [[cpu number, cpu name],]
def cpu_info():
	#cpu_output = Popen("cat","/proc/cpuinfo"], stdout=PIPE).communicate()[0].split('\n\n')
	cpu_output = Popen(["dmidecode", "-t", "4"], stdout=PIPE).communicate()[0].split('\n\n')
	if len(cpu_output) == 1:
		return ["Error:","Unable to run dmidecode"]
	cpus=[i.split('\n') for i in cpu_output]
	# Cpu sockets is len(cpus) - 2 : (dmidecode header and blank '')
	# cpus[1][i] deffinitions of interest
	# 2 is socket number
	# 37 is Version (Intel(R) Xeon(R) CPU E5-2670 0 @ 2.60GHz)
	a=[]
	for i in range(1,len(cpus) -1):
		try:
			a.append([cpus[i][2][21:], cpus[i][37][10:].rstrip()])
		except:
			pass
	return a

# Returns an array with the management info
def get_management_address():
	output = Popen(["ipmitool","lan","print"], stdout=PIPE).communicate()[0].split('\n')
	management_dict = {}
	for line in output:
		t = line.split(' : ')
		if line.find('IP') >= 0 or line.find('Subnet Mask') >= 0 or line.find('MAC') >= 0:
			management_dict[t[0].rstrip(' ')] = t[1].lstrip(' ')

	#ret_string = "BMC Address: %s %s" % (management_dict['IP Address'],management_dict['MAC Address'])
	ret_array = ['BMC',management_dict['MAC Address'],'Unknown','Unknown', 'None',management_dict['IP Address']]
	return ret_array

# returns [[number of slots, populated slots, size],[errors...],[unpopulated]]
def mem_info():
	mem_output = Popen(["dmidecode", "-t", "17"], stdout=PIPE).communicate()[0].split('\n\n')
	if len(mem_output) == 1:
		return []
	elif len(mem_output) == 2:
		return []
	mem = [i.split('\n') for i in mem_output]
	# Mem amount p len(mem) -2
	# numbers of interest
	# 6 is size '\tSize: <size> MB'
	# 9 is location '\tLocator: PROC  1 DIMM  1 '
	#
	# This should check for consistant size and report error if one or more are different

	##### Put all the dims into [[slot, size]] format
	populated = 0
	modules = []
	for i in range(1,len(mem)-1):
		modules.append([mem[i][9].replace('\tLocator: ',''),mem[i][6].replace('\tSize: ','')])

	##### Check to make sure the first slot is populated then use it as the base to check all other dimms
	
	base_size = modules[0][1]

	##### Check to see which ones are actaully populated
	for i in range(0,len(modules)):
		if modules[i][1][0].isdigit():
			populated += 1
	
	##### Find the errors (ones that differ from the base)
	ret_line = [[str(len(modules)),populated,base_size],[],[]]
	for i in range(1,len(mem) - 1):
		if mem[i][6].replace('\tSize: ','')  == base_size:
			pass
		else:
			if not "Module" in mem[i][6]: 
				ret_line[1].append([mem[i][9].replace('\tLocator: ',''),mem[i][6].replace('\tSize: ','')])
			elif "Module" in mem[i][6]:
				ret_line[2].append([mem[i][9].replace('\tLocator: ',''),mem[i][6].replace('\tSize: ','')])


	return ret_line

# returns [manafacturer, product name, serial number]
def system_info():
	system_output = Popen(["dmidecode", "-t", "1"], stdout=PIPE).communicate()[0].split('\n\n')
	if len(system_output) == 1:
		return ["Error:","Unable to run dmidecode",""]
	system = [i.split('\n') for i in system_output]

	# Numbers of interest
	# 2 manafacturer
	# 3 Prod name
	# 5 serial number
	return [system[1][2][15:].rstrip(), system[1][3][15:].rstrip(), system[1][5][16:].rstrip()]

def scr_print(scr, y, x, print_string, formatting=0):
	height, width = scr.getmaxyx()
	#if (y < height) and (x + len(print_string) < width):
	if (y < height) and (x < width) :
		scr.addstr(y,x,print_string, formatting)

def main():
	stdscr = curses.initscr()
	curses.start_color()
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(1)
	#set the the getch to nonblocking with a .2 sec wait
	curses.halfdelay(2)

	cpu_array = cpu_info()
	mem_array = mem_info()	
	sys_info = system_info()

	
	while 1:
		scr_print(stdscr,0,0, "Saga Node: Server Discovery Tool. %s %s Serial: %s" %(sys_info[0],sys_info[1],sys_info[2]), curses.A_REVERSE)
		stdscr.refresh()
		# Get screen size to make sure we don't break stuff
		
		# Stop ctrl-c from killing the program
		signal.signal(signal.SIGINT, signal_handler)
		try:
			output= Popen(["./interface_helper.sh"], stdout=PIPE).communicate()[0].split('\n')
		except:
			pass
		try:
			output= Popen(["/scripts/interface_helper.sh"], stdout=PIPE).communicate()[0].split('\n')
		except:
			pass
		interfaces=[i.split() for i in output]
		location = 0
		scr_print(stdscr,2,0,'{0:10} {1:20} {2:10} {3:8} {4:10} {5:20}'.format("Interface","MAC Address","Speed","Link","Driver","IP"))
		location += 3
		for x in xrange(0, len(interfaces) - 1):
			try:
				ipaddr =  interfaces[x][5]
			except:
				ipaddr = "none"
			curses.init_pair(1,curses.COLOR_RED, curses.COLOR_BLACK)
			curses.init_pair(2,curses.COLOR_GREEN, curses.COLOR_BLACK)
			if interfaces[x][3] == 'yes':
				color = curses.color_pair(2)
			else:
				color = curses.color_pair(1)	
			scr_print(stdscr,location,0,'{0:10} {1:20} {2:10} {3:8} {4:10} {5:20}'.format(interfaces[x][0],interfaces[x][1],interfaces[x][2],interfaces[x][3],interfaces[x][4],ipaddr), color)
			location += 1
		ma = get_management_address()
		scr_print(stdscr,location,0,'{0:10} {1:20} {2:10} {3:8} {4:10} {5:20}'.format(ma[0],ma[1],ma[2],ma[3],ma[4],ma[5]), curses.color_pair(2))
		location +=2
		scr_print(stdscr,location,0,"--------- CPU Info ---------")
		location += 1
		for x in range(0,len(cpu_array)):
			scr_print(stdscr,location,0,"%s %s" % (cpu_array[x][0], cpu_array[x][1]))
			location += 1
		location += 1
		if len(mem_array) > 0:
			scr_print(stdscr,location,0, "--------- Memory Info ---------")
			location += 1
			scr_print(stdscr,location,0,"%s DIMMs at %s for a total of %s MB" % (mem_array[0][1],mem_array[0][2],str(int(mem_array[0][1]) * int(mem_array[0][2].replace(' MB',''))))) 
			location += 2
			scr_print(stdscr,location,0, "--------- Unpopulated Slots ---------")
			location +=1
			for x in range(0,len(mem_array[2])):
				scr_print(stdscr,location,0, "%s %s" % (mem_array[2][x][0],mem_array[2][x][1]))
				location += 1
			location += 1
			scr_print(stdscr,location,0, "--------- Memory Errors Found ---------")
			location +=1
			for x in range(0,len(mem_array[1])):
				scr_print(stdscr,location,0, "%s %s" % (mem_array[1][x][0],mem_array[1][x][1]))
				location += 1
		stdscr.refresh()
		c = stdscr.getch()
		if c == ord('q'):
			stdscr.keypad(0);
			break
		elif c == ord('p'):
			stdscr.keypad(0);
			break	
	


if __name__ == "__main__":
	try:
		main()
	except:
		pass
	curses.nocbreak(); curses.echo ()
	curses.endwin()


