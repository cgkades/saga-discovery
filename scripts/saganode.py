#!/usr/bin/python

import sys
import subprocess
import requests
import argparse
import os
import socket, struct
os.environ["PATH"] += os.pathsep + "/sbin" + os.pathsep + "/usr/sbin"
from repobuilder import RepoBuilder
try:
	import json
except ImportError:
	import simplejson as json


class SagaNode():
	def __init__(self):
		self.location = 'Temp Location'
		self.headers = {'content-type': 'application/json'}
		self.facts = None
		self.boot_args = None
		self.discovery_server = None
		self.repos = RepoBuilder()

	def initalize(self):
		self._parse_boot_args()
		self._get_discovery_server()
		self._get_location()
		self._get_facts()

	#Process arguments passed to the kernel at boot
	def _parse_boot_args(self):
		boot_args = {}
		tmp_args = open('/proc/cmdline', 'r')
		tmp_args = tmp_args.read();
		tmp_args = tmp_args.split(' ')
		tmp_args = map(lambda x: x.split('='), tmp_args)

		for item in tmp_args:
			if (len(item) == 1):
				item.append(True);
			boot_args[item[0]] = item[1]
		self.boot_args = boot_args

	#Running arbitarty commands
	def _do_action(self,cmd):
		if "reboot" in cmd and len(cmd) == 1:
			cmd = '/sbin/shutdown +1 -r'.split()
		try:
			p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(stdout, stderr) = p.communicate();
			status = p.returncode
		except Exception as e:
			status = 999
			stdout = ''
			stderr = str(e)
		return (status, stdout, stderr)


	#Determine our server
	def _get_discovery_server(self, boot_args=None):
		if not boot_args:
			boot_args = self.boot_args
		if 'discovery.server' in boot_args:
			self.discovery_server = boot_args['discovery.server']
		else:
			self.discovery_server = False
		return self.discovery_server

	def _get_location(self):
		if not self.boot_args:
			self._parse_boot_args()
		if 'discovery.location' in self.boot_args:
			self.location = self.boot_args['discovery.location']
		else:
			self.location = 'Unknown'

	def _get_facts(self):
		(status, stdout, stderr) = self._do_action(['facter','-j'])
		if stdout:
			facts = json.loads(stdout)
			if 'serialnumber' not in facts:
				print "No serialnumber found in facts.  Are you running as root?"
				sys.exit(1)
		self.facts = facts


	def post_data(self, data=None):
		if not data:
			if not self.facts:
				self._get_facts
			data = {}
			data['location'] = self.location
			data['serialnumber'] = self.facts['serialnumber']
			data['facts'] = self.facts;
		try:
 			r = requests.post("%s/nodes/%s/discover" % (self.discovery_server, self.facts['serialnumber']), data=json.dumps(data), headers=self.headers,verify=False)
 		except:
 			print "Unable to reach server.."
 			sys.exit(1)
 		try:
 			response = json.loads(r.text)
 		except Exception as e:
			sys.stderr.write("Failed to parse response: %s\n" % e)
			sys.exit(1)

		if response:
			self._handle_server_response(response)
		# With every server send, there is a repsonse back with stuff to do

	def _handle_server_response(self, response):
		if 'actions' in response and response['actions'] != []:
			for action in response['actions']:
				print "Firing action: %s" % action['cmd']
				(status, stdout, stderr) = self._do_action(action['cmd'].split(' '))
				action['status'] = status
				action['stdout'] = stdout
				action['stderr'] = stderr

			self._send_actions_response(response['actions'])

		if 'repositories' in response and response['repositories'] != []:
			self.repos.install_repo(response['repositories'])

	def _send_actions_response(self, actions_dictionary):
		if not self.facts:
			self._get_facts()

		return_data = {'actions': actions_dictionary, 'facts': self.facts,'location': self.location	}
		self.post_data(return_data)

	def is_dhcp_lease_valid(self):
		default_gateway = self._get_default_route()
		if default_gateway == "1.2.3.4":
			return False
		response = os.system("/bin/ping -c 3 -w2 " + default_gateway + " > /dev/null 2>&1")
		if response == 0:
			return True
		else:
			return False

	def renew_dhcp_lease(self):
		"""Renew DHCP lease by restarting the network."""
		response = os.system("/sbin/dhclient -r;/sbin/dhclient")
		if response != 0:
			print "Network restart failed. DHCP Lease failed."


	def _get_default_route(self):
		"""Read the default gateway directly from /proc."""
		with open("/proc/net/route") as fh:
			for line in fh:
				fields = line.strip().split()
				if fields[1] != '00000000' or not int(fields[3], 16) & 2:
					continue
				else:
					return socket.inet_ntoa(struct.pack("=L", int(fields[2], 16)))

			return "1.2.3.4"


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	node = SagaNode()
	print "Running initalization, this may take a while..."
	node.initalize()
	discovery_server = node.discovery_server
	parser.add_argument("-s","--server",help="Discovery server to use",default=discovery_server)
	args = parser.parse_args()
	if args.server:
		discovery_server = args.server

	if not discovery_server:
		print "No discovery server found in boot arguments or program arguments."
		sys.exit(1)
	node.discovery_server = discovery_server

	if not node.is_dhcp_lease_valid():
		node.renew_dhcp_lease()
	node.post_data()
