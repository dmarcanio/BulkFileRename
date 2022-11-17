# -*- coding: utf-8 -*-
# BulkFileRename/rename.py

"""This module provides the Renamer class to rename multiple files via pathlib.rename()
   and emits custom signals to communicate with the main thread and update the GUI.
   """

import time
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal

class Renamer(QObject):
    # Define custom signals
    # .progressed() will emit every time the class renames a new file.
    # Returns integer representing number of currently renamed file, for progress bar.
    progressed = pyqtSignal(int)
    # Emit signal when file is renamed. Returns path to the renamed file.
    # Used to update the list of renamed files in the GUI.
    renamedFile = pyqtSignal(Path)
    finished = pyqtSignal()  # emit signal when file renaming is completed.

    def __init__(self, files, prefix):
        super().__init__()
        self._files = files
        self._prefix = prefix

    def renameFiles(self):
        for fileNumber, file in enumerate(self._files, 1)  # starting increment 1
            newFile = file.parent.joinpath(
                f"{self._prefix}{str(filenumber)}{file.suffix}"
            )
            file.rename(newFile)
            time.sleep(0.1)  # slow down renaming to visualize how the process executes.
            self.progressed.emit(fileNumber)
            self.renamedFile.emit(newFile)
        self.progressed.emit(0)  # Reset the progress.
        self.finished.emit()