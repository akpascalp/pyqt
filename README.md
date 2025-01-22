# Test GUI

This project is a graphical user interface for managing tests. It uses PySide6 for the user interface and interacts with a database for test data management.

## Project Structure

### Main Files

- [`test_gui/test_gui.py`](test_gui/test_gui.py): Contains the main logic for the user interface for managing tests.
- [`test_gui/ask_test_gui.py`](test_gui/ask_test_gui.py): Contains the logic for the dialog box to select, duplicate, or create a new test.
- [`ui/test_gui.ui`](ui/test_gui.ui): XML file defining the layout of the user interface.

### Tests

The tests are located in the [`tests`](test_gui/tests/fake_db.py) directory and use [`pytest`](test_gui/tests/test_win_registry.py) for unit testing.

- [`test_gui/tests/test_win_registry.py`](test_gui/tests/test_win_registry.py): Tests for window registry management.
- [`test_gui/tests/test_models.py`](test_gui/tests/test_models.py): Tests for the data models used in the user interface.
- [`test_gui/tests/fake_db.py`](test_gui/tests/fake_db.py): Contains utility functions to simulate a database for testing.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd test_gui
    ```

2. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the [test_gui.py](http://_vscodecontentref_/1) file:
```sh
python test_gui.py
```

## Tests

To run the tests, use `pytest`:
```sh
pytest
```
