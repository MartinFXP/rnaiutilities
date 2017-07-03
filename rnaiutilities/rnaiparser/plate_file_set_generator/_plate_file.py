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


class PlateFile:
    """
    Class that stores the feature name and the absolute filename.

    """

    def __init__(self, filename, feature):
        self._filename = filename
        self._feature = feature

    @property
    def filename(self):
        return self._filename

    @property
    def featurename(self):
        return self._feature

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self._feature
