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


def encode_boolean(value, block):
    """
    Encodes a boolean value according to block specifications.
    """
    return "0b1" if value else "0b0"


def encode_binary(value, block):
    """
    Encodes a binary value according to block specifications.
    """
    bits = block["bits"]
    bit_str = bin(int(value, 2)) if value.startswith("0b") else bin(int(value, 16))
    return truncate_bits(bit_str, bits)


def encode_integer(value, block):
    """
    Encodes an integer value according to block specifications.
    """
    value -= block["offset"]
    bits = block["bits"]
    overflow = 2 ** bits - 1
    bit_str = bin(min([max([value, 0]), overflow]))
    return truncate_bits(bit_str, bits)


def encode_float(value, block):
    """
    Encodes a float value according to block specifications.
    """
    bits = block["bits"]
    upper = block["upper"]
    lower = block["lower"]
    approximation = block["approximation"]
    approx = round
    if approximation == "floor":
        approx = math.floor
    elif approximation == "ceil":
        approx = math.ceil
    overflow = 2 ** bits - 1
    delta = upper - lower
    value = overflow * (value - lower) / delta
    bit_str = bin(approx(min([max([value, 0]), overflow])))
    return truncate_bits(bit_str, bits)


def encode_pad(value, block):
    """
    Encodes a pad value according to block specifications.
    """
    return "0b" + "1" * block["bits"]


def encode_array(value, block, encode_items):
    """
    Encodes an array value according to block specifications.
    """
    message = ""
    length_bits = block["bits"]
    message += encode_integer(len(value), {"bits": length_bits, "offset": 0})
    max_length = min([2 ** length_bits - 1, len(value)])
    items = [block["blocks"].copy() for _, v in zip(range(max_length), value)]
    if len(value) > 0:
        message += "".join([msg[2:] for msg in encode_items(value[:max_length], items)])
    return message


def encode_object(value, block, encode_items):
    """
    Encodes an object value according to block specifications.
    """
    items = block["items"]
    values = [value[item["key"]] for item in items]
    return "0b" + "".join([msg[2:] for msg in encode_items(values, items)])


def encode_string(value, block, rev_alphabeth):
    """
    Encodes an object value according to block specifications.
    """
    message = "0b"
    value = " " * (block["length"] - len(value)) + value
    integer_block = {"bits": 6, "offset": 0}
    custom_alphabeth = block["custom_alphabeth"]
    rev_custom_alphabeth = {val: key for key, val in block["custom_alphabeth"].items()}
    rev_space_map = {" ": 62}  # Maps spaces to +
    for letter in value:
        val = rev_custom_alphabeth.get(
            letter, rev_space_map.get(letter, rev_alphabeth.get(letter, 63))
        )
        message += encode_integer(val, integer_block)[2:]
    return message


def encode_steps(value, block):
    """
    Encodes a steps value according to block specifications.
    """
    steps = block["steps"]
    length = ([2 ** i >= len(steps) for i in range(7)] + [True]).index(True)
    value = ([value >= s for s in steps] + [False]).index(False)
    block = {"bits": length, "offset": 0}
    return encode_integer(value, block)


def encode_categories(value, block):
    """
    Encodes a categories value according to block specifications.
    """
    categories = block["categories"] + ["error"]
    bits = ([2 ** i >= len(categories) for i in range(7)] + [True]).index(True)
    value = value if value in categories else "error"
    value = categories.index(value)
    block = {"bits": bits, "offset": 0}
    return encode_integer(value, block)


def encode_crc8(value, block):
    """
    Encodes a categories value according to block specifications.
    """
    if value.startswith("0x"):
        value = bytes.fromhex(value[2:])
    else:
        value = bytes.fromhex(hex(int(value, 2))[2:])
    hasher = crc8.crc8()
    hasher.update(value)
    crc = bin(int(hasher.hexdigest(), 16))
    crc = "0b" + "{0:0>8}".format(crc[2:])
    return crc


def truncate_bits(bit_str, bits):
    """
    Truncates the `bit_str` to up to `bits`.
    Args:
        bit_str (str): Bit string.
        bits (int): Number of bits to truncate.

    Returns:
        trunc_bit_str (str): Truncated bit string.
    """
    return "0b" + "0" * (bits - len(bit_str) + 2) + bit_str[2 : bits + 2]
