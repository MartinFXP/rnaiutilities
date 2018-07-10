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


import re

NONE = "none"

GENE = "gene"
SIRNA = "sirna"
WELL = "well"

IMAGE = "image."
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

BSCORE = "bscore"
LOESS = "loess"
ZSCORE = "zscore"

ADDED_COLUMNS_FOR_PRINTING = {
    'cells': [
        'parent_nuclei',
        'children_invasomes_count',
        'children_bacteria_count'
    ]
}

# file that stores the inforation which well is at which position.
# great stuff :)
IMAGE_MAPPING_FILE = "Image.FileName_OrigDNA".lower()

# shouldnt that be sufficient???
USABLE_FEATURES = [
    "bacteria",
    "cells",
    "nuclei",
    "perinuclei",
    "expandednuclei",
    "invasomes"]

# the latter two can probably be combined
UNUSED_PLATE_FEATURE_REGEX = re.compile(
  ".*((BACKUP)|(INVASIN)|(OLIGOPROFILE)|(TITRATION)|"
  "(RHINO-TEST)|(1PMOL)).*".upper())

# features to be skipped during parsing file names
SKIPPABLE_FEATURE_NAMES = list(
  map(lambda x: x.lower(), [
      "Batch_handles.",
      "Neighbors.",
      "ERGIC53.",
      "TGN46.",
      "Bacteria.SubObjectFlag.",
      "CometTails.",
      "DAPIFG.",
      "BlobBacteria."]))

# features to be skipped based on regex during parsing file names
SKIPPABLE_FEATURE_REGEX = [
    re.compile(".*_subcell.*"), re.compile(".*subobjectflag.*")]
