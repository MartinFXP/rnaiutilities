# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of rnaiutilities.
#
# rnaiutilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rnaiutilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rnaiutilities. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import logging
import os

import enforce
import numpy as np
import pandas

from rnaiutilities.data_set import DataSet
from rnaiutilities.globals import WELL, GENE, SIRNA, \
    SAMPLE, ADDED_COLUMNS_FOR_PRINTING
from rnaiutilities.io.io import IO
from rnaiutilities.normalization.normalizer import Normalizer
from rnaiutilities.table_file_set import TableFileSet
from rnaiutilities.utility.functional import filter_by_prefix, \
    inverse_filter_by_prefix

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class QueryResult:
    """
    Set of results derived from a database query.
    """

    _filter_attributes_ = [GENE, SIRNA, WELL, SAMPLE]
    _sar_ = ".*"

    def __init__(self, tablefile_sets, **kwargs):
        self._tablefile_sets = tablefile_sets
        # filters applied for querying
        self._filters = self._set_filter(**kwargs)
        self._shared_features = self._get_shared_features()
        self._sample, self._filter_fn = 2 ** 30, lambda x: x
        self._normalizer = Normalizer()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._tablefile_sets)

    def __iter__(self):
        for tablefileset in self._tablefile_sets:
            yield self._compile(tablefileset)

    def dump(self, sample, normalize, fh=None):
        """
        Print the result set of the database query to tsv or stdout. If a string
        is given as param *fh* prints to file, otherwise if None is given prints
        to stdout.

        :param sample: number of samples to draw from every well or None
        :param sample: int or None
        :param normalize: a list of normalisation methods to use, e.g. like
         'zscore'. Options so far are 'bscore', 'loess' and 'zscore'.
        :type normalize: list(str)
        :param fh: name of the file or None
        :type fh: str
        """

        self._set_normalization(normalize)
        self._set_sample_size(sample)
        with IO(fh) as io:
            for data in self:
                if data is not None:
                    io.dump(data)
        logger.info("Successfully wrote table files!")

    def _set_normalization(self, normalize):
        """
        Set the used normalisations.

        :param normalize: string of normalisation technmethodsiques
        """

        self._normalizer.set_normalization(normalize)

    def _set_sample_size(self, sample):
        self._sample = sample if sample is not None else 2 ** 30
        # lambda function for sampling
        self._filter_fn = lambda x: x.loc[np.random.choice(
          x.index, self._sample, False), :] if len(x) >= self._sample else x

    def _compile(self, tablefileset):
        """
        Converts a table file set to a pandas dataframe
        """

        try:
            # test if the data files can be found
            if all(os.path.isfile(f) for f in tablefileset.filenames):
                # read the data files, i.e. cells/nuclei/perinuclei
                data = self._read(tablefileset)
                # compile everything together
                data = self._process(data)
                # append study/pathogen/library/...
                data = self._insert_columns(data, tablefileset)
                return data
            else:
                raise ValueError("Could not find files: {}".format(
                  ", ".join(tablefileset.filenames)))
        except Exception as e:
            logger.error("Error occured for tablefileset {}: {}"
                         .format(tablefileset.classifier, e))
        return None

    @enforce.runtime_validation
    def _read(self, tablefileset: TableFileSet):
        """
        Read the data files from a plate and concatenate the single tables.
        Since the dimensions of the tables should be the same, the concatenation
        should work. If the dimensions do not fit (i.e. the mapping did not
        work), `None` is returned.

        :param tablefileset: the object to be parsed
        :type tablefileset: TableFileSet
        :return: returns the merged data as DataSet or None if the concat did
         not work
        :rtype: DataSet
        """

        # read the X files to memory
        tables = [pandas.read_csv(f, sep="\t", header=0)
                  for f in tablefileset.filenames]
        # check if the dimensions of the tables are the same
        self._check_table_dimensions(tables, tablefileset)
        # iterate over the tables and drop the redundant meta information
        tables = self._drop_meta_columns(tables, tablefileset)
        # merge the three tables together column-wise
        data_merged = pandas.concat(tables, axis=1)

        return DataSet(data_merged,
                       tablefileset.feature_classes,
                       tablefileset.features,
                       tablefileset.classifier)

    @staticmethod
    def _check_table_dimensions(tables, tfs):
        for i in range(len(tables) - 1):
            for j in range(i + 1, len(tables)):
                if tables[i].shape[0] != tables[j].shape[0]:
                    raise ValueError(
                      "TableFileSet's {} data files do not have "
                      "matching dimensions.".format(tfs.classifier))

    @staticmethod
    def _drop_meta_columns(tables, tablefileset):
        # get meta column names
        meta_cols = inverse_filter_by_prefix(
          tables[0].columns, tablefileset.feature_classes)
        # iterate over the plate meta columns and drop them from the tables
        for i in range(1, len(tables)):
            meta_cols_curr = inverse_filter_by_prefix(
              tables[i], tablefileset.feature_classes)
            if meta_cols != meta_cols_curr:
                raise ValueError(
                  "Meta column names are not equal: {}".format(tablefileset))

            feat_col_names = filter_by_prefix(
              tables[i], tablefileset.feature_classes)
            tables[i] = tables[i][feat_col_names]

        return tables

    @enforce.runtime_validation
    def _process(self, data: DataSet):
        """
        Process a plate data set file. The following preprocessing
         steps are done:

        * drop columns that are not in the shared feature set, i.e., keep only
          columns that every TableFileSet has
        * normalize the features using the set normalisation parameters
        * filter the data by the defined criteria (i.e. genes/sirna)
        * sample the cells from every well

        :param data: a plate data set
        :type data: DataSet
        :return: returns the preprocessed data set or None
        :rtype: DataSet
        """

        # only take subset of columns that every tablefileset has
        # otherwise we don't get a nice tabular dataset in the end
        data = self._set_correct_columns(data)
        data = self._normalizer.normalize_plate(data)
        # filter by well/sirna/gene
        data = self._filter_data(data)
        # sample from each well 'sample' number if times
        data = self._sample_data(data)

        return data

    def _set_correct_columns(self, data):
        # Subset the dataframe for columns that are shared
        # in all tablefile sets.

        feature_classes = data.feature_classes
        # get the columns in data that are feature columns
        feat_cols = set(filter_by_prefix(data.data.columns, feature_classes))
        # get the columns that are meta columns, such as gene/well/etc.
        meta_cols = inverse_filter_by_prefix(data.data.columns, feature_classes)
        # make sure to only take columns that are in the
        feat_cols = list(feat_cols & set(self._shared_features))
        data.data = data.data[meta_cols + feat_cols]
        # add features that are explicitely desired
        # but not found in every screen :(
        for feature_class in feature_classes:
            if feature_class in ADDED_COLUMNS_FOR_PRINTING:
                for col in ADDED_COLUMNS_FOR_PRINTING[feature_class]:
                    add_col = feature_class + "." + col
                    if add_col not in data.data:
                        # add the new column
                        data.data.insert(len(data.data.columns), add_col, 0)
                        # add the column to the new feature set for later check
                        feat_cols.append(add_col)
        # sort columns
        # (this should be a sufficient condition for optimal overlap)
        feat_cols = sorted(feat_cols)
        data.data = data.data.reindex(
          meta_cols + feat_cols, axis=1, copy=False)
        data.feature_columns = feat_cols

        if len(data.feature_columns) != len(self._shared_features):
            raise ValueError(
              "Data does not have the correct number of features. Skipping.")
        if data.data is None:
            raise ValueError("Data is none after setting columns.")
        return data

    def _filter_data(self, data):
        well = self.__getattribute__("_" + WELL)
        gene = self.__getattribute__("_" + GENE)
        sirna = self.__getattribute__("_" + SIRNA)
        logger.info("\tfiltering data on well '{}', gene '{}' and sirna '{}'."
                    .format(well, gene, sirna))
        data.data = data.data[
            data.data.well.str.contains(well) &
            data.data.gene.str.contains(gene) &
            data.data.sirna.str.contains(sirna)]
        if len(data.data) == 0:
            raise ValueError("Data is zero after filtering")
        return data

    def _sample_data(self, data):
        if self.__getattribute__("_" + SAMPLE) != QueryResult._sar_:
            logger.info("\tsampling {} cells/well.".format(str(self._sample)))
            data.data = data.data.groupby([WELL, GENE, SIRNA]).apply(
              self._filter_fn)
            if len(data.data) == 0:
                raise ValueError("Data is zero after sampling.")
        return data

    def _set_filter(self, **kwargs):
        fls = []
        for k, v in kwargs.items():
            if k in QueryResult._filter_attributes_:
                if v is not None:
                    reg = "^" + "|".join(v.split(",")) + "$"
                    # user provided gene/sirna/well regex to match
                    self.__setattr__("_" + k, reg)
                else:
                    # if user didnt provide anything match all
                    self.__setattr__("_" + k, QueryResult._sar_)
                fls.append(v)
        return fls

    def _get_shared_features(self):
        # create a minimal set of features for every table set file
        features_set = set()
        for tablefile in self._tablefile_sets:
            if len(features_set) == 0:
                features_set = tablefile.features
            else:
                features_set &= tablefile.features
        # add all required columns that we most definitely want all table file
        # sets to have, e.g. bacterial counts or parent nuclei
        for feature_class, cols in ADDED_COLUMNS_FOR_PRINTING.items():
            for col in cols:
                add_col = feature_class + "." + col
                features_set.add(add_col)
        return sorted(list(features_set))

    @staticmethod
    def _insert_columns(data, table):
        data.data.insert(0, "plate", table.plate)
        data.data.insert(0, "replicate", table.replicate)
        data.data.insert(0, "design", table.design)
        data.data.insert(0, "library", table.library)
        data.data.insert(0, "pathogen", table.pathogen)
        data.data.insert(0, "study", table.study)
        return data
