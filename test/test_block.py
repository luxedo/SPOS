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
import warnings

from spos.blocks import truncate_bits
from . import TestCase
import spos


class TestValidateBlock(TestCase):
    def test_key_not_in_block(self):
        block = {"type": "boolean"}
        with self.assertRaises(KeyError):
            spos.Block(block)

    def test_key_value_not_a_string(self):
        block = {"type": "boolean", "key": True}
        with self.assertRaises(TypeError):
            spos.Block(block)

    def test_type_not_in_block(self):
        block = {"key": "aloha"}
        with self.assertRaises(KeyError):
            spos.Block(block)

    def test_undefined_type(self):
        block = {"key": "aloha", "type": "hakuna"}
        with self.assertRaises(ValueError):
            spos.Block(block)

    def test_missing_required_key(self):
        block = {"key": "aloha", "type": "integer"}
        with self.assertRaises(KeyError):
            spos.Block(block)

    def test_wrong_type_for_required_key(self):
        block = {"key": "aloha", "type": "integer", "bits": "mattata"}
        with self.assertRaises(TypeError):
            spos.Block(block)

    def test_wrong_type_for_optional_key(self):
        block = {
            "key": "aloha",
            "type": "integer",
            "bits": 1,
            "offset": "mattata",
        }
        with self.assertRaises(TypeError):
            spos.Block(block)

    def test_invalid_key(self):
        block = {
            "key": "aloha",
            "type": "integer",
            "bits": 1,
            "mattata": "mattata",
        }
        with self.assertRaises(KeyError):
            spos.Block(block)


class TestBlock(TestCase):
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
        with self.assertRaises(ValueError):
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
            "blocks": {"key": "array val", "type": "integer", "bits": 3},
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
            "blocks": {"key": "array val", "type": "integer", "bits": 3},
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
            "blocks": {"key": "array val", "type": "integer", "bits": 3},
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
                "blocks": {"key": "array val 2", "type": "integer", "bits": 3},
            },
        }
        t = [[1, 2], [3, 4, 5]]
        a = "0b10010001010011011100101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_object_block(self):
        block = {
            "key": "object",
            "type": "object",
            "blocklist": [
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
            "blocklist": [
                {"key": "key1", "type": "integer", "bits": 3},
                {
                    "key": "key2",
                    "type": "object",
                    "blocklist": [
                        {"key": "nKey", "type": "boolean"},
                        {
                            "key": "nKey2",
                            "type": "object",
                            "blocklist": [
                                {"key": "nKey3", "type": "float", "bits": 8}
                            ],
                        },
                    ],
                },
            ],
        }
        t = {"key1": 6, "key2": {"nKey": False, "nKey2": {"nKey3": 0.8}}}
        a = "0b110011001100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertDict(spos.decode_block(a, block), t)

    def test_object_dot_notation_0(self):
        block = {
            "key": "object",
            "type": "object",
            "blocklist": [
                {"key": "key1", "type": "integer", "bits": 3},
                {"key": "key2.surprise", "type": "string", "length": 5},
                {
                    "key": "key2",
                    "type": "object",
                    "blocklist": [
                        {"key": "nKey", "type": "boolean"},
                        {
                            "key": "nKey2",
                            "type": "object",
                            "blocklist": [
                                {"key": "nKey3", "type": "float", "bits": 8}
                            ],
                        },
                    ],
                },
            ],
        }
        t = {
            "key1": 6,
            "key2": {
                "surprise": "hello",
                "nKey": False,
                "nKey2": {"nKey3": 0.8},
            },
        }
        a = "0b110100001011110100101100101101000011001100"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertDict(spos.decode_block(a, block), t)

    def test_object_dot_notation_1(self):
        block = {
            "key": "object",
            "type": "object",
            "blocklist": [
                {"key": "key1.nest1.a", "type": "integer", "bits": 3},
                {"key": "key1.nest1.b", "type": "string", "length": 5},
                {"key": "key1.nest1.c", "type": "integer", "bits": 3},
                {
                    "key": "key1",
                    "type": "object",
                    "blocklist": [
                        {"key": "nest1.d", "type": "integer", "bits": 3},
                        {
                            "key": "nest1",
                            "type": "object",
                            "blocklist": [
                                {"key": "e", "type": "integer", "bits": 3},
                                {"key": "f", "type": "integer", "bits": 3},
                            ],
                        },
                    ],
                },
            ],
        }
        t = {
            "key1": {
                "nest1": {"a": 1, "b": "hello", "c": 2, "d": 3, "e": 4, "f": 5}
            },
        }
        a = "0b001100001011110100101100101101000010011100101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertDict(spos.decode_block(a, block), t)

    def test_object_key_error(self):
        with self.assertRaises(KeyError):
            block = {
                "key": "object missing key",
                "type": "object",
                "blocklist": [
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
        t_dec = "0<=x<5"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_steps_error_steps_names(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 5, 10],
            "steps_names": ["one", "two"],
        }
        t = 1
        a = "0b10"
        with self.assertRaises(ValueError):
            spos.encode_block(t, block)
        with self.assertRaises(ValueError):
            spos.decode_block(a, block)

    def test_steps_error_unordered_steps(self):
        block = {
            "key": "steps",
            "type": "steps",
            "steps": [5, 0, 10],
            "steps_names": ["one", "two"],
        }
        t = 1
        a = "0b10"
        with self.assertRaises(ValueError):
            spos.encode_block(t, block)
        with self.assertRaises(ValueError):
            spos.decode_block(a, block)

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
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_categories_block_2(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "charged"
        a = "0b010"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_categories_block_3(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "full"
        a = "0b011"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

    def test_categories_block_4(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        t = "unknown"
        a = "0b100"
        t_dec = "unknown"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_categories_block_overflow(self):
        block = {
            "key": "categories",
            "type": "categories",
            "categories": ["critical", "low", "charged", "full"],
        }
        a = "0b111"
        t_dec = "error"
        self.assertEqual(spos.decode_block(a, block), t_dec)

    def test_crc_bin(self):
        t = "0b1011110010110010"
        a = "0b10100100"
        b = "0b101111001011001010100100"
        self.assertEqual(spos.create_crc8(t), a)
        self.assertEqual(spos.check_crc8(b), True)

    def test_crc_hex(self):
        t = "0xABCD35"
        a = "0b00101011"
        b = "0xABCD352B"
        self.assertEqual(spos.create_crc8(t), a)
        self.assertEqual(spos.check_crc8(b), True)

    def test_validate_encode_input_types_decorator_keyword_argument(self):
        block = {"key": "boolean encode true", "type": "boolean"}
        block = spos.Block(block)
        block.bin_encode(value=True)

    def test_validate_encode_input_types_decorator_type_error(self):
        block = {"key": "boolean encode true", "type": "boolean"}
        block = spos.Block(block)
        with self.assertRaises(TypeError):
            block.bin_encode(True, "err")
        with self.assertRaises(TypeError):
            block.bin_encode()

    def test_static_value(self):
        static_value = "0b10101"
        block = {
            "key": "binary bin",
            "type": "binary",
            "value": static_value,
            "bits": 5,
        }
        self.assertEqual(spos.encode_block(None, block), static_value)
        self.assertEqual(spos.encode_block("0b11", block), static_value)
        self.assertEqual(spos.encode_block(static_value, block), static_value)

    def test_static_value_mismatch_warning(self):
        static_value = "0b10101"
        block = {
            "key": "binary bin",
            "type": "binary",
            "value": static_value,
            "bits": 5,
        }
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(spos.decode_block("0b11111", block), static_value)
            self.assertEqual(len(w), 1)
            self.assertTrue(
                issubclass(w[-1].category, spos.StaticValueMismatchWarning)
            )
