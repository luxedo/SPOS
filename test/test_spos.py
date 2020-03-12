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
from spos.encoders import truncate_bits
import spos


class TestBlock(unittest.TestCase):
    def assertClose(self, val1, val2, delta=0.01):
        self.assertTrue(abs(val1 - val2) < delta)

    def assertDict(self, dict1, dict2, delta=0.01):
        self.assertEqual(dict1.keys(), dict2.keys())
        for key in dict1:
            if isinstance(dict2[key], float):
                self.assertClose(dict1[key], dict2[key], delta)
            else:
                self.assertEqual(dict1[key], dict2[key])

    def test_boolean_block(self):
        block = {"name": "boolean encode true", "type": "boolean"}
        t = True
        a = "0b1"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        block = {"name": "boolean false", "type": "boolean"}
        t = False
        a = "0b0"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)
        with self.assertRaises(TypeError):
            t = "fail"
            block = {"name": "boolean error", "type": "boolean"}
            self.assertEqual(spos.encode_block(t, block), a)

    def test_binary_block(self):
        block = {"name": "binary bin", "type": "binary", "settings": {"bits": 10}}
        t = "0b100101"
        a = "0b0000100101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), a)
        self.assertEqual(spos.encode_block(a, block), a)

        with self.assertRaises(ValueError):
            block = {
                "name": "binary bin error",
                "type": "binary",
                "settings": {"bits": 10},
            }
            spos.encode_block("0xfail", block)

        block = {
            "name": "binary large hex",
            "type": "binary",
            "settings": {"bits": 10},
        }
        t = "0xdeadbeef"
        a = bin(int(t, 16))[:12]
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), a)

        block = {
            "name": "binary small hex",
            "type": "binary",
            "settings": {"bits": 10},
        }
        t = "0xff"
        a = truncate_bits(bin(int(t, 16))[:12], block["settings"]["bits"])
        self.assertEqual(spos.encode_block(t, block), a)

        with self.assertRaises(ValueError):
            block = {
                "name": "binary hex fail",
                "type": "binary",
                "settings": {"bits": 10},
            }
            spos.encode_block("0xfail", block)

        with self.assertRaises(TypeError):
            block = {
                "name": "binary type fail",
                "type": "binary",
                "settings": {"bits": 10},
            }
            spos.encode_block("fail", block)

    def test_integer_block(self):
        block = {
            "name": "integer test",
            "type": "integer",
            "settings": {"bits": 6},
        }
        t = 1
        a = "0b000001"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        with self.assertRaises(TypeError):
            block = {
                "name": "integer fail",
                "type": "integer",
                "settings": {"bits": 6},
            }
            spos.encode_block("fail", block)

        block = {
            "name": "integer offset",
            "type": "integer",
            "settings": {"bits": 6, "offset": 100},
        }
        t = 120
        a = "0b010100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        block = {
            "name": "integer underflow",
            "type": "integer",
            "settings": {"bits": 6},
        }
        t = -10
        a = "0b000000"
        self.assertEqual(spos.encode_block(t, block), a)

        block = {
            "name": "integer overflow",
            "type": "integer",
            "settings": {"bits": 6},
        }
        t = 128
        a = "0b111111"
        self.assertEqual(spos.encode_block(t, block), a)

    def test_float_block(self):
        block = {"name": "float test", "type": "float", "settings": {"bits": 2}}
        t = 0.66
        a = "0b10"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

        with self.assertRaises(TypeError):
            block = {
                "name": "float fail",
                "type": "float",
                "settings": {"bits": 4},
            }
            spos.encode_block("fail", block)

        block = {
            "name": "float approximation floor",
            "type": "float",
            "settings": {"bits": 2, "approximation": "floor"},
        }
        t = 0.66
        a = "0b01"
        t_dec = 0.33
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t_dec)

        block = {
            "name": "float approximation ceil",
            "type": "float",
            "settings": {"bits": 2, "approximation": "ceil"},
        }
        t = 0.34
        a = "0b10"
        t_dec = 0.66
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t_dec)

        block = {
            "name": "float upper",
            "type": "float",
            "settings": {"bits": 5, "upper": 31},
        }
        t = 13
        a = "0b01101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

        block = {
            "name": "float lower",
            "type": "float",
            "settings": {"bits": 3, "lower": -6},
        }
        t = -1
        a = "0b101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

        block = {
            "name": "float underflow",
            "type": "float",
            "settings": {"bits": 6},
        }
        t = -10
        a = "0b000000"
        self.assertEqual(spos.encode_block(t, block), a)

        block = {
            "name": "float overflow",
            "type": "float",
            "settings": {"bits": 6},
        }
        t = 10
        a = "0b111111"
        self.assertEqual(spos.encode_block(t, block), a)

    def test_pad_block(self):
        block = {"name": "pad test", "type": "pad", "settings": {"bits": 2}}
        t = None
        a = "0b11"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        block = {"name": "pad test", "type": "pad", "settings": {"bits": 6}}
        t = None
        a = "0b111111"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_array_block(self):
        block = {
            "name": "integer array",
            "type": "array",
            "settings": {
                "bits": 3,
                "blocks": {
                    "name": "array val",
                    "type": "integer",
                    "settings": {"bits": 3},
                },
            },
        }
        t = [1, 2, 3, 4]
        a = "0b100001010011100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        block = {
            "name": "truncate array",
            "type": "array",
            "settings": {
                "bits": 2,
                "blocks": {
                    "name": "array val",
                    "type": "integer",
                    "settings": {"bits": 3},
                },
            },
        }
        t = [1, 2, 3, 4, 5]
        a = "0b11001010011"
        t_dec = [1, 2, 3]
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        block = {
            "name": "empty array",
            "type": "array",
            "settings": {
                "bits": 7,
                "blocks": {
                    "name": "array val",
                    "type": "integer",
                    "settings": {"bits": 3},
                },
            },
        }
        t = []
        a = "0b0000000"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), [])

        # Nested arrays another day
        # block = {
        #     "name": "nested array",
        #     "type": "array",
        #     "settings": {
        #         "bits": 2,
        #         "blocks": {
        #             "name": "array val 1",
        #             "type": "array",
        #             "settings": {
        #                 "bits": 3,
        #                 "blocks": {
        #                     "name": "array val 2",
        #                     "type": "integer",
        #                     "settings": {"bits": 3},
        #                 },
        #             },
        #         },
        #     },
        # }
        # t = [[1, 2], [3, 4]]
        # a = "0b10010001010010011100"
        # self.assertEqual(spos.encode_block(t, block), a)
        # self.assertEqual(spos.decode_block(a, block), t)

    def test_object_block(self):
        block = {
            "name": "object",
            "type": "object",
            "settings": {
                "bits": 3,
                "items": [
                    {"name": "key1", "type": "integer", "settings": {"bits": 3},},
                    {"name": "key2", "type": "float", "settings": {"bits": 5},},
                ],
            },
        }
        t = {"key1": 6, "key2": 0.9}
        a = "0b11011100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertDict(spos.decode_block(a, block), t)

        with self.assertRaises(KeyError):
            block = {
                "name": "object missing key",
                "type": "object",
                "settings": {
                    "bits": 3,
                    "items": [
                        {"name": "key1", "type": "integer", "settings": {"bits": 3}},
                        {"name": "key2", "type": "float", "settings": {"bits": 5}},
                        {"name": "key3", "type": "boolean"},
                    ],
                },
            }
            t = {"key1": 6, "key2": 0.9}
            spos.encode_block(t, block)

    def test_string_block(self):
        block = {
            "name": "string",
            "type": "string",
            "settings": {"length": 6},
        }
        t = "test"
        a = "0b111110111110101101011110101100101101"
        t_dec = "++test"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        block = {
            "name": "string",
            "type": "string",
            "settings": {"length": 6},
        }
        t = "test%"
        a = "0b111110101101011110101100101101111111"
        t_dec = "+test/"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_block(self):
        block = {
            "name": "steps",
            "type": "steps",
            "settings": {
                "steps": [0, 5, 10],
                "steps_names": ["critical", "low", "charged", "full"],
            },
        }
        t = 2
        a = "0b01"
        t_dec = "low"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = -1
        a = "0b00"
        t_dec = "critical"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = 5
        a = "0b10"
        t_dec = "charged"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = 11
        a = "0b11"
        t_dec = "full"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_categories_block(self):
        block = {
            "name": "categories",
            "type": "categories",
            "settings": {"categories": ["critical", "low", "charged", "full"],},
        }
        t = "critical"
        a = "0b000"
        t_dec = "critical"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = "low"
        a = "0b001"
        t_dec = "low"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = "charged"
        a = "0b010"
        t_dec = "charged"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = "full"
        a = "0b011"
        t_dec = "full"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

        t = "unknown"
        a = "0b100"
        t_dec = "error"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)
