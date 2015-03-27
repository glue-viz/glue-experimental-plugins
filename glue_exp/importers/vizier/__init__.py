def setup():

    from .qt_widget import QtVizierImporter
    from glue.config import importer

    @importer("Import from VizieR")
    def vizier_importer():
        wi = QtVizierImporter()
        wi.exec_()
        return wi.datasets

