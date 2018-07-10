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

from rnaiutilities.globals import FEATURECLASS, WELL
from rnaiutilities.globals import GENE, SIRNA, LIBRARY, DESIGN
from rnaiutilities.globals import REPLICATE, PLATE, STUDY, PATHOGEN

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseQueryBuilder:
    _sirna_ = SIRNA
    _gene_ = GENE
    _well_ = WELL
    _gsw_ = [_gene_, _sirna_, _well_]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def build_select_query(self, select, **kwargs):
        """Translates the user's query into an SQL statement"""
        q = self._build_select_query(select, **kwargs)
        logger.info(q)
        return q

    def build_query(self, **kwargs):
        """Translates the user's query into an SQL statement"""
        q = self._build_file_name_query(**kwargs)
        logger.info(q)
        return q

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

    @staticmethod
    def read_query_file(file_name):
        res = []
        with open(file_name, "r") as fh:
            for line in fh.readlines():
                tokens = line.strip().split("\t")
                res.append((*tokens,))
        return res

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
                if k in DatabaseQueryBuilder._descr_:
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

    def _build_select_query(self, select, **kwargs):
        if not self._query_has_filters(**kwargs):
            if select in [DatabaseQueryBuilder._gene_,
                          DatabaseQueryBuilder._sirna_,
                          DatabaseQueryBuilder._well_]:
                return "SELECT distinct {} from {};".format(select, select)
            else:
                return "SELECT distinct {} from meta;".format(select)

        # get the three table queries
        mq, gq, sq = self._build_subqueries("*", **kwargs)
        # in case we want to select genes or sirnas, we need to enforce
        # that the tables are still joined
        # otherwise we cannot find the selectable column later
        if select in DatabaseQueryBuilder._gsw_:
            if select == DatabaseQueryBuilder._sirna_ and sq is None:
                sq = "SELECT * FROM sirna"
            elif select == DatabaseQueryBuilder._gene_ and gq is None:
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

    @staticmethod
    def create_meta_table_statement():
        s = "CREATE TABLE IF NOT EXISTS meta " + \
            "(" + \
            "id serial, "
        for col in DatabaseQueryBuilder._descr_:
            s += "{} varchar(100) NOT NULL, ".format(col)
        s += "filename varchar(1000) NOT NULL, " + \
             "PRIMARY KEY(id)" + \
             ");"
        logger.info(s)
        return s

    @staticmethod
    def create_table_name(t):
        s = "CREATE TABLE IF NOT EXISTS {} ".format(t) + \
            "(" + \
            "id serial, " + \
            "{} varchar(100) NOT NULL, ".format(t) + \
            "filename varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(id)" + \
            ");"
        logger.info(s)
        return s

    @staticmethod
    def create_into_meta_statement(
      file, study, bacteria, library, design, replicate, plate, featureclass):
        s = "INSERT INTO meta " \
            "({}, {}, {}, {}, {}, {}, {}, {}) " \
                .format(STUDY, PATHOGEN, LIBRARY, DESIGN,
                        REPLICATE, PLATE, FEATURECLASS, "filename") + \
            "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');" \
                .format(study, bacteria, library, design, replicate, plate,
                        featureclass, file)

        return s

    @staticmethod
    def insert_into_statement(k, v, file):
        s = "INSERT INTO {} ({}, filename) VALUES('{}', '{}')" \
            .format(k, k, v, file)
        return s

    @staticmethod
    def create_file_feature_table(tab):
        s = "CREATE TABLE IF NOT EXISTS {}".format(tab) + \
            " (feature varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(feature));"
        logger.info(s)
        return s

    @staticmethod
    def create_meta_index():
        s = "CREATE INDEX meta_index ON meta ({});" \
            .format(", ".join(DatabaseQueryBuilder._descr_))
        logger.info(s)
        return s

    @staticmethod
    def create_table_index(t):
        s = "CREATE INDEX {}_index ON {} ({});".format(t, t, t)
        logger.info(s)
        return s
