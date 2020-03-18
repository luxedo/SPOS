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


class SposTestCase(unittest.TestCase):
    def assertClose(self, val1, val2, delta=0.01, error_msg=""):
        error_msg = (
            error_msg if error_msg else "Values {0} - {1} differ.".format(val1, val2)
        )
        self.assertTrue(abs(val1 - val2) < delta, error_msg)

    def assertArray(self, arr1, arr2, delta=0.01, error_msg=""):
        error_msg = (
            error_msg if error_msg else "Arrays differ:\n{0}\n{1}".format(arr1, arr2)
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
            error_msg if error_msg else "Dicts differ:\n{0}\n{1}".format(dict1, dict2)
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


class TestValidateBlock(SposTestCase):
    def test_key_not_in_block(self):
        with self.assertRaises(KeyError):
            block = {"type": "boolean"}
            spos.validate_block(block)

    def test_key_value_not_a_string(self):
        with self.assertRaises(TypeError):
            block = {"type": "boolean", "key": True}
            spos.validate_block(block)

    def test_type_not_in_block(self):
        with self.assertRaises(KeyError):
            block = {"key": "aloha"}
            spos.validate_block(block)

    def test_undefined_type(self):
        with self.assertRaises(ValueError):
            block = {"key": "aloha", "type": "hakuna"}
            spos.validate_block(block)

    def test_missing_required_key(self):
        with self.assertRaises(KeyError):
            block = {"key": "aloha", "type": "integer"}
            spos.validate_block(block)

    def test_wrong_type_for_required_key(self):
        with self.assertRaises(TypeError):
            block = {"key": "aloha", "type": "integer", "bits": "mattata"}
            spos.validate_block(block)

    def test_wrong_type_for_optional_key(self):
        with self.assertRaises(TypeError):
            block = {"key": "aloha", "type": "integer", "bits": 1, "offset": "mattata"}
            spos.validate_block(block)

    def test_invalid_key(self):
        with self.assertRaises(KeyError):
            block = {"key": "aloha", "type": "integer", "bits": 1, "mattata": "mattata"}
            spos.validate_block(block)


class TestBlock(SposTestCase):
    def test_boolean_true(self):
        block = {"key": "boolean encode true", "type": "boolean"}
        t = True
        a = "0b1"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_boolean_false(self):
        block = {"key": "boolean false", "type": "boolean"}
        t = False
        a = "0b0"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_binary_block(self):
        block = {"key": "binary bin", "type": "binary", "bits": 10}
        t = "0b100101"
        a = "0b0000100101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), a)
        self.assertEqual(spos.encode_block(a, block), a)

    def test_binary_value_error(self):
        with self.assertRaises(ValueError):
            block = {
                "key": "binary bin error",
                "type": "binary",
                "bits": 10,
            }
            spos.encode_block("0xfail", block)

    def test_binary_hex(self):
        block = {
            "key": "binary large hex",
            "type": "binary",
            "bits": 10,
        }
        t = "0xdeadbeef"
        a = bin(int(t, 16))[:12]
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), a)

    def test_binary_small_hex(self):
        block = {
            "key": "binary small hex",
            "type": "binary",
            "bits": 10,
        }
        t = "0xff"
        a = truncate_bits(bin(int(t, 16))[:12], block["bits"])
        self.assertEqual(spos.encode_block(t, block), a)

    def test_binary_hex_value_error(self):
        with self.assertRaises(ValueError):
            block = {
                "key": "binary hex fail",
                "type": "binary",
                "bits": 10,
            }
            spos.encode_block("0xfail", block)

    def test_binary_type_error(self):
        with self.assertRaises(TypeError):
            block = {
                "key": "binary type fail",
                "type": "binary",
                "bits": 10,
            }
            spos.encode_block("fail", block)

    def test_integer_block(self):
        block = {
            "key": "integer test",
            "type": "integer",
            "bits": 6,
        }
        t = 1
        a = "0b000001"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_integer_type_error(self):
        with self.assertRaises(TypeError):
            block = {
                "key": "integer fail",
                "type": "integer",
                "bits": 6,
            }
            spos.encode_block("fail", block)

    def test_integer_offset(self):
        block = {
            "key": "integer offset",
            "type": "integer",
            "bits": 6,
            "offset": 100,
        }
        t = 120
        a = "0b010100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_integer_underflow(self):
        block = {
            "key": "integer underflow",
            "type": "integer",
            "bits": 6,
        }
        t = -10
        a = "0b000000"
        self.assertEqual(spos.encode_block(t, block), a)

    def test_integer_overflow(self):
        block = {
            "key": "integer overflow",
            "type": "integer",
            "bits": 6,
        }
        t = 128
        a = "0b111111"
        self.assertEqual(spos.encode_block(t, block), a)

    def test_float_block(self):
        block = {"key": "float test", "type": "float", "bits": 2}
        t = 0.66
        a = "0b10"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

    def test_float_type_error(self):
        with self.assertRaises(TypeError):
            block = {
                "key": "float fail",
                "type": "float",
                "bits": 4,
            }
            spos.encode_block("fail", block)

    def test_float_approximation_floor(self):
        block = {
            "key": "float approximation floor",
            "type": "float",
            "bits": 2,
            "approximation": "floor",
        }
        t = 0.66
        a = "0b01"
        t_dec = 0.33
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t_dec)

    def test_float_approximation_ceil(self):
        block = {
            "key": "float approximation ceil",
            "type": "float",
            "bits": 2,
            "approximation": "ceil",
        }
        t = 0.34
        a = "0b10"
        t_dec = 0.66
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t_dec)

    def test_float_upper(self):
        block = {
            "key": "float upper",
            "type": "float",
            "bits": 5,
            "upper": 31,
        }
        t = 13
        a = "0b01101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

    def test_float_lower(self):
        block = {
            "key": "float lower",
            "type": "float",
            "bits": 3,
            "lower": -6,
        }
        t = -1
        a = "0b101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

    def test_float_underflow(self):
        block = {
            "key": "float underflow",
            "type": "float",
            "bits": 6,
        }
        t = -10
        a = "0b000000"
        self.assertEqual(spos.encode_block(t, block), a)

    def test_float_overflow(self):
        block = {
            "key": "float overflow",
            "type": "float",
            "bits": 6,
        }
        t = 10
        a = "0b111111"
        self.assertEqual(spos.encode_block(t, block), a)

    def test_pad_block_2(self):
        block = {"key": "pad test", "type": "pad", "bits": 2}
        t = None
        a = "0b11"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_pad_block_6(self):
        block = {"key": "pad test", "type": "pad", "bits": 6}
        t = None
        a = "0b111111"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_array_block(self):
        block = {
            "key": "integer array",
            "type": "array",
            "bits": 3,
            "blocks": {"key": "array val", "type": "integer", "bits": 3,},
        }
        t = [1, 2, 3, 4]
        a = "0b100001010011100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_array_truncate(self):
        block = {
            "key": "truncate array",
            "type": "array",
            "bits": 2,
            "blocks": {"key": "array val", "type": "integer", "bits": 3,},
        }
        t = [1, 2, 3, 4, 5]
        a = "0b11001010011"
        t_dec = [1, 2, 3]
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_array_empty(self):
        block = {
            "key": "empty array",
            "type": "array",
            "bits": 7,
            "blocks": {"key": "array val", "type": "integer", "bits": 3,},
        }
        t = []
        a = "0b0000000"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), [])

    def test_array_nested(self):
        block = {
            "key": "nested array",
            "type": "array",
            "bits": 2,
            "blocks": {
                "key": "array val 1",
                "type": "array",
                "bits": 3,
                "blocks": {"key": "array val 2", "type": "integer", "bits": 3,},
            },
        }
        t = [[1, 2], [3, 4]]
        a = "0b10010001010010011100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_object_block(self):
        block = {
            "key": "object",
            "type": "object",
            "items": [
                {"key": "key1", "type": "integer", "bits": 3},
                {"key": "key2", "type": "float", "bits": 5},
            ],
        }
        t = {"key1": 6, "key2": 0.9}
        a = "0b11011100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertDict(spos.decode_block(a, block), t)

    def test_object_nested(self):
        block = {
            "key": "object",
            "type": "object",
            "items": [
                {"key": "key1", "type": "integer", "bits": 3},
                {
                    "key": "key2",
                    "type": "object",
                    "items": [
                        {"key": "nKey", "type": "boolean"},
                        {
                            "key": "nKey2",
                            "type": "object",
                            "items": [{"key": "nKey3", "type": "float", "bits": 8,}],
                        },
                    ],
                },
            ],
        }
        t = {"key1": 6, "key2": {"nKey": False, "nKey2": {"nKey3": 0.8}}}
        a = "0b110011001100"
        j = spos.encode_block(t, block)
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertDict(spos.decode_block(a, block), t)

    def test_object_key_error(self):
        with self.assertRaises(KeyError):
            block = {
                "key": "object missing key",
                "type": "object",
                "items": [
                    {"key": "key1", "type": "integer", "bits": 3},
                    {"key": "key2", "type": "float", "bits": 5},
                    {"key": "key3", "type": "boolean"},
                ],
            }
            t = {"key1": 6, "key2": 0.9}
            spos.encode_block(t, block)

    def test_string_block(self):
        block = {
            "key": "string",
            "type": "string",
            "length": 6,
        }
        t = "test"
        a = "0b111110111110101101011110101100101101"
        t_dec = "++test"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_string_block_unknown_character(self):
        block = {
            "key": "string",
            "type": "string",
            "length": 6,
        }
        t = "test%"
        a = "0b111110101101011110101100101101111111"
        t_dec = "+test/"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_string_custom_alphabeth(self):
        block = {
            "key": "string",
            "type": "string",
            "length": 6,
            "custom_alphabeth": {62: " "},
        }
        t = "test"
        a = "0b111110111110101101011110101100101101"
        t_dec = "  test"
        b = spos.encode_block(t, block)
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_block(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 5, 10],
            "steps_names": ["critical", "low", "charged", "full"],
        }
        t = 2
        a = "0b01"
        t_dec = "low"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_index_0(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 5, 10],
            "steps_names": ["critical", "low", "charged", "full"],
        }
        t = -1
        a = "0b00"
        t_dec = "critical"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_lower_boundary(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 5, 10],
            "steps_names": ["critical", "low", "charged", "full"],
        }
        t = 5
        a = "0b10"
        t_dec = "charged"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_last_index(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 5, 10],
            "steps_names": ["critical", "low", "charged", "full"],
        }
        t = 11
        a = "0b11"
        t_dec = "full"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_auto_steps_names(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 5, 10],
        }
        t = 1
        a = "0b01"
        t_dec = "0<x<=5"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_error_steps_names(self):
        with self.assertRaises(ValueError):
            block = {
                "key": "steps",
                "type": "steps",
                "steps": [0, 5, 10],
                "steps_names": ["one", "two"],
            }
            t = 1
            encoded = spos.encode_block(t, block)
            spos.decode_block(encoded, block)

    def test_categories_block_0(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "critical"
        a = "0b000"
        t_dec = "critical"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_categories_block_1(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "low"
        a = "0b001"
        t_dec = "low"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_categories_block_2(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "charged"
        a = "0b010"
        t_dec = "charged"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_categories_block_3(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "full"
        a = "0b011"
        t_dec = "full"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_categories_block_4(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "unknown"
        a = "0b100"
        t_dec = "error"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_crc_bin(self):
        t = "0b1011110010110010"
        a = "0b10100100"
        b = "0b101111001011001010100100"
        block = {"key": "crc BIN test", "type": "crc8"}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(b, block), True)

    def test_crc_hex(self):
        t = "0xABCD35"
        a = "0b00101011"
        b = "0b10101011110011010011010100101011"
        block = {"key": "crc HEX test", "type": "crc8"}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(b, block), True)


class TestItems(SposTestCase):
    def test_items(self):
        items = [
            {"key": "active", "type": "boolean"},
            {"key": "s3cr37", "type": "binary", "bits": 12},
            {"key": "timestamp", "type": "integer", "bits": 32},
            {"key": "wind speed", "type": "float", "bits": 7},
            {"key": "pad", "type": "pad", "bits": 7},
            # {
            #     "key": "counts",
            #     "type": "array",
            #     "bits": 7,
            #     "blocks": {
            #         "key": "count",
            #         "type": "integer",
            #         "bits": 5,
            #     },
            # },
            {
                "key": "sensor X",
                "type": "object",
                "items": [
                    {"key": "value Y", "type": "integer", "bits": 6},
                    {"key": "value Z", "type": "float", "bits": 6},
                ],
            },
            {"key": "user input", "type": "string", "length": 7},
            {
                "key": "bird sightings",
                "type": "steps",
                "steps": [0, 5, 10, 15, 20],
                "steps_names": [
                    "Bogey",
                    "Par",
                    "Birdie",
                    "Eagle",
                    "Albatross",
                    "Condor",
                ],
            },
            {
                "key": "battery",
                "type": "categories",
                "categories": ["critical", "low", "charged", "full"],
            },
        ]
        values = [
            True,
            "0b1011111011101111",
            1584042831,
            0.7,
            None,
            {"value Y": 10, "value Z": 0.3},
            # [2, 0, 6, 7, 1, 6, 8, 8, 15, 18, 19, 24, 25],
            "burguer",
            1337,
            "charged",
        ]
        a = [
            "0b1",
            "0b101111101110",
            "0b01011110011010101001001101001111",
            "0b1011001",
            "0b1111111",
            "0b001010010011",
            "0b011011101110101011100000101110011110101011",
            "0b101",
            "0b010",
        ]
        values_dec = [
            True,
            "0b101111101110",
            1584042831,
            0.7007874015748031,
            None,
            {"value Y": 10, "value Z": 0.30158730158730157},
            "burguer",
            "Condor",
            "charged",
        ]
        encoded = spos.encode_items(values, items)
        self.assertArray(encoded, a)
        decoded = spos.decode_items(a, items)
        self.assertArray(decoded, values_dec)


class TestEncodeDecode(SposTestCase):
    def test_encode_decode_0(self):
        payload_data = {"holy": "grail", "buffer": [1, 2, 3, 4], "date": 0.98}
        payload_spec = {
            "name": "test encode",
            "version": 1,
            "items": [
                {"key": "holy", "type": "string", "length": 10,},
                {"key": "version", "type": "integer", "value": 1, "bits": 6,},
                {
                    "key": "buffer",
                    "type": "array",
                    "bits": 8,
                    "blocks": {"key": "buf_val", "type": "integer", "bits": 8,},
                },
                {"key": "date", "type": "float", "bits": 6,},
                {"key": "crc", "type": "crc8"},
            ],
        }
        encoded = "0b111110111110111110111110111110100000101011011010100010100101000001000001000000000100000010000000110000010011111010000100"
        decoded = {
            "holy": "+++++grail",
            "version": 1,
            "buffer": [1, 2, 3, 4],
            "date": 0.98,
            "crc": True,
        }
        enc = spos.encode(payload_data, payload_spec)
        self.assertEqual(enc, encoded)
        dec = spos.decode(encoded, payload_spec)
        self.assertDict(dec, decoded)

    def test_encode_decode_1(self):
        payloads = [
            {
                "sent_yesterday": 0,
                "rpi_temperature": 25,
                "voltage": 8,
                "temperature": 23.3,
                "count_arm": 3,
                "count_eri": 5,
                "count_cos": 10,
                "count_fru": 15,
                "count_sac": 20,
            },
            {
                "sent_yesterday": 1,
                "rpi_temperature": 35,
                "voltage": 11.9,
                "temperature": 27.3,
                "count_arm": 10,
                "count_eri": 6,
                "count_cos": 12,
                "count_fru": 18,
                "count_sac": 24,
            },
            {
                "sent_yesterday": 0,
                "rpi_temperature": 51,
                "voltage": 12.5,
                "temperature": 11.8,
                "count_arm": 5,
                "count_eri": 20,
                "count_cos": 6,
                "count_fru": 7,
                "count_sac": 14,
            },
            {
                "sent_yesterday": 1,
                "rpi_temperature": 77,
                "voltage": 14.1,
                "temperature": 34.5,
                "count_arm": 60,
                "count_eri": 8,
                "count_cos": 16,
                "count_fru": 24,
                "count_sac": 32,
            },
            {
                "sent_yesterday": 0,
                "rpi_temperature": 55,
                "voltage": 4.5,
                "temperature": 24.5,
                "count_arm": 11,
                "count_eri": 5,
                "count_cos": 40,
                "count_fru": 3,
                "count_sac": 9,
            },
        ]

        payload_spec = {
            "name": "test payload 2",
            "version": 2,
            "items": [
                {"key": "pad", "type": "pad", "bits": 5},
                {"key": "msg_version", "type": "integer", "value": 2, "bits": 6,},
                {"key": "sent_yesterday", "type": "boolean"},
                {
                    "key": "rpi_temperature",
                    "type": "steps",
                    "steps": [30, 50, 75],
                    "steps_names": ["T<30", "30<T<50", "50<T<75", "T>75"],
                },
                {
                    "key": "voltage",
                    "type": "float",
                    "bits": 6,
                    "lower": 10,
                    "upper": 13,
                },
                {
                    "key": "temperature",
                    "type": "float",
                    "bits": 6,
                    "lower": 5,
                    "upper": 50,
                },
                {"key": "count_arm", "type": "integer", "bits": 6,},
                {"key": "count_eri", "type": "integer", "bits": 6,},
                {"key": "count_cos", "type": "integer", "bits": 6,},
                {"key": "count_fru", "type": "integer", "bits": 6,},
                {"key": "count_sac", "type": "integer", "bits": 6,},
                {"key": "crc8", "type": "crc8"},
            ],
        }

        for payload_data in payloads:
            enc = spos.encode(payload_data, payload_spec)
            dec = spos.decode(enc, payload_spec)
            payload_data["sent_yesterday"] = bool(payload_data["sent_yesterday"])
            payload_data["crc8"] = True
            payload_data["msg_version"] = 2
            if payload_data["voltage"] < 10:  # There's an underflow in the data
                payload_data["voltage"] = 10
            del dec["rpi_temperature"], payload_data["rpi_temperature"]
            self.assertDict(dec, payload_data, 3)

    def test_encode_decode_2(self):
        payloads = [
            {
                "confidences": [0.9, 0.8, 0.7],
                "categories": ["bike", "bike", "scooter"],
                "timestamp": 1234567890,
                "voltage": 12,
                "temperature": 45,
            }
        ]
        payload_spec = {
            "items": [
                {
                    "key": "confidences",
                    "type": "array",
                    "bits": 8,
                    "blocks": {"key": "confidence", "type": "float", "bits": 4,},
                },
                {
                    "key": "categories",
                    "type": "array",
                    "bits": 8,
                    "blocks": {
                        "key": "category",
                        "type": "categories",
                        "categories": ["bike", "skate", "scooter"],
                    },
                },
                {"key": "msg_version", "type": "integer", "value": 1, "bits": 6,},
                {"key": "timestamp", "type": "integer", "bits": 32,},
                {
                    "key": "voltage",
                    "type": "float",
                    "bits": 8,
                    "lower": 10,
                    "upper": 13,
                },
                {
                    "key": "temperature",
                    "type": "float",
                    "bits": 8,
                    "lower": 5,
                    "upper": 50,
                },
            ]
        }
        for payload_data in payloads:
            enc = spos.encode(payload_data, payload_spec)
            dec = spos.decode(enc, payload_spec)
            payload_data["msg_version"] = 1
            self.assertDict(dec, payload_data, 3)

    def test_hex_encode_decode_0(self):
        payload_data = {"holy": "grail", "buffer": [1, 2], "date": 0.98}
        payload_spec = {
            "name": "test encode",
            "version": 1,
            "items": [
                {"key": "holy", "type": "string", "length": 11,},
                {
                    "key": "buffer",
                    "type": "array",
                    "bits": 8,
                    "blocks": {"key": "buf_val", "type": "integer", "bits": 9,},
                },
                {"key": "date", "type": "float", "bits": 7,},
            ],
        }
        encoded = "0b111110111110111110111110111110100000101011011010100010100101000001000001000000000100000010000000110000010011111010000100"
        decoded = {
            "holy": "++++++grail",
            "buffer": [1, 2],
            "date": 0.98,
        }
        enc = spos.hex_encode(payload_data, payload_spec)
        dec = spos.hex_decode(enc, payload_spec)
        self.assertDict(dec, decoded)


if __name__ == "__main__":
    unittest.main()
