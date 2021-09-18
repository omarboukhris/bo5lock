
import sys
from bo5lock_cmd import ArgvLex, Session, Service

from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QLineEdit
from PyQt6.QtCore import QCoreApplication, QMetaObject

from bo5lock_ui import Ui_bo5lock_widget



class UiBo5lock(QWidget, Ui_bo5lock_widget):
	interpreter  = "python"
	path_to_exec = "bo5lock_cmd.py"

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

		if cmd in ["create", "update", "delete"] and self.kw_lineEdit.text() == "":
			self.status_textEdit.setText(self.tr("ui_bo5lock", "please enter passphrase"))
			return


		if cmd in ["create", "fetch", "update", "delete", "list"]:
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


if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = UiBo5lock()
	ui.show()
	sys.exit(app.exec())


