#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
webcam_importer=glue_exp.importers.webcam:setup
vizier_importer=glue_exp.importers.vizier:setup
contour_selection=glue_exp.tools.contour_selection:setup
floodfill_selection=glue_exp.tools.floodfill_selection:setup
dendrogram_selection=glue_exp.tools.dendrogram_selection:setup
"""

setup(name='glue_exp',
      version="0.1.dev0",
      description = "Experimental plugins for glue",
      author='Thomas Robitaille, Chris Beaumont',
      author_email='glueviz@gmail.com',
      url='http://glueviz.org',
      classifiers=[
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Scientific/Engineering :: Visualization',
          'License :: OSI Approved :: BSD License'
          ],
      packages = find_packages(),
      package_data={'glue_exp.importers.vizier': ['*.ui'], 'glue_exp.importers.webcam':['*.ui'], '': ['*.png']},
      entry_points=entry_points
    )
