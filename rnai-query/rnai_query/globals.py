# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of tix_query.
#
# tix_query is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tix_query is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tix_query. If not, see <http://www.gnu.org/licenses/>.
#
#
# @author = 'Simon Dirmeier'
# @email = 'mail@simon-dirmeier.net'


import re

GENE = "gene"
SIRNA = "sirna"
WELL = "well"

STUDY = "study"
PATHOGEN = "pathogen"
LIBRARY = "library"
DESIGN = "design"
REPLICATE = "replicate"
PLATE = "plate"
FEATURECLASS = "featureclass"


FEATURES = "features"
ELEMENTS = "elements"
SAMPLE = "sample"

FILE_FEATURES_PATTERNS = re.compile(
      "(\w+)-(\w+)-(\w+)-(\w+)-(\w+)-(\d+)-(.*)_(\w+)")