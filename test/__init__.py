"""
SPOS - Small Payload Object Serializer
Copyright (C) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest


class TestCase(unittest.TestCase):
    def assertClose(self, val1, val2, delta=0.01, error_msg=""):
        error_msg = (
            error_msg
            if error_msg
            else "Values {0} - {1} differ.".format(val1, val2)
        )
        self.assertTrue(abs(val1 - val2) < delta, error_msg)

    def assertArray(self, arr1, arr2, delta=0.01, error_msg=""):
        error_msg = (
            error_msg
            if error_msg
            else "Arrays differ:\n{0}\n{1}".format(arr1, arr2)
        )
        self.assertEqual(len(arr1), len(arr2), error_msg)
        for i, _ in enumerate(arr1):
            if isinstance(arr1[i], float) or isinstance(arr2[i], float):
                self.assertClose(arr1[i], arr2[i], delta, error_msg)
            elif isinstance(arr1[i], dict):
                self.assertDict(arr1[i], arr2[i], delta, error_msg)
            else:
                self.assertEqual(arr1[i], arr2[i], error_msg)

    def assertDict(self, dict1, dict2, delta=0.01, error_msg=""):
        error_msg = (
            error_msg
            if error_msg
            else "Dicts differ:\n{0}\n{1}".format(dict1, dict2)
        )
        self.assertEqual(dict1.keys(), dict2.keys(), error_msg)
        for key in dict1:
            if isinstance(dict1[key], float) or isinstance(dict2[key], float):
                self.assertClose(dict1[key], dict2[key], delta, error_msg)
            elif isinstance(dict2[key], dict):
                self.assertDict(dict1[key], dict2[key], delta, error_msg)
            elif isinstance(dict2[key], list):
                self.assertArray(dict1[key], dict2[key], delta, error_msg)
            else:
                self.assertEqual(dict1[key], dict2[key], error_msg)
