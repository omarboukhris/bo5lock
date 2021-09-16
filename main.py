#!/home/omar/tf-lab/bin/python3

import base64
import getpass
import sys
import collections

from cryptography.fernet import Fernet
import os.path

import pickle
import pyperclip
import hashlib

""" Class used for parsing arguments
"""
class ArgvLex:

	def __init__(self, argv):
		self.parsedargv = {}
		for arg in argv:
			s = arg.split("=")
			if len(s) == 1:
				self.parsedargv[s[0]] = True
			elif len(s) == 2:
				self.parsedargv[s[0]] = s[1]
			# else :
			# pass

	def get(self, key):
		if key in self.parsedargv.keys():
			return self.parsedargv[key]
		return False

	def dump(self):
		print (self.parsedargv)

class Service :
	def __init__(self, service, label, ticket):
		self.service, self.label, self.ticket = service, label, ticket


""" Class used for IO operations
"""
class IO:
	@staticmethod
	def load_ticket(filename):
		fs = open(filename, "rb")
		result = fs.read()
		fs.close()
		return result

	@staticmethod
	def store_ticket(filename, ticket):
		fs = open(filename, "wb")
		fs.write(ticket)
		fs.close()

	@staticmethod
	def read_file(enc_file: str):
		if os.path.isfile(enc_file):
			fstream = open(enc_file, "rb")
			# number of stored services
			acc_enc = pickle.load(fstream)
			fstream.close()
			return acc_enc
		else:
			return []

	@staticmethod
	def write_file(data: Service, enc_file: str):
		fstream = open(enc_file, "wb")
		pickle.dump(data, fstream)
		fstream.close()


""" Security engine : main class for encryption/decryption
"""
class SecEngine:
	def __init__(self, key_filename=""):
		if key_filename == "":
			self.ticket = Fernet.generate_key()
		else:
			self.ticket = IO.load_ticket(key_filename)
		self.cipher = Fernet(self.ticket)

	def encode(self, data: str):
		# msg = self.cipher.encrypt(b'texttext')
		enc_data = self.cipher.encrypt(SecEngine.bitify(data))
		return enc_data

	def decode(self, data: bytes):
		dec_data = self.cipher.decrypt(data).decode("utf-8")
		return dec_data

	@staticmethod
	def bitify(data: str):
		return data.encode() if type(data) == str else bytes(str(data), "utf-8")
		# return bytes(data, "utf-8") if type(data) == str else bytes(str(data), "utf-8")


""" el king
"""
class Session:

	def __init__(self, p_engine: ArgvLex):
		self.p_engine = p_engine

		self.engine = None

	def get_param(self, label: str, param: str, is_passwd: bool = False):
		if self.p_engine.get(param):
			return self.p_engine.get(param)
		elif not self.p_engine.get("-ui"):  # if not in ui mode, allow interaction
			if is_passwd:
				return getpass.getpass("(mypass_session) enter {} > ".format(label))
			else:
				return input("(mypass_session) enter {} > ".format(label))
		else:
			raise Exception("No {} parameter specified with -ui".format(param))

	def check_service_eq(self, a, c):
		return self.engine.decode(a.service) == self.engine.decode(c.service)

	def check_eq(self, a , c):
		return self.check_service_eq(a, c) and self.engine.decode(a.label) == self.engine.decode(c.label)

	def create(self):
		tik = self.get_param("ticket file path", "-p")
		tik = "{}.tik".format(tik) if tik[-4:] != ".tik" else tik
		self.make_engine(tik)

		enc_file = self.get_param("protected file path", "-f")
		acc = IO.read_file(enc_file)

		service = self.engine.encode(self.get_param("service", "-s"))
		login = self.engine.encode(self.get_param("login", "-l"))
		kw = self.engine.encode(self.get_param("keyword", "-k", True))

		c = Service(service, login, kw)
		new_acc = []
		found = False
		for a in acc:
			if self.check_eq(a, c) and not found:
				print("(info) service/login found")
				found = True
				new_acc.append(c)
			else:
				new_acc.append(a)
		if not found :
			print("(info) service/login not found, user created")
			new_acc.append(c)

		IO.write_file(new_acc, enc_file)
		print("(info) added info to database")

	def list_data(self):
		tik = self.get_param("ticket file path", "-p")
		tik = "{}.tik".format(tik) if tik[-4:] != ".tik" else tik
		self.make_engine(tik)

		enc_file = self.get_param("protected file path", "-f")
		acc = IO.read_file(enc_file)

		ord_dic = collections.OrderedDict()
		print()
		for a in acc:
			kw = self.engine.decode(a.service)
			if not (kw in ord_dic.keys()):
				ord_dic[kw] = [self.engine.decode(a.label)]
			else:
				ord_dic[kw].append(self.engine.decode(a.label))
		for k, l in ord_dic.items():
			print(k)
			for el in l:
				print("\t- {}".format(el))
		print()

	def fetch(self):
		tik = self.get_param("ticket file path", "-p")
		tik = "{}.tik".format(tik) if tik[-4:] != ".tik" else tik
		self.make_engine(tik)

		enc_file = self.get_param("protected file path", "-f")
		acc = IO.read_file(enc_file)

		service = self.engine.encode(self.get_param("service", "-s"))
		login = self.engine.encode(self.get_param("login", "-l"))

		found = False
		c = Service(service, login, self.engine.encode(""))
		for a in acc:
			if self.check_eq(a, c) and not found:
				print("(info) user found, check clipboard")
				pyperclip.copy(self.engine.decode(a.ticket))
				found = True
		if not found:
			print("(info) service/login not found, check credentials")

	def update(self):
		tik = self.get_param("ticket file path", "-p")
		tik = "{}.tik".format(tik) if tik[-4:] != ".tik" else tik
		self.make_engine(tik)

		enc_file = self.get_param("protected file path", "-f")
		acc = IO.read_file(enc_file)

		service = self.engine.encode(self.get_param("service", "-s"))
		login = self.engine.encode(self.get_param("login", "-l"))

		kw = self.engine.encode(self.get_param("keyword", "-k", True))

		c = Service(service, login, kw)
		new_acc = []
		found = False
		for a in acc:
			if self.check_eq(a, c) and not found:
				print("(info) service/login found, user updating")
				found = True
				new_acc.append(c)
			else:
				new_acc.append(a)
		if not found:
			print("(info) service/login not found, user not updated")

		IO.write_file(new_acc, enc_file)
		print("(info) updated info to database")

	def delete(self):
		tik = self.get_param("ticket file path", "-p")
		tik = "{}.tik".format(tik) if tik[-4:] != ".tik" else tik
		self.make_engine(tik)

		enc_file = self.get_param("protected file path", "-f")
		acc = IO.read_file(enc_file)

		service = self.engine.encode(self.get_param("service", "-s"))
		login = self.engine.encode(self.get_param("login", "-l"))

		c = Service(service, login, self.engine.encode(" "))
		new_acc = []
		found = False

		if self.engine.decode(login) == self.engine.decode(self.engine.encode("*")):
			# delete all
			for a in acc:
				if self.check_service_eq(a, c):
					print("(info) service/login found, deleting ...")
					found = True
				else:
					new_acc.append(a)
			if not found:
				print("(info) service/login not found, nothing to delete")

		else:
			for a in acc:
				if self.check_eq(a, c) and not found:
					print("(info) service/login found")
					found = True
				else:
					new_acc.append(a)
			if not found:
				print("(info) service/login not found, nothing to delete")

		IO.write_file(new_acc, enc_file)

	def make_engine(self, tik):
		if os.path.isfile(tik):
			print("(info) > ticket found")
			self.engine = SecEngine(tik)
		else:  # SecEngine generates new ticket, be sure to store it
			print("(info) > ticket not found !")
			self.engine = SecEngine()
			IO.store_ticket(tik, self.engine.ticket)
			print("(info) > generated new ticket, stored in {}".format(tik))

def print_help():
	print("""
{} COMMAND [-f=USER_FILE] [-p=PASS_FILE] [-s=SERVICE] [-l=LOGIN]
COMMAND can be :
	- create
	- fetch 
	- update
	- delete
	- list

The rest of the command's parameters are: 
	-l=LOGIN       :mypasswd app login
	-p=PASSWD_FILE :path to passwd file
	-f=USER_FILE   :where encoded passwds are stored
	-s=SERVICE     :service to retreive passwd for

All parameters are optional. If mandatory parameters are not specified, 
and depending on command, user may be prompted to enter data in terminal 
	""".format(sys.argv[0]))


if __name__ == "__main__":
	# parse args
	try:
		parser = ArgvLex(sys.argv[2:])  # argv[0] is main.py,
		sess = Session(parser)
		if len(sys.argv) > 1:
			cmd = sys.argv[1]
			if cmd == "create":
				sess.create()
			elif cmd == "fetch":
				sess.fetch()
			elif cmd == "update":
				sess.update()
			elif cmd == "delete":
				sess.delete()
			elif cmd == "list":
				sess.list_data()
		else:
			print_help()
	except Exception as e:
		print("An exception has occured : {}".format(e))
