import collections
import sys

from bo5lock_cmd import ArgvLex, Session, Service, IO

from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6.QtCore import QCoreApplication, QMetaObject

from bo5lock_ui import Ui_bo5lock_widget



class UiBo5lock(QWidget, Ui_bo5lock_widget):

	def __init__(self):
		super(UiBo5lock, self).__init__()
		self.setupUi(self)

		self._tr = QCoreApplication.translate
		self.loaded_wallet = collections.OrderedDict()

		self.wallet = ""
		while self.wallet == "":
			self.wallet = QFileDialog.getSaveFileName(
				self, self._tr("ui_bo5lock", "Open Wallet"),
				".", self._tr("ui_bo5lock", "Wallet file (*.wlt)"),
				options=QFileDialog.Option.DontConfirmOverwrite)[0]

		self.ticket = ""
		while self.ticket == "":
			self.ticket = QFileDialog.getSaveFileName(
				self, self._tr("ui_bo5lock", "Open Ticket"),
				".", self._tr("ui_bo5lock", "Ticket file (*.tik)"),
				options=QFileDialog.Option.DontConfirmOverwrite)[0]

		self.load_wlt()
		self.update_service(0)

		self.apply_pushButton.clicked.connect(self.apply_clicked)
		self.cmd_comboBox.currentTextChanged.connect(self.cmd_changed)

		self.service_comboBox.currentIndexChanged.connect(self.update_service)

		QMetaObject.connectSlotsByName(self)

		self.setFixedSize(
			self.frameGeometry().width(),
			self.frameGeometry().height())

	def cmd_changed(self):
		if self.cmd_comboBox.currentText() in ["create", "update", "delete"]:
			self.kw_lineEdit.setEnabled(True)
		else:
			self.kw_lineEdit.setDisabled(True)

	def update_service(self, index):
		if len(list(self.loaded_wallet.values())) == 0:
			return  # break function, no element to display
		value_at_index = list(self.loaded_wallet.values())[index]

		self.label_comboBox.clear()
		c = 0
		for i in value_at_index:
			self.label_comboBox.addItem("")
			self.label_comboBox.setItemText(c, self._tr("ui_bo5lock", i))
			c += 1

	def load_wlt(self):
		argv = [
			"-f={}".format(self.wallet),
			"-p={}".format(self.ticket),
			"-ui"
		]
		sys_out = []
		parser = ArgvLex(argv)
		sess = Session(
			parser,
			fetch_callback=(lambda x: x),
			log_out=sys_out.append)
		self.loaded_wallet = sess.list_data()

		self.service_comboBox.clear()
		i = 0
		for k in self.loaded_wallet.keys():
			self.service_comboBox.addItem("")
			self.service_comboBox.setItemText(i, self._tr("ui_bo5lock", k))
			i += 1

	def apply_clicked(self):
		cmd = self.cmd_comboBox.currentText()
		if cmd in ["create", "fetch", "update", "delete"]:
			if self.service_comboBox.currentText() == "":
				self.status_textEdit.setText(self._tr("ui_bo5lock", "please setup service"))
				return
			if self.label_comboBox.currentText() == "":
				self.status_textEdit.setText(self._tr("ui_bo5lock", "please setup login"))
				return

		if cmd in ["create", "update", "delete"] and self.kw_lineEdit.text() == "":
			self.status_textEdit.setText(self._tr("ui_bo5lock", "please enter passphrase"))
			return

		if cmd in ["create", "fetch", "update", "delete"]:
			argv = [
				"-f={}".format(self.wallet),
				"-p={}".format(self.ticket),
				"-s={}".format(self.service_comboBox.currentText()),
				"-l={}".format(self.label_comboBox.currentText()),
				"-k={}".format(self.kw_lineEdit.text()),
				"-ui"
			]
			sys_out = []
			parser = ArgvLex(argv)
			sess = Session(parser, fetch_callback=QApplication.clipboard().setText, log_out=sys_out.append)
			sess.run(cmd)
			ss_out = "\n".join(sys_out)
			self.status_textEdit.setText(ss_out)

		self.load_wlt()
		self.update_service(self.service_comboBox.currentIndex())



if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = UiBo5lock()
	ui.show()
	sys.exit(app.exec())


