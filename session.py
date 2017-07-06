# -*- coding: utf-8 -*-
#
#       Copyright 2016 Ahmed Nazmy
#

# Meta
__license__ = "AGPLv3"
__author__ = 'Ahmed Nazmy <ahmed@nazmy.io>'

import logging
import getpass
from SSHClient import SSHClient


class Session(object):
	""" 
	Base Session class 
	"""

	def __init__(self,aker_core,host,port,uuid):
		self.aker= aker_core
		self.host = host
		self.host_user = self.aker.user.name
		self.host_port = int(port)
		self.src_port = self.aker.config.src_port
		self.uuid = uuid
		logging.debug("Session: Base Session created")

		
	def attach_sniffer(self,sniffer):
		self._client.attach_sniffer(sniffer)
	
	def stop_sniffer(self):
		self._client.stop_sniffer()

	def connect(self, size):
		self._client.connect(self.host, self.host_port, size)

	def start_session(self):
		raise NotImplementedError
		
	def close_session(self):
		self.aker.session_end_callback(self)
		
	def kill_session(self, signum, stack):
		logging.debug("Session: Session ended")
		self.close_session()


class SSHSession(Session):
	""" Wrapper around SSHClient instantiating 
		a new SSHClient instance every time
	"""
	
	def __init__(self, aker_core, host, port, uuid):
		super(SSHSession, self).__init__(aker_core, host, port, uuid)
		self._client = SSHClient(self)
		logging.debug("Session: SSHSession created")

		
	def start_session(self):
		try:
			auth_secret = self.aker.user.get_priv_key()
		# currently, if no SSH public key exists, an ``Exception``
		# is raised.  Catch it and try a password.
		except Exception as exc:
			if str(exc) == 'Core: Invalid Private Key':
				auth_secret = getpass.getpass("Password: ")
			else:
				raise
		self._client.start_session(self.host_user, auth_secret)
