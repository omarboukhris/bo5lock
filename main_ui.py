
import sys, os

from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QLineEdit
from PyQt6.QtCore import QCoreApplication, QMetaObject

from bo5lock_ui import Ui_bo5lock_widget
import threading

class UiBo5lock(QWidget, Ui_bo5lock_widget):
	interpreter  = "python"
	path_to_exec = "main.py"

	def __init__(self):
		super(UiBo5lock, self).__init__()
		self.setupUi(self)

		self._tr = QCoreApplication.translate

		self.wallet = QFileDialog.getSaveFileName(
			self, self._tr("ui_bo5lock", "Open Wallet"),
			".", self._tr("ui_bo5lock", "Wallet file (*.wlt)"),
			options=QFileDialog.Option.DontConfirmOverwrite)[0]
		self.ticket = QFileDialog.getSaveFileName(
			self, self._tr("ui_bo5lock", "Open Ticket"),
			".", self._tr("ui_bo5lock", "Ticket file (*.tik)"),
			options=QFileDialog.Option.DontConfirmOverwrite)[0]

		self.apply_pushButton.clicked.connect(self.apply_clicked)
		self.cmd_comboBox.currentTextChanged.connect(self.cmd_changed)

		QMetaObject.connectSlotsByName(self)

		self.setFixedSize(
			self.frameGeometry().width(),
			self.frameGeometry().height())

	def cmd_changed(self):
		if self.cmd_comboBox.currentText() in ["create", "update"]:
			self.kw_lineEdit.setEnabled(True)
		else:
			self.kw_lineEdit.setDisabled(True)

	def apply_clicked(self):
		cmd = self.cmd_comboBox.currentText()
		if cmd in ["create", "fetch", "update", "delete"]:
			if self.service_comboBox.currentText() == "":
				self.status_textEdit.setText(self._tr("ui_bo5lock", "please setup service"))
				return
			if self.label_comboBox.currentText() == "":
				self.status_textEdit.setText(self._tr("ui_bo5lock", "please setup login"))
				return

		if cmd in ["create", "update"] and self.kw_lineEdit.text() == "":
			self.status_textEdit.setText(self.tr("ui_bo5lock", "please enter passphrase"))
			return


		if cmd in ["create", "fetch", "update", "delete", "list"]:
			full_cmd = "{interp} {main_file} {cmd} -f={p1} -p={p2} -s={p3} -l={p4} -k={p5} -ui".format(
				interp=UiBo5lock.interpreter,
				main_file=UiBo5lock.path_to_exec,
				cmd=cmd, p1=self.wallet, p2=self.ticket,
				p3=self.service_comboBox.currentText(),
				p4=self.label_comboBox.currentText(),
				p5=self.kw_lineEdit.text()
			)
			# print(full_cmd)
			if cmd == "fetch":
				os.system(full_cmd)
			else:
				pipe = os.popen(full_cmd, "r")
				all_text = "".join(pipe.readlines())
				pipe.close()
				self.status_textEdit.setText(all_text)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = UiBo5lock()
	ui.show()
	sys.exit(app.exec())


