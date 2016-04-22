import os

from glue.external.qt import QtGui
from glue.external.qt.QtCore import Qt
from glue.utils.qt.helpers import load_ui

from .vizier_helpers import query_vizier, fetch_vizier_catalog

__all__ = ["QtVizierImporter"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'vizier.ui')


class QtVizierImporter(QtGui.QDialog):

    def __init__(self):

        super(QtVizierImporter, self).__init__()

        self.ui = load_ui(UI_MAIN, self)

        self.cancel.clicked.connect(self.reject)
        self.ok.clicked.connect(self.finalize)
        self.search_button.clicked.connect(self.search)

        # Focus on anything other than query line otherwise the placeholder
        # text disappears straight away.
        self.search_button.setFocus()

        self.query.setPlaceholderText("Enter a search term here to search for authors, titles, descriptions, etc.")

        self._checkboxes = {}
        self.datasets = []

    def clear(self):
        self._checkboxes.clear()
        self.tree.clear()

    def search(self):

        self.search_button.setEnabled(False)
        self.search_button.setText("Searching")
        QtGui.qApp.processEvents()

        self.clear()

        results = query_vizier(self.query.text())

        for catalog_set in results:
            main = QtGui.QTreeWidgetItem(self.tree.invisibleRootItem(),
                                         [catalog_set['description'], ""])
            main.setFlags(main.flags() | Qt.ItemIsTristate)
            main.setCheckState(2, Qt.Unchecked)
            for catalog in catalog_set['tables']:
                sub = QtGui.QTreeWidgetItem(main)
                sub.setFlags(sub.flags() | Qt.ItemIsUserCheckable)
                sub.setCheckState(2, Qt.Unchecked)
                sub.setText(0, catalog['description'])
                sub.setText(1, catalog['nrows'])
                sub.setText(2, "")
                self._checkboxes[catalog['name']] = sub

        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)

        self.search_button.setEnabled(True)
        self.search_button.setText("Search")


    def finalize(self):

        retrieve = []

        for name in self._checkboxes:
            if self._checkboxes[name].checkState(2) > 0:
                retrieve.append(name)

        self.datasets = []

        for iname, name in enumerate(retrieve):

            self.progress.setValue(iname / float(len(retrieve)) * 100.)
            QtGui.qApp.processEvents()  # update progress bar

            self.datasets.append(fetch_vizier_catalog(name))

        self.progress.setValue(100)
        self.accept()
