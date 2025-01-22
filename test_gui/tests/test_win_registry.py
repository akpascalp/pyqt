from __future__ import annotations

import pytest
from unittest import mock
from random import randint, seed
from pytest_mock import MockerFixture

from main.scripts.gui.test_gui.wins_tab_widget import InvalidWinError, SynchronizeError
from main.scripts.gui.test_gui.wins_tab_widget import WinRegistry, DuplicateError
from main.lib.database import mainDB
from fake_db import patchDB
from constants.versions import Version

OBJECT_TYPES = mainDB.objects.OBJECT_TYPE_LIST
seed(0)
Type = OBJECT_TYPES[randint(0, len(OBJECT_TYPES) - 1)]


@mock.patch("main.lib.database.mainDB.tests.get")
@mock.patch("main.lib.database.mainDB.windescriptions.get")
def test_winRegistryEmpty(mock_windescriptions_get, mock_tests_get):
    registry = WinRegistry()

    assert registry.getDbWins() == {}
    assert registry.getAddedWinsCodes() == []
    assert registry.getDeletedWinsCodes() == []
    assert registry.getUpdatedWinsCodes() == []

    assert registry.needSave() is False


@mock.patch("main.lib.database.mainDB.tests.get")
@mock.patch("main.lib.database.mainDB.windescriptions.get")
def test_winRegistryAddWin(mock_windescriptions_get, mock_tests_get):
    registry = WinRegistry()

    outputPath = ("xxx", "yyy", "Pros")
    win = registry.createWin(outputPath)

    assert win.isUsedInMultipletests is False

    assert registry.isWinNew(win) is True
    assert registry.isWinUpdated(win) is False
    assert registry.isWinToDelete(win) is False

    assert registry.getAddedWinsCodes() == [outputPath]
    assert registry.getDeletedWinsCodes() == []
    assert registry.getUpdatedWinsCodes() == []

    assert registry.needSave() is True


@mock.patch("main.lib.database.mainDB.tests.get")
@mock.patch("main.lib.database.mainDB.windescriptions.get")
def test_winRegistrySavetestWinsUnregistered(mock_windescriptions_get, mock_tests_get):
    tests = [("test", Type, Version(1, 0), [])]

    winDescriptions, tests = patchDB([], tests)
    testId = tests[0]["_id"]
    mock_windescriptions_get.return_value = winDescriptions
    mock_tests_get.return_value = tests

    registry = WinRegistry()

    test = registry.gettest(testId)

    assert registry.gettestWins(test) == []
    assert registry.gettestWinsCodes(test) == []

    with pytest.raises(InvalidWinError):
        registry.savetestWins(registry.gettest(testId), [win])

    assert registry.gettestWins(test) == []
    assert registry.gettestWinsCodes(test) == []
