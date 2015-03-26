# This plugin requires OpenCV to be installed, and returns a PIL Image object

import os
import sys

from PyQt4.QtGui import QDialog, QApplication, QLabel, QGridLayout, QCheckBox
from PyQt4.uic import loadUi

from astropy.io import fits

UI_MAIN = os.path.join(os.path.dirname(__file__), 'hdu_select.ui')


class HDUListSelector(QDialog):

    def __init__(self, hdulist):

        super(HDUListSelector, self).__init__()

        self.ui = loadUi(UI_MAIN, self)

        self.grid_layout = QGridLayout(self.scroll.widget())

        self.grid_layout.addWidget(QLabel("<b>HDU</b>"), 1, 1)
        self.grid_layout.addWidget(QLabel("<b>Name</b>"), 1, 3)
        self.grid_layout.addWidget(QLabel("<b>Type</b>"), 1, 5)
        self.grid_layout.addWidget(QLabel("<b>Shape</b>"), 1, 7)
        self.grid_layout.addWidget(QLabel("<b>Import?</b>"), 1, 9)
        self.grid_layout.setRowMinimumHeight(1, 40)

        row = 1

        self.checkboxes = {}

        for ihdu, hdu in enumerate(hdulist):

            row += 1

            self.grid_layout.addWidget(QLabel(str(ihdu)), row, 1)

            self.grid_layout.addWidget(QLabel(hdu.name), row, 3)

            if hdu.data.size == 0:
                label = "No data"
                shape = ""
            elif isinstance(hdu, (fits.PrimaryHDU, fits.ImageHDU, fits.CompImageHDU)):
                label = "Image/gridded data"
                shape = "Shape: " + "x".join(hdu.data.shape)
            elif isinstance(hdu, (fits.TableHDU, fits.BinTableHDU)):
                label = "Tabular data"
                shape = "{0} row{1} x {2} column{3}".format(len(hdu.data),
                                                            "s" if len(hdu.data) > 1 else "",
                                                            len(hdu.data.dtype.names),
                                                            "s" if len(hdu.data.dtype.names) > 1 else ""
                                                            )
            else:
                label = "Unknown"
                shape = "Unknown"

            self.grid_layout.addWidget(QLabel(label), row, 5)

            self.grid_layout.addWidget(QLabel(shape), row, 7)

            if label != "No data":
                self.checkboxes[ihdu] = QCheckBox()
                self.checkboxes[ihdu].setChecked(True)
                self.grid_layout.addWidget(self.checkboxes[ihdu], row, 9)

            for col in (2, 4, 6, 8):
                self.grid_layout.setColumnMinimumWidth(col, 30)

            self.grid_layout.setRowMinimumHeight(row, 40)

        self.grid_layout.setRowStretch(row + 1, 10)
        self.grid_layout.setVerticalSpacing(0)

        self.cancel.clicked.connect(self.reject)
        self.ok.clicked.connect(self.finalize)

        self._hdulist = hdulist

    def finalize(self):
        self.selected_hdus = [self._hdulist[ihdu] for ihdu in self.checkboxes if self.checkboxes[ihdu].isChecked()]
        self.accept()

if __name__ == "__main__":

    hdulist = fits.open(sys.argv[1])

    app = QApplication(sys.argv)  # Create an application object
    wi = HDUListSelector(hdulist)
    wi.show()
    app.exec_()
    print(wi.selected_hdus)
