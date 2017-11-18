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
import re
from itertools import chain

from rnaiutilities.db.db_setup import DatabaseInserter
from rnaiutilities.filesets.table_file_set import TableFileSet
from rnaiutilities.globals import FEATURECLASS, WELL
from rnaiutilities.globals import GENE, SIRNA, LIBRARY, DESIGN
from rnaiutilities.globals import REPLICATE, PLATE, STUDY, PATHOGEN

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseQuery:
    _sirna_ = SIRNA
    _gene_ = GENE
    _well_ = WELL
    _gsw_ = [_gene_, _sirna_, _well_]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def __init__(self, connection):
        self.__connection = connection

    def select(self, select, **kwargs):
        q = self._build_select_query(select, **kwargs)
        logger.info(q)
        res = self.__connection.query(q)
        res = map(lambda x: x[0], res)
        return res

    def print(self, **kwargs):
        q = self._build_file_name_query(**kwargs)
        logger.info(q)
        res = self._print(q, **kwargs)
        return res

    def query(self, file_name, **kwargs):
        q = self._build_file_name_query(**kwargs)
        if file_name is None:
            logger.info(q)
        res = self._query(q, file_name, **kwargs)
        return res

    def _build_file_name_query(self, **kwargs):
        mq, gq, sq = self._build_subqueries("*", **kwargs)
        su = None
        # put the stuff together as we only need file names
        if gq is not None and sq is not None:
            su = "JOIN (SELECT a1.filename \n" + \
                 "\t\tFROM ({}) a1 \n".format(gq) + \
                 "\t\tJOIN ({}) a2 \n".format(sq) + \
                 "\t\tON (a1.filename = a2.filename) \n" + \
                 "\t) a2"
        elif gq:
            su = "JOIN ({}) a2".format(gq)
        elif sq:
            su = "JOIN ({}) a2".format(sq)
        if su:
            q = "\nSELECT distinct * \n" \
                "\tFROM ({}) a1 \n".format(mq) + \
                "\t" + su + " \n" \
                            "\tON (a1.filename = a2.filename);"
        else:
            q = mq + ";"
        return q

    def _build_subqueries(self, select, **kwargs):
        """
        This builds the subqueries and returns all.

        a) builds the meta query from the meta table
        b) builds the gene query to get filenames for specific genes
        c) builds the sirna query to get filenames for specific sirna
        """

        # select * from meta where (.);
        mq = self._build_meta_query(select, **kwargs)
        # select * from gene where gene = gene
        gq = self._build_plate_query(GENE, **kwargs)
        # select * from sirna where sirna = sirna
        sq = self._build_plate_query(SIRNA, **kwargs)

        return mq, gq, sq

    def _print(self, q, **kwargs):
        return self.__connection.query(q)

    def _query(self, q, file_name, **kwargs):
        # get for relevant files
        if file_name is None:
            results = self.__connection.query(q)
        else:
            results = self.__read_query_file(file_name)
        # merge files of the same plate together
        result_set_map = self._build_result_set(results)
        # setup table file list
        fls = [
            TableFileSet(
              # the key, i.e. file prefix for all the data files
              # (so the name of the plate without feature suffix)
              k,
              # the table files
              x,
              # chain lists of features to one list total
              list(chain.from_iterable(
                [self._feature_query(e[-1]) for e in x])),
              # filtering information
              **kwargs)
            for k, x in result_set_map.items()
        ]
        return fls

    @staticmethod
    def __read_query_file(file_name):
        res = []
        with open(file_name, "r") as fh:
            for line in fh.readlines():
                tokens = line.strip().split("\t")
                res.append((*tokens,))
        return res

    @staticmethod
    def _build_result_set(results):
        """
        Set together the different files belonging to one plate.
        """

        result_set_map = {}
        reg = re.compile("(.+)_\w+_meta.tsv")
        for result in results:
            mat = reg.match(result[-1])
            if mat is not None:
                desc = mat.group(1)
                if desc not in result_set_map:
                    result_set_map[desc] = []
                result_set_map[desc].append(result)
        return result_set_map

    @staticmethod
    def _build_meta_query(what, **kwargs):
        s = "SELECT {} FROM meta".format(what)
        ar = []
        for k, v in kwargs.items():
            if v is not None:
                if isinstance(v, str):
                    varr = v.split(",")
                else:
                    varr = v
                els = []
                if k in DatabaseQuery._descr_:
                    for vel in varr:
                        els.append("{}='{}'".format(k, vel))
                    ar.append("(" + " OR ".join(els) + ")")
        if len(ar) > 0:
            s += " WHERE " + " and ".join(ar)
        return s

    @staticmethod
    def _build_plate_query(el, **kwargs):
        s = None
        if el in kwargs.keys():
            if kwargs[el] is not None:
                varr = kwargs[el].split(",")
                els = []
                for vel in varr:
                    els.append("{}='{}'".format(el, vel))
                eq = "(" + " OR ".join(els) + ")"
                s = "SELECT * FROM {} WHERE {}".format(el, eq)
        return s

    def _feature_query(self, filename):
        d = DatabaseInserter.feature_table_name(filename)
        res = self.__connection.query("SELECT distinct * FROM {}".format(d))
        res = list(map(lambda x: x[0], res))
        return res

    def _build_select_query(self, select, **kwargs):
        if not self._query_has_filters(**kwargs):
            if select in [DatabaseQuery._gene_, DatabaseQuery._sirna_,
                          DatabaseQuery._well_]:
                return "SELECT distinct {} from {};".format(select, select)
            else:
                return "SELECT distinct {} from meta;".format(select)

        # get the three table queries
        mq, gq, sq = self._build_subqueries("*", **kwargs)
        # in case we want to select genes or sirnas, we need to enforce
        # that the tables are still joined
        # otherwise we cannot find the selectable column later
        if select in DatabaseQuery._gsw_:
            if select == DatabaseQuery._sirna_ and sq is None:
                sq = "SELECT * FROM sirna"
            elif select == DatabaseQuery._gene_ and gq is None:
                gq = "SELECT * FROM gene"

        su = None
        if gq is not None and sq is not None:
            su = "JOIN (SELECT * \n" + \
                 "\t\tFROM ({}) a1 \n".format(gq) + \
                 "\t\tJOIN ({}) a2 \n".format(sq) + \
                 "\t\tON (a1.filename = a2.filename) \n" + \
                 "\t) a2"
        elif gq:
            su = "JOIN ({}) a2".format(gq)
        elif sq:
            su = "JOIN ({}) a2".format(sq)
        if su:
            q = "\nSELECT distinct {}\n" \
                "\tFROM ({}) a1 \n".format(select, mq) + \
                "\t" + su + " \n" \
                            "\tON (a1.filename = a2.filename)" \
                            ";"
        else:
            mq = self._build_meta_query(select, **kwargs)
            q = mq + ";"
        return q

    @staticmethod
    def _query_has_filters(**kwargs):
        if any(v is not None for _, v in kwargs.items()):
            return True
        return False
