import os

from glue.external.qt import QtGui, QtCore
from glue.qt import get_qapp
from glue.qt.qtutil import load_ui
from glue.core.data import CategoricalComponent

UI_FILE = os.path.join(os.path.dirname(__file__), 'categorical.ui')


class CategoricalReorder(QtGui.QDialog):

    def __init__(self, parent=None, session=None, data_collection=None):

        super(CategoricalReorder, self).__init__()

        self.ui = load_ui(UI_FILE, self)

        self.session = session
        self.data_collection = data_collection

        self._show_data()

        self._connect()

    def _connect(self):

        self.ok.clicked.connect(self.finalize)
        self.cancel.clicked.connect(self.reject)

        QtCore.QObject.connect(self.data_collection_tree.selectionModel(),
                               QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.select)

    def select(self, selected, deselected):
        for item in self.data_collection_tree.selectedItems():
            label1 = item.text(0)
            label2 = item.text(1)
            if label2.strip() == "":
                return
            else:
                component = self.items[(label1, label2)]
                if isinstance(component, CategoricalComponent):
                    self._show_labels(component)

    def _show_labels(self, component):
        self.ui.component_list.clear()
        for label in component._categories:
            self.ui.component_list.addItem(label)


    def finalize(self):
        pass

    def _show_data(self):
        self.items = {}
        for data in self.data_collection:
            main = QtGui.QTreeWidgetItem(self.data_collection_tree.invisibleRootItem(), [data.label, ""])
            for component in data.components:
                sub = QtGui.QTreeWidgetItem(main, [component.label, data.label])
                self.items[(component.label, data.label)] = data.get_component(component)




# app = get_qapp()
# d = CategoricalReorder()
# d.show()
# app.exec_()
# app.quit()
