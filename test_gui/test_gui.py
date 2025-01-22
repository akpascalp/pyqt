import sys
import enum
from typing import Any

# from bson import DBRef
from pathlib import Path
from copy import deepcopy
from bson import ObjectId
from PySide6 import QtWidgets, QtGui
from PySide6 import (
    QtWebEngineWidgets,
)  # noqa F401 : Needs to be loaded before loading UI

from main.lib.misc import utils
from main.lib.database import mainDB
from main.scripts.gui.parent_gui import MainWindow, MainApp
from main.scripts.gui.ui.ui_test_gui import Ui_TestGUI
from main.scripts.gui.test_gui.ask_test_gui import AskTestDialog
from main.scripts.gui.tracks_gui.tracks_gui import TracksViewDialog

from constants.versions import Version


class TEMPLATE_FORMAT(enum.Enum):
    WORD = "Word files (*.docx)"
    PPTX = "Powerpoint files (*.pptx)"


class TestModel:
    def __init__(self, testId: ObjectId) -> None:
        self.testData = mainDB.tests.get(id=testId)[0]
        # for WIDGET_DATABASE_MAPKEYLISTS_MAPPING use, convert testData to full dict
        self.testData["version"] = self.testData["version"].toDict()

    def __str__(self) -> str:
        _testData = deepcopy(self.testData)
        _testData["version"] = Version(
            self.testData["version"]
        )  # convert back to Version object for display
        return f"{_testData['name']} - {_testData['version']}"

    def setData(self, mapList: list[str], value: Any):
        try:
            utils.setInDict(self.testData, mapList, value)
        except TypeError:
            if self.testData is None:
                raise RuntimeError("Test Data not initialized yet.")

    def _to_qt(self, value: Any) -> Any:
        match value:
            # case DBRef():
            #     value = value.id
            case Path():
                value = value.as_posix()
            case list():
                value = [self._to_qt(_) for _ in value]
            case dict():
                value = {
                    self._to_qt(key): self._to_qt(value) for key, value in value.items()
                }

        return value

    def getData(self, mapList: list[str]) -> Any:
        try:
            value = utils.getFromDict(self.testData, mapList)
            value = self._to_qt(value)
        except TypeError:
            if self.testData is None:
                raise RuntimeError("Test Data not initialized yet.")
        return value

    def saveData(self) -> bool:
        updateDict = deepcopy(self.testData)
        for key in ["_id", "lastUpdateDate", "creationDate", "lastUpdateUser"]:
            updateDict.pop(key)
        for key in updateDict:
            if isinstance(updateDict[key], str):
                updateDict[key] = utils.removeWhitespace(updateDict[key])
        updated = mainDB.tests.update(self.testData["_id"], updateDict)
        return updated

    def refresh(self):
        if (testId := self.testData.get("_id")) is not None:
            # mainDB._clearCache()  # TODO
            self.testData = mainDB.tests.get(id=testId)[0]


class TestWindow(Ui_TestGUI, MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Load frontend
        self.setupUi(self)
        self.initWindowTitle()

        self.IS_READ_ONLY = mainDB.IS_READ_ONLY
        self.WIDGET_DATABASE_MAPKEYLISTS_MAPPING = {
            self.testNameLE: ["name"],
            self.objectTypeCoB: ["objectType"],
            self.versionMajorSB: ["version", "major"],
            self.versionMinorSB: ["version", "minor"],
            self.isActiveChB: ["active"],
            self.testCommentTE: ["comment"],
            self.reportTemplatesListWidget: ["reportFilePathList"],
            self.debriefTemplatesListWidget: ["debriefFilePathList"],
        }

        self.initWidgets()

        self.testModel: TestModel = None
        self.initTest()

        # add test menu
        self.testMenu = QtWidgets.QMenu(self.menubar)
        self.testMenu.setObjectName(("Test"))
        self.testMenu.setTitle("Test")
        self.menubar.addAction(self.testMenu.menuAction())

        # Add menu action for test change
        self.loadTestAction = QtGui.QAction("Load Test...")
        self.loadTestAction.setShortcut("Ctrl+L")
        self.loadTestAction.triggered.connect(self.on_selectTest)
        self.testMenu.addAction(self.loadTestAction)

        if self.IS_READ_ONLY:
            self.actionTracksGUI.setDisabled(True)
        self.actionTracksGUI.triggered.connect(self.on_actionTracksGUITriggered)

    # ------------------------------ INIT ------------------------------ #

    def initWidgets(self):
        for objectType in mainDB.objects.OBJECT_TYPE_LIST:
            self.objectTypeCoB.addItem(objectType, objectType)

        for widget in [
            self.testNameLE,
            self.objectTypeCoB,
            self.versionMajorSB,
            self.versionMinorSB,
            self.savePB,
            self.cancelPB,
            self.testCommentTE,
            self.reportTemplatesListWidget,
            self.addReportTemplatePB,
            self.removeReportTemplatePB,
            self.debriefTemplatesListWidget,
            self.addDebriefTemplatePB,
            self.removeDebriefTemplatePB,
            self.isActiveChB,
        ]:
            widget.setDisabled(True)

        for widget, dbKey in self.WIDGET_DATABASE_MAPKEYLISTS_MAPPING.items():
            match widget:
                case QtWidgets.QLineEdit():
                    widget.editingFinished.connect(
                        self._getGenericCallBack(widget, dbKey)
                    )
                case QtWidgets.QComboBox():
                    widget.currentTextChanged.connect(
                        self._getGenericCallBack(widget, dbKey)
                    )
                case QtWidgets.QSpinBox():
                    widget.valueChanged.connect(self._getGenericCallBack(widget, dbKey))
                case QtWidgets.QTextEdit():
                    widget.textChanged.connect(self._getGenericCallBack(widget, dbKey))
                case QtWidgets.QListWidget():
                    pass  # No signal for data changes, will be handle manually with buttons
                case QtWidgets.QCheckBox():
                    widget.stateChanged.connect(self._getGenericCallBack(widget, dbKey))
                case _:
                    raise NotImplementedError

        if not self.IS_READ_ONLY:
            self.editPB.clicked.connect(self.on_editPBClicked)
            self.savePB.clicked.connect(self.on_savePBClicked)
            self.cancelPB.clicked.connect(self.on_cancelPBClicked)
            self.reportTemplatesListWidget.itemSelectionChanged.connect(
                self.on_reportTemplatesSelectionChanged
            )
            self.debriefTemplatesListWidget.itemSelectionChanged.connect(
                self.on_debriefTemplatesSelectionChanged
            )
            self.addReportTemplatePB.clicked.connect(self.on_addReportTemplatePBClicked)
            self.removeReportTemplatePB.clicked.connect(
                self.on_removeReportTemplatePBClicked
            )
            self.addDebriefTemplatePB.clicked.connect(
                self.on_addDebriefTemplatePBClicked
            )
            self.removeDebriefTemplatePB.clicked.connect(
                self.on_removeDebriefTemplatePBClicked
            )
        else:
            for widget in [
                self.editPB,
                self.savePB,
                self.cancelPB,
                self.addReportTemplatePB,
                self.removeReportTemplatePB,
                self.addDebriefTemplatePB,
                self.removeDebriefTemplatePB,
            ]:
                widget.hide()

    def on_selectTest(self):
        testId = self.initTest()
        self.scoreTestViewer.loadTest(testId)

    def initTest(self):
        askTestDialog = AskTestDialog(self)
        if askTestDialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            testId = askTestDialog.selectedTestId
            self.testModel = TestModel(testId)

            self.testLabel.setText(str(self.testModel))
            self.refresh()

            # init all other tabs data
            self.scoreTestViewer.loadTest(testId)
            self.descriptionEditorWidget.init_gui(testId)
            self.winsDescriptionEditor.setTestId(testId)
        else:
            # if cancelled we reuse the previous test used (which happens to be stored in ScoreTestViewer)
            try:
                testId = self.scoreTestViewer.testId
            except AttributeError:  # if no test, we just exit
                raise SystemExit(1)
        return testId

    # ------------------------------ CALLBACKS ------------------------------ #

    def _getGenericCallBack(self, widget: QtWidgets.QWidget, mapKeyList: list[str]):
        def _genericCallback():
            match widget:
                case QtWidgets.QLineEdit():
                    value = utils.removeWhitespace(widget.text())
                case QtWidgets.QComboBox():
                    value = widget.currentData()
                case QtWidgets.QSpinBox():
                    value = widget.value()
                case QtWidgets.QTextEdit():
                    value = widget.toPlainText() if widget.toPlainText() != "" else None
                case QtWidgets.QListWidget():
                    pass  # No signal for data changes, will be handle manually with buttons
                case QtWidgets.QCheckBox():
                    value = widget.isChecked()
                case _:
                    raise NotImplementedError
            self.testModel.setData(mapKeyList, value)

        return _genericCallback

    def on_editPBClicked(self):
        self.enableWidgets(True)
        self.savePB.setEnabled(True)
        self.cancelPB.setEnabled(True)
        self.editPB.setEnabled(False)

    def on_cancelPBClicked(self):
        self.enableWidgets(False)
        self.testModel.refresh()
        self.refresh()
        self.savePB.setEnabled(False)
        self.cancelPB.setEnabled(False)
        self.editPB.setEnabled(True)

    def on_savePBClicked(self):
        saved = self.testModel.saveData()
        if saved:
            self.enableWidgets(False)
            self.savePB.setEnabled(False)
            self.cancelPB.setEnabled(False)
            self.editPB.setEnabled(True)
        else:
            QtWidgets.QMessageBox.warning(
                self, "Failed", "Test Info not saved. Please check log."
            )

    def on_reportTemplatesSelectionChanged(self):
        self.removeReportTemplatePB.setEnabled(
            len(self.reportTemplatesListWidget.selectedItems()) > 0
        )

    def on_debriefTemplatesSelectionChanged(self):
        self.removeDebriefTemplatePB.setEnabled(
            len(self.debriefTemplatesListWidget.selectedItems()) > 0
        )

    def on_actionTracksGUITriggered(self):
        trackView = TracksViewDialog()
        trackView.exec()

    def on_addReportTemplatePBClicked(self):
        self.addFilePathTemplate("Report", TEMPLATE_FORMAT.WORD, ["reportFilePathList"])
        self.refresh()

    def on_removeReportTemplatePBClicked(self):
        if len(selectedItems := self.reportTemplatesListWidget.selectedItems()) > 0:
            selectedItem = selectedItems[0]
            self.removeFilePathTemplate(selectedItem.text(), ["reportFilePathList"])
            self.refresh()

    def on_addDebriefTemplatePBClicked(self):
        self.addFilePathTemplate(
            "Debrief", TEMPLATE_FORMAT.PPTX, ["debriefFilePathList"]
        )
        self.refresh()

    def on_removeDebriefTemplatePBClicked(self):
        if len(selectedItems := self.debriefTemplatesListWidget.selectedItems()) > 0:
            selectedItem = selectedItems[0]
            self.removeFilePathTemplate(selectedItem.text(), ["debriefFilePathList"])
            self.refresh()

    # ------------------------------ UPDATE ------------------------------ #
    def refresh(self):
        for widget, keyMap in self.WIDGET_DATABASE_MAPKEYLISTS_MAPPING.items():
            value = self.testModel.getData(keyMap)
            match widget:
                case QtWidgets.QLineEdit() | QtWidgets.QTextEdit():
                    widget.setText(value if value is not None else "")
                case QtWidgets.QComboBox():
                    for index in range(
                        widget.count()
                    ):  # findData method not working...
                        if widget.itemText(index) == value:
                            widget.setCurrentIndex(index)
                            widget.setCurrentText(value)
                            break
                case QtWidgets.QSpinBox():
                    if value:
                        widget.setValue(value)
                case QtWidgets.QListWidget():
                    widget.clear()
                    if value:
                        widget.addItems(value)
                case QtWidgets.QCheckBox():
                    widget.setChecked(value)
                case _:
                    raise NotImplementedError

    def enableWidgets(self, enable: bool = True):
        for widget in [
            self.testNameLE,
            self.objectTypeCoB,
            self.versionMajorSB,
            self.versionMinorSB,
            self.testCommentTE,
            self.reportTemplatesListWidget,
            self.debriefTemplatesListWidget,
            self.addReportTemplatePB,
            self.addDebriefTemplatePB,
            self.isActiveChB,
        ]:
            widget.setEnabled(enable)

    def addFilePathTemplate(
        self, category: str, docType: TEMPLATE_FORMAT, dbKeyMap: list[str]
    ):
        _filepath = QtWidgets.QFileDialog.getOpenFileName(
            self, f"Choose {category} Template", "C:\\", docType.value
        )
        if _filepath:
            try:
                filepath = Path(_filepath[0]).relative_to(Path.cwd()).as_posix()
            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self, "Failed", f"Template must be in {Path.cwd()} folder."
                )
            else:
                oldFilePathList = self.testModel.getData(dbKeyMap)
                if oldFilePathList is None:
                    oldFilePathList = []
                self.testModel.setData(dbKeyMap, oldFilePathList + [filepath])

    def removeFilePathTemplate(self, value: str, dbKeyMap: list[str]):
        oldFilePathList = self.testModel.getData(dbKeyMap)
        newFilePathList = [_ for _ in oldFilePathList if _ != value]
        self.testModel.setData(dbKeyMap, newFilePathList)


if __name__ == "__main__":
    app = MainApp()
    window = TestWindow()
    window.showNormal()
    sys.exit(app.exec())
