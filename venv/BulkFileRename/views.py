# -*- coding: utf-8 -*-
# rprename/views.py

"""This module provides the BulkFileRename main window."""

# Deques are a generalization of stacks and queues to support
# efficient append and pop operations from either side of deque.
from collections import deque
from pathlib import Path

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog, QWidget

from .rename import Renamer  # import Renamer class from root/rename.py
from .ui.window import Ui_Window  # import from ui/window.py

FILTERS = ";;".join(
    (
        "All Files (*)",
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "Text Files (*.png)",
        "Python Files (*.py)",
        "PDF Files (*.pdf)"
    )
)


class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()
        self._files = deque()  # deque object to store paths to files user will rename.
        self._filesCount = len(self._files)  # number of files to be renamed.
        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        self.setupUi(self)
        self._updateStateWhenNoFiles()

    def _updateStateWhenNoFiles(self):
        self._filesCount = len(self._files)
        self.loadFilesButton.setEnabled(True)
        self.loadFilesButton.setFocus(True)
        self.renameFilesButton.setEnabled(False)
        self.prefixEdit.clear()
        self.prefixEdit.setEnabled(False)

    def _connectSignalsSlots(self):
        """Collect several signal and slot connections in a single place.
           Connects the Load Files button's .clicked signal with .loadFiles() slot
           This makes it possible to trigger .loadFiles() every time user click the button.
           """
        self.loadFilesButton.clicked.connect(self.loadFiles)
        self.renameFilesButton.clicked.connect(self.renameFiles)

    def loadFiles(self):
        """ Load the files to be renamed. """
        self.dstFileList.clear()  # Clear the file list on button click
        if self.dirEdit.text():  # If Last Source Directory is holding any path,
            initDir = self.dirEdit.text()  # set the initDir to hold that path
        else:  # if no path currently being displayed, use home folder instead.
            initDir = str(Path.home())
        # open file dialog box (parent, caption, directory, file type filters)
        files, filter = QFileDialog.getOpenFileNames(
            self, "Choose Files to Rename", initDir, filter=FILTERS
        )
        if len(files) > 0:  # if user has selected at least one file
            fileExtension = filter[filter.index("*") : -1]  # slice text of the .extensionLabel object to get file extension
            self.extensionLabel.setText(fileExtension)
            # Create path object using path to first file in list of files.
            # .parent attribute holds path to the containing directory.
            srcDirName = str(Path(files[0]).parent)
            self.dirEdit.setText(srcDirName)
            # for each file, create a Path object and append it to ._files
            for file in files:
                self._files.append(Path(file))
                self.srcFileList.addItem(file)  # add each file to selected file list widget
            self._filesCount = len(self._files)

    def renameFiles(self):
        self._runRenamerThread()

    def _runRenamerThread(self):
        prefix = self.prefixEdit.text()
        self._thread = QThread()  # New thread to offload the renaming process.
        self._renamer = Renamer(
            files=tuple(self._files),
            prefix=prefix,
        )
        self._renamer.moveToThread(self._thread)  # Instantiate renamer.
        # Rename
        # Connect .started signal with .renameFiles() on renamer instance
        self._thread.started.connect(self._renamer.renameFiles)
        # Update state
        self._renamer.renamedFile.connect(self._updateStateWhenFileRenamed)
        self._renamer.progressed.connect(self._updateProgressBar)
        self._renamer.finished.connect(self._updateStateWhenNoFiles)
        # Clean up
        self._renamer.finished.connect(self._thread.quit)
        self._renamer.finished.connect(self._renamer.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        # Run the thread
        self._thread.start()

    def _updateStateWhenFileRenamed(self, newFile):
        self._files.popleft()
        self.srcFileList.takeItem(0)
        self.dstFileList.addItem(str(newFile))

    def _updateProgressBar(self, fileNumber):
        progressPercent = int(fileNumber / self._filesCount * 100)
        self.progressBar.setValue(progressPercent)
