from unittest import mock
from random import randint, seed
from main.lib.database import mainDB
from main.scripts.gui.test_gui.wins_tab_widget import AllWinsItemModel
from main.scripts.gui.test_gui.wins_tab_widget import WinRegistry, TestWinsItemModel
from fake_db import patchDB
from utils import generateRandomCode
from constants.versions import Version

OBJECT_TYPES = mainDB.objects.OBJECT_TYPE_LIST
seed(0)


@mock.patch("main.lib.database.mainDB.tests.get")
@mock.patch("main.lib.database.mainDB.windescriptions.get")
def test_allWinsItemModelEmptyDb(mock_windescriptions_get, mock_tests_get, qtmodeltester):
    model = AllWinsItemModel(WinRegistry())
    qtmodeltester.check(model, force_py=True)


@mock.patch("main.lib.database.mainDB.tests.get")
@mock.patch("main.lib.database.mainDB.windescriptions.get")
def test_allWinsItemModel(mock_windescriptions_get, mock_tests_get, qtmodeltester):
    winDescriptions, tests = patchDB(generateRandomCode(20), [])
    mock_windescriptions_get.return_value = winDescriptions
    mock_tests_get.return_value = tests

    model = AllWinsItemModel(WinRegistry())
    qtmodeltester.check(model, force_py=True)


@mock.patch("main.lib.database.mainDB.tests.get")
@mock.patch("main.lib.database.mainDB.windescriptions.get")
def test_testWinsItemModel(mock_windescriptions_get, mock_tests_get, qtmodeltester):
    winsData = generateRandomCode(20)
    tests = [
        ("Test", OBJECT_TYPES[randint(0, len(OBJECT_TYPES) - 1)], Version(1, 0), list(range(len(winsData)))[::2])
    ]

    winDescriptions, tests = patchDB(winsData, tests)
    mock_windescriptions_get.return_value = winDescriptions
    mock_tests_get.return_value = tests

    model = TestWinsItemModel(tests[0]["_id"], WinRegistry())

    qtmodeltester.check(model, force_py=True)
