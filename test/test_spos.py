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
from spos import utils
import spos


class TestBlock(unittest.TestCase):
    def assertClose(self, val1, val2, delta=0.01):
        self.assertTrue(abs(val1 - val2) < delta)

    def test_boolean_block(self):
        # block = spos.Block({"name": "boolean test true", "type": "boolean"})
        t = True
        a = "0b1"
        self.assertEqual(
            spos.encode_block(t, {"name": "boolean encode true", "type": "boolean"}), a,
        )
        self.assertEqual(
            spos.decode_block(a, {"name": "boolean decode true", "type": "boolean"}), t,
        )

        t = False
        a = "0b0"
        self.assertEqual(
            spos.encode_block(t, {"name": "boolean false", "type": "boolean"}), a,
        )
        self.assertEqual(
            spos.decode_block(a, {"name": "boolean decode false", "type": "boolean"}),
            t,
        )
        with self.assertRaises(TypeError):
            t = "fail"
            self.assertEqual(
                spos.encode_block(t, {"name": "boolean error", "type": "boolean"}), a,
            )

    def test_binary_block(self):
        block = {"name": "binary test bin", "type": "binary", "settings": {"bits": 10}}
        t = "0b100101"
        a = "0b0000100101"
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), a)
        self.assertEqual(spos.encode_block(a, block), a)

        with self.assertRaises(ValueError):
            spos.encode_block(
                "0xfail",
                {
                    "name": "binary test bin error",
                    "type": "binary",
                    "settings": {"bits": 10},
                },
            )

        block = {
            "name": "binary test large hex",
            "type": "binary",
            "settings": {"bits": 10},
        }
        t = "0xdeadbeef"
        a = bin(int(t, 16))[:12]
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), a)

        block = {
            "name": "binary test small hex",
            "type": "binary",
            "settings": {"bits": 10},
        }
        t = "0xff"
        a = utils.truncate_bits(bin(int(t, 16))[:12], block["settings"]["bits"])
        self.assertEqual(spos.encode_block(t, block), a)

        with self.assertRaises(ValueError):
            block = {
                "name": "binary test hex fail",
                "type": "binary",
                "settings": {"bits": 10},
            }
            spos.encode_block("0xfail", block)

        with self.assertRaises(TypeError):
            block = {
                "name": "binary test type fail",
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
                "name": "integer test fail",
                "type": "integer",
                "settings": {"bits": 6},
            }
            spos.encode_block("fail", block)

        t = 120
        a = "0b010100"
        block = {
            "name": "integer test offset",
            "type": "integer",
            "settings": {"bits": 6, "offset": 100},
        }
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        t = -10
        a = "0b000000"
        block = {
            "name": "integer test underflow",
            "type": "integer",
            "settings": {"bits": 6},
        }
        self.assertEqual(spos.encode_block(t, block), a)

        t = 128
        a = "0b111111"
        block = {
            "name": "integer test overflow",
            "type": "integer",
            "settings": {"bits": 6},
        }
        self.assertEqual(spos.encode_block(t, block), a)

    def test_float_block(self):
        t = 0.66
        a = "0b10"
        block = {"name": "float test", "type": "float", "settings": {"bits": 2}}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

        with self.assertRaises(TypeError):
            block = {
                "name": "float test fail",
                "type": "float",
                "settings": {"bits": 4},
            }
            spos.encode_block("fail", block)

        t = 0.66
        a = "0b01"
        t_dec = 0.33
        block = {
            "name": "float test approximation floor",
            "type": "float",
            "settings": {"bits": 2, "approximation": "floor"},
        }
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t_dec)

        t = 0.34
        a = "0b10"
        t_dec = 0.66
        block = {
            "name": "float test approximation ceil",
            "type": "float",
            "settings": {"bits": 2, "approximation": "ceil"},
        }
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t_dec)

        t = 13
        a = "0b01101"
        block = {
            "name": "float test upper",
            "type": "float",
            "settings": {"bits": 5, "upper": 31},
        }
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

        t = -1
        a = "0b101"
        block = {
            "name": "float test upper",
            "type": "float",
            "settings": {"bits": 3, "lower": -6},
        }
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertClose(spos.decode_block(a, block), t)

        t = -10
        a = "0b000000"
        block = {
            "name": "float test underflow",
            "type": "float",
            "settings": {"bits": 6},
        }
        self.assertEqual(spos.encode_block(t, block), a)

        t = 10
        a = "0b111111"
        block = {
            "name": "float test overflow",
            "type": "float",
            "settings": {"bits": 6},
        }
        self.assertEqual(spos.encode_block(t, block), a)

    def test_pad_block(self):
        t = None
        a = "0b11"
        block = {"name": "pad test", "type": "pad", "settings": {"bits": 2}}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)

        t = None
        a = "0b111111"
        block = {"name": "pad test", "type": "pad", "settings": {"bits": 6}}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(a, block), t)
        
    def test_crc(self):
        t = '0b1011110010110010'
        a = '0b10100100'
        b = '0b101111001011001010100100'
        block = {"name": "crc BIN test", "type": "crc8"}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(b, block), True)

        t = '0xABCD35'
        a = '0b00101011'
        b = '0b10101011110011010011010100101011'
        block = {"name": "crc HEX test", "type": "crc8"}
        self.assertEqual(spos.encode_block(t, block), a)
        self.assertEqual(spos.decode_block(b, block), True)
