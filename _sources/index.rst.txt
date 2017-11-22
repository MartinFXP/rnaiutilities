rnaiutilities
=============

.. image:: http://www.repostatus.org/badges/latest/active.svg
   :target: http://www.repostatus.org/#active
.. image:: https://travis-ci.org/cbg-ethz/rnaiutilities.svg?branch=master
   :target: https://travis-ci.org/cbg-ethz/rnaiutilities/
.. image:: https://codecov.io/gh/cbg-ethz/rnaiutilities/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cbg-ethz/rnaiutilities
.. image:: https://api.codacy.com/project/badge/Grade/1822ba83768d4d7389ba667a9c839638
   :target: https://www.codacy.com/app/simon-dirmeier/rnaiutilities_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cbg-ethz/rnaiutilities&amp;utm_campaign=Badge_Grade
.. image:: https://readthedocs.org/projects/rnaiutilities/badge/?version=latest
   :target: http://rnaiutilities.readthedocs.io/en/latest/
   :alt: doc


A collection of python modules and command line tools for processing image-based RNAi screens.


Introduction
------------

Welcome to ``rnaiutilities``.

``rnaiutilities`` provide a set of python modules and commandline scripts that can be used to process, convert, query and analyse imaged-based RNAi-screens.

The packages are designed for the following workflow:

* Download raw ``mat`` files from an openBIS instance or where ever your data lie. The ``mat`` files are supposed to be created by ``CellProfiler``, i.e. platewise data-sets, where every file describes a single features for single-cells.
* Parse the downloaded data using ``rnai-parse``: install the package, and process as described in the package folder. This generates a list of raw ``tsv`` files or a bundled ``h5`` file. Until now the parser writes featuresets for *cells*, *perinuclei*, *nuclei*,  *expandednuclei*,  *bacteria* and *invasomes*.
* Query the meta DB using ``rnai-query`` and create and combine datasets. For that first meta files generated from the step above are written into a database. Then the DB can be queried against to subset single *genes*, *sirnas*, *pathogens*, etc. and write the *normalized* results.

* To come: ``rnai-analyse`` for analysing large-scale RNAi screens.


The package is still under development, so if you'd like to contribute,
`fork us on GitHub <https://github.com/cbg-ethz/rnaiutilities>`_.


Installation
------------

Make sure to have ``python3`` installed. ``rnaiutilities`` does not support
previous versions. The best way to do that is to download `anaconda <https://www.continuum.io/downloads>`_ and create a
virtual `environment <https://conda.io/docs/using/envs.html>`_.

Download the latest `release <https://github.com/cbg-ethz/rnaiutilities/releases>`_ first and install it using:

.. code-block:: bash

  pip install .


If you get errors, I probably forgot some dependency.


Command line scripts
--------------------

.. toctree::
   :maxdepth: 2

   rnai_parse
   rnai_query

API
----

.. toctree::
   :maxdepth: 2

   modules

Examples
--------

.. toctree::
   :maxdepth: 2

   api

