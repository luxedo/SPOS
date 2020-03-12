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
import math
import crc8

from . import utils


def encode_boolean(value, block):
    """
    Encodes a boolean value according to block specifications.
    """
    return "0b1" if value else "0b0"


def encode_binary(value, block):
    """
    Encodes a binary value according to block specifications.
    """
    value = value
    bits = block["settings"]["bits"]
    bit_str = bin(int(value, 2)) if value.startswith("0b") else bin(int(value, 16))
    return utils.truncate_bits(bit_str, bits)


def encode_integer(value, block):
    """
    Encodes an integer value according to block specifications.
    """
    value -= block["settings"]["offset"]
    bits = block["settings"]["bits"]
    overflow = 2 ** bits - 1
    bit_str = bin(min([max([value, 0]), overflow]))
    return utils.truncate_bits(bit_str, bits)


def encode_float(value, block):
    """
    Encodes a float value according to block specifications.
    """
    bits = block["settings"]["bits"]
    upper = block["settings"]["upper"]
    lower = block["settings"]["lower"]
    approximation = block["settings"]["approximation"]
    approx = round
    if approximation == "floor":
        approx = math.floor
    elif approximation == "ceil":
        approx = math.ceil

    overflow = 2 ** bits - 1
    delta = upper - lower
    value = overflow * (value - lower) / delta
    bit_str = bin(approx(min([max([value, 0]), overflow])))
    return utils.truncate_bits(bit_str, bits)


def encode_array(value, block):
    """
    Encodes an array value according to block specifications.
    """
    bits = block["settings"]["bits"]
    upper = block["settings"]["upper"]
    lower = block["settings"]["lower"]
    approximation = block["settings"]["approximation"]
    approx = round
    if approximation == "floor":
        approx = math.floor
    elif approximation == "ceil":
        approx = math.ceil

    overflow = 2 ** bits - 1
    delta = upper - lower
    value = overflow * (value - lower) / delta
    bit_str = bin(approx(min([max([value, 0]), overflow])))
    return utils.truncate_bits(bit_str, bits)

def encode_crc(value, block):  ## message validation: validate.binary()
    """
    Creates an 8-bit CRC of the message.

    Args:
        message (str): Message string, in BIN ("0b...") or HEX ("0x...") format

    Return:
        crc8 (bin str): 8-bit CRC
    """

    if value.startswith("0x"):
        value = bytes.fromhex(value[2:])
    else:
        value = bytes.fromhex(hex(int(value, 2))[2:])
    hasher = crc8.crc8()
    hasher.update(value)
    crc = bin(int(hasher.hexdigest(), 16))
    crc = '0b' + '{0:0>8}'.format(crc[2:])
    return crc


