"""
SPOS - Small Payload Object Serializer
MIT License

Copyright (c) 2020 [Luiz Eduardo Amaral](luizamaral306@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import unittest

test_specs = {
    "test_0": "test/json/test_spec_0.json",
    "test_1": "test/json/test_spec_1.json",
}


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
