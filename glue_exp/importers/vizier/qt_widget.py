import os

from glue.external.qt import QtGui
from glue.external.qt.QtCore import Qt

# TODO: update to use glue.qt once load_ui has been generalized
from PyQt4.uic import loadUi

from .vizier_helpers import query_vizier, fetch_vizier_catalog

__all__ = ["QtVizierImporter"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'vizier.ui')


class QtVizierImporter(QtGui.QDialog):

    def __init__(self):

        super(QtVizierImporter, self).__init__()

        self.ui = loadUi(UI_MAIN, self)

        self.cancel.clicked.connect(self.reject)
        self.ok.clicked.connect(self.finalize)
        self.search_button.clicked.connect(self.search)

    def search(self):

        results = query_vizier(self.query.text())

        self._checkboxes = {}
        for catalog_set in results:
            main = QtGui.QTreeWidgetItem(self.tree.invisibleRootItem(),
                                         [catalog_set['description'], ""])
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