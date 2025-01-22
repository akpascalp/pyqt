import logging
import typing
from PySide6 import QtWidgets, QtCore

from main.lib.database import mainDB

from constants.versions import Version
from configs import gui_config


class AskTestDialog(QtWidgets.QDialog):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget]) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle("Test GUI")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowContextHelpButtonHint | QtCore.Qt.WindowStaysOnTopHint)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.IS_READ_ONLY = mainDB.IS_READ_ONLY

        self.mainLayout.addWidget(QtWidgets.QLabel("Select a test:"))
        self.testCoB = QtWidgets.QComboBox(self)
        for testDict in mainDB.tests.getOrderedList(gui_config.MOST_USED_TEST):
            self.testCoB.addItem(f"{testDict['name']} - {testDict['version']}", testDict["_id"])
        self.mainLayout.addWidget(self.testCoB)

        self.selectPB = QtWidgets.QPushButton(text="Select")
        self.selectPB.clicked.connect(self.on_selectPBClicked)
        self.mainLayout.addWidget(self.selectPB)

        self.duplicatePB = QtWidgets.QPushButton(text="Duplicate")
        self.duplicatePB.clicked.connect(self.on_duplicatePBClicked)
        self.mainLayout.addWidget(self.duplicatePB)

        self.createPB = QtWidgets.QPushButton(text="Create New")
        self.createPB.clicked.connect(self.on_createPBClicked)
        self.mainLayout.addWidget(self.createPB)

        self.selectedTestId = None

        if self.IS_READ_ONLY:
            self.createPB.setDisabled(True)
            self.duplicatePB.setDisabled(True)

    # ------------------------------ CALLBACKS ------------------------------ #
    def on_duplicatePBClicked(self):
        selectedTestId = self.testCoB.currentData(QtCore.Qt.ItemDataRole.UserRole)
        test = mainDB.tests.get(
            id=selectedTestId, projection={"objectType": True, "name": True, "version": True})[0]
        userResponse = QtWidgets.QMessageBox.question(
            self,
            "Duplicate Test",
            f"Create a new test duplicated from {test} ?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if userResponse == QtWidgets.QMessageBox.Yes:
            self.selectedTestId = mainDB.tests.duplicateFrom(testId=selectedTestId)
            self.accept()

    def on_selectPBClicked(self):
        self.selectedTestId = self.testCoB.currentData(QtCore.Qt.ItemDataRole.UserRole)
        self.accept()

    def on_createPBClicked(self):
        objectTypes = mainDB.objects.OBJECT_TYPE_LIST
        objectType, ok = QtWidgets.QInputDialog.getItem(
            self, "Select object type", "Object type:", objectTypes, 0, False
        )
        if ok:
            testName, ok = QtWidgets.QInputDialog.getText(self, "Enter Test Name", "Test Name:")
            if ok:
                while True:
                    version, ok = QtWidgets.QInputDialog.getText(self, "Enter Version", "Version: (ex: 1.0)")
                    if ok:
                        try:
                            versionMajor, versionMinor = map(int, version.split("."))
                            break
                        except ValueError:
                            logging.error("Please enter a valid version (e.g., 1.0)")

                existingTest = mainDB.tests.get(name=testName, version=Version(versionMajor, versionMinor))
                if existingTest:
                    logging.error("A test with same name and version already exists")
                else:
                    self.selectedTestId = mainDB.tests.create(
                        objectType=objectType,
                        name=testName,
                        version=Version(versionMajor, versionMinor),
                        stageDescriptionIdList=[],
                        winDescriptionIdList=[],
                        scoreDescriptionIdList=[],
                    )
                    self.accept()
