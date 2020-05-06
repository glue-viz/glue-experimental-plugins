from io import BytesIO

import requests
from astropy.io.votable import parse
from glue.core.data_factories import astropy_tabular_data


def query_vizier(query_text):

    # Do the search using VizieR
    r = requests.post("http://vizier.u-strasbg.fr/viz-bin/votable",
                      {'-words': query_text.split(), '-meta.all': 1})

    # We now loop over the results and construct a list of dictionaries, where
    # each dictionary contains information about one set of tables.
    votablefile = parse(BytesIO(r.content))
    result = []
    for resource in votablefile.resources:
        catalog_set = {}
        catalog_set['description'] = resource.description
        catalog_set['tables'] = []
        for table in resource.tables:
            catalog = {}
            catalog['description'] = table.description
            catalog['nrows'] = str(table.nrows)
            catalog['name'] = str(table.name)
            catalog_set['tables'].append(catalog)
        result.append(catalog_set)

    return result


def fetch_vizier_catalog(catalog_name):
    r = requests.post("http://vizier.u-strasbg.fr/viz-bin/votable",
                      {'-source': catalog_name})
    table = astropy_tabular_data(BytesIO(r.content), format='votable')
    table.label = catalog_name
    return table
