rnai-query
----------

``rnai-query`` builds on the previously **parsed** Matlab files (see
:doc:`rnai_parse`) and uses them for quickly subsetting the complete dataset
of single-cells using an *SQLite*.

For that, you first need to create a database that indexes the plates` meta
information. Having the database set up, you can query for different plates
and compile different data-sets.

The following sections will explain how ``rnai-query`` and its subcommands
are used. So far the following subcommands are available:

* ``rnai-query insert`` for inserting meta information to a database,
* ``rnai-query query`` for creating datasets,
* ``rnai-query select`` for selecting single variables from the database.

**The steps have to be taken in succession (or at least insert has to be the first command to be executed), so make sure to read it all**.


Inserting meta information
..........................

Before being able query the database, we need to insert the parsed meta files.
We can to that by calling:

.. code-block:: bash

  rnai-query insert --db /i/am/a/file/called/tix.db
                    /i/am/a/path/to/parsed/data

where ``/i/am/a/path/to/parsed/data`` points to the folder where the ``*meta.tsv``
and ``*data.tsv`` files lie (the result from :doc:`rnai_parse`).
This creates an *SQLite* database called ``tix.db`` which we will use for
querying the data and creating datasets.


Creating data-sets
..................

Having the database set up, we can query it and create custom
single-cell data-sets by filtering on meta information. As a motivating
example consider these two scripts:

.. code-block:: bash

  rnai-query query --db /i/am/a/file/called/tix.db --sample 10 OUTFILE
  rnai-query query --db /i/am/a/file/called/tix.db --plate dz05-1e --gene pik3ca OUTFILE

The first query would return 10 single cells randomly sampled from each well
from all plates and write it to the file `OUTFILE`. The second query would
only look at plate *dz05-1e* and gene *pik3ca* and write the single cells
that fit the criteria to `OUTFILE`.

The next sections walk you through using ``rnai-query query``.


.. _cmdlineargs-label:

Command line arguments
======================

Say we would want to filter the database on some critera and only write the
single-cell features that fit these conditions. Using ``rnai-query query`` you
can choose which plates/gene/sirnas/etc. to choose from, by setting the
respective command line arguments:

--study
    The study to query for, e.g. like 'infectx', or a comma-separated string
    of libraries, such as 'infectx,infectx_published'.

--pathogen
    The pathogen to query for, e.g. like 'adeno', or a comma-separated string of pathogens, such as 'adeno, bartonella'.

--library
    The library to query for, e.g. like 'd', or a comma-separated string of libraries, such as 'd,q'.

--plate
    The plate to query for, e.g. like 'dz03-1k', or a comma-separated string of plates, such as 'dz03-1k,dz04-1k'.

--design
     The design to query for, e.g. like 'p'.

--replicate
    The replicate to query for, e.g. like '1', or a comma-separated string of replicates, such as '1,4'.

--gene
    The gene to query for, e.g. like 'pik3ca', or a comma-separated string of genes, such as 'pik3ca,pik4ca'.

--sirna
    The sirna to query for, e.g. like 's12312', or a comma-separated string of sirnas, such as 's12312,s123112'.

--well
     The well to query for, e.g. like 'a01', or a comma-separated string of wells, such as 'a01,l05'.

--featureclass
    The featureclass to query for, e.g. like 'cells' or a or a comma-separated string of cells, such as 'cells,perinuclei,nuclei'.

--sample
     The amount of single cells that are sampled per well,like '100'. If unset defaults to all cells.

--debug
    Dont write the files, put only print debug information.

--help
    Print a help message.


**If any argument is not specified it is internally set to None, the whole database will be searched and no filters applied.**


Examples
========

Here, we show some examples how you can query. In these examples we use a
*SQLite* database called ``database.db``.


Sample 100 cells from every well for every plate and write to *OUTFILE*.

.. code-block:: bash

  rnai-query query --db database.db
                   --sample 100
                   OUTFILE


Filter by pathogens *shigella* and *bartonella* and write to *OUTFILE*.

.. code-block:: bash

  rnai-query query --db database.db
                   --pathogen shigella,bartonella
                   OUTFILE


Filter by pathogens *Shigella* and *Bartonella* and gene *pik3ca* and write
to *OUTFILE*.

.. code-block:: bash

  rnai-query query --db database.db
                   --pathogen shigella,bartonella
                   --gene pik3ca
                   OUTFILE


Filter by pathogens *Shigella* and *Bartonella* and gene *pik3ca* and only
write debug info.

.. code-block:: bash

  rnai-query query --db database.db
                   --pathogen shigella,bartonella
                   --gene pik3ca
                   --debug
                   OUTFILE


Filter by gene *nfkb1*, pathogen *Shigella*, study *infectx*, *pooled*
designs, sample 1000 cells per well and write to output

.. code-block:: bash

  rnai-query query --db database.db
                   --gene nfkb1
                   --pathogen shigella
                   --study infectx
                   --design p
                   --sample 1000
                   OUTFILE


Filter by gene *pik3ca* and *mock*, feature classes *cells* and *perinuclei*,
pathogens *Shigella* and *Bartonella*, library *Dharmacon* with a *pooled*
siRNA design, sample 100 cells from each well and write to *OUTFILE*.

.. code-block:: bash

  rnai-query query --db /i/am/a/file/called/tix.db
                   --featureclass cells,perinuclei
                   --gene pik3ca,mock
                   --library d
                   --design p
                   --pathogen shigella,bartonella
                   --sample 100
                   OUTFILE


Selecting single variables from the database
............................................

Sometimes we might want to select single features from the database without
writing them to a file, for instance

* if we want to see which genes are available for a pathogen,
* to see which libraries are available for a pathogen,
* to see which plates carry which genes,
* ...

We can use ``rnai-query select`` for this kind of question. For example, if
we are interested in finding which genes are available on plate *dz05-1e*, we
would call

.. code-block:: bash

   rnai-query select --plate dz05-1e gene

``rnai-query select`` takes the same filters as ``rnai-query query``, except
*sample*, and *debug*, so check section :ref:`cmdlineargs-label`.


Examples
========

Here, we show some examples how you can select variables. In these examples we
use a *SQLite* database called ``database.db``.


Select which genes are available for pathogens *shigella* and *bartonella*.

.. code-block:: bash

  rnai-query select --db database.db
                    --pathogen shigella,bartonella
                    genes


Select which libraries are available for pathogens *shigella* and
*bartonella* and gene *pik3ca*.

.. code-block:: bash

  rnai-query select --db database.db
                    --pathogen shigella,bartonella
                    --gene pik3ca
                    library


Select pathogens for which *pik3ca* and *mock*, feature classes *cells*
and *perinuclei*, library *Dharmacon* with a *pooled* siRNA design are
available.

.. code-block:: bash

  rnai-query query --db /i/am/a/file/called/tix.db
                   --featureclass cells,perinuclei
                   --gene pik3ca,mock
                   --library d
                   --design p
                   pathogen
