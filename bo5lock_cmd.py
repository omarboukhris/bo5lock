#!/home/omar/tf-lab/bin/python3

import getpass
import sys
import collections

from cryptography.fernet import Fernet
import os.path

import pickle

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
	def write_file(data: list, enc_file: str):
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

	def __init__(self, p_engine: ArgvLex, fetch_callback=callable, log_out: callable = print):
		self.p_engine = p_engine

		self.fetch_callback = fetch_callback
		self.log_out = log_out

		self.engine = None

	def run(self, cmd):
		if cmd == "create":
			self.create()
		elif cmd == "fetch":
			self.fetch()
		elif cmd == "update":
			self.update()
		elif cmd == "delete":
			self.delete()
		elif cmd == "list":
			self.list_data()

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

	def check_eq(self, a, c):
		return self.check_service_eq(a, c) and self.engine.decode(a.label) == self.engine.decode(c.label)

	def get_input(self, cmd):
		service, login, kw = None, None, None
		if cmd in ["create", "fetch", "update", "delete"]:
			service = self.engine.encode(self.get_param("service", "-s"))
			login = self.engine.encode(self.get_param("login", "-l"))
		if cmd in ["create", "update", "delete"]:
			kw = self.engine.encode(self.get_param("keyword", "-k", True))
		return service, login, kw

	def get_input_files(self):
		tik = self.get_param("ticket file path", "-p")
		tik = "{}.tik".format(tik) if tik[-4:] != ".tik" else tik
		self.make_engine(tik)

		enc_file = self.get_param("protected file path", "-f")
		acc = IO.read_file(enc_file)

		return tik, enc_file, acc

	def create(self):
		_, enc_file, acc = self.get_input_files()
		service, login, kw = self.get_input("create")

		c = Service(service, login, kw)
		new_acc = []
		found = False
		for a in acc:
			if self.check_eq(a, c) and not found:
				self.log_out("(info) service/login found")
				found = True
				new_acc.append(c)
			else:
				new_acc.append(a)
		if not found :
			self.log_out("(info) service/login not found, user created")
			new_acc.append(c)

		IO.write_file(new_acc, enc_file)
		self.log_out("(info) added info to database")

	def list_data(self):
		_, _, acc = self.get_input_files()

		ord_dic = collections.OrderedDict()
		for a in acc:
			kw = self.engine.decode(a.service)
			if not (kw in ord_dic.keys()):
				ord_dic[kw] = [self.engine.decode(a.label)]
			else:
				ord_dic[kw].append(self.engine.decode(a.label))
		for k, l in ord_dic.items():
			self.log_out(k)
			for el in l:
				self.log_out("\t- {}".format(el))
		return ord_dic

	def fetch(self):
		_, _, acc = self.get_input_files()
		service, login, _ = self.get_input("fetch")

		found = False
		c = Service(service, login, self.engine.encode(""))
		for a in acc:
			if self.check_eq(a, c) and not found:
				self.log_out("(info) user found, check clipboard")
				self.fetch_callback(self.engine.decode(a.ticket))
				found = True
		if not found:
			self.log_out("(info) service/login not found, check credentials")

	def update(self):
		_, enc_file, acc = self.get_input_files()
		service, login, kw = self.get_input("update")

		c = Service(service, login, kw)
		new_acc = []
		found = False
		for a in acc:
			if self.check_eq(a, c) and not found:
				self.log_out("(info) service/login found, user updating")
				found = True
				new_acc.append(c)
			else:
				new_acc.append(a)
		if not found:
			self.log_out("(info) service/login not found, user not updated")

		IO.write_file(new_acc, enc_file)
		self.log_out("(info) updated info to database")

	def delete(self):
		_, enc_file, acc = self.get_input_files()
		service, login, kw = self.get_input("delete")

		c = Service(service, login, kw)
		new_acc = []
		found = False

		if self.engine.decode(login) == self.engine.decode(self.engine.encode("*")):
			# delete all
			for a in acc:
				if self.check_service_eq(a, c) :
					self.log_out("(info) service/login found, deleting ...")
					found = True
				else:
					new_acc.append(a)
			if not found:
				self.log_out("(info) service/login not found, nothing to delete")

		else:
			for a in acc:
				if self.check_eq(a, c) and not found and \
					self.engine.decode(a.ticket) == self.engine.decode(c.ticket):
					self.log_out("(info) service/login found, deleting")
					found = True
				else:
					new_acc.append(a)
			if not found:
				self.log_out("(info) service/login not found or incorrect key, nothing to delete")

		IO.write_file(new_acc, enc_file)

	def make_engine(self, tik):
		if os.path.isfile(tik):
			self.log_out("(info) > ticket found")
			self.engine = SecEngine(tik)
		else:  # SecEngine generates new ticket, be sure to store it
			self.log_out("(info) > ticket not found !")
			self.engine = SecEngine()
			IO.store_ticket(tik, self.engine.ticket)
			self.log_out("(info) > generated new ticket, stored in {}".format(tik))

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
		import pyperclip
		parser = ArgvLex(sys.argv[2:])  # argv[0] is main.py,
		sess = Session(parser, fetch_callback=pyperclip.copy, log_out=print)
		if len(sys.argv) > 1:
			sess.run(sys.argv[1])
		else:
			print_help()
	except Exception as e:
		print("An exception has occured : {}".format(e))
