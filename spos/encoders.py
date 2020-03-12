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


def encode_boolean(value, block):
    """
    Encodes a boolean value according to block specifications.
    """
    return "0b1" if value else "0b0"


def encode_binary(value, block):
    """
    Encodes a binary value according to block specifications.
    """
    bits = block["settings"]["bits"]
    bit_str = bin(int(value, 2)) if value.startswith("0b") else bin(int(value, 16))
    return truncate_bits(bit_str, bits)


def encode_integer(value, block):
    """
    Encodes an integer value according to block specifications.
    """
    value -= block["settings"]["offset"]
    bits = block["settings"]["bits"]
    overflow = 2 ** bits - 1
    bit_str = bin(min([max([value, 0]), overflow]))
    return truncate_bits(bit_str, bits)


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
    return truncate_bits(bit_str, bits)


def encode_array(value, block, encode_block, encode_items):
    """
    Encodes an array value according to block specifications.
    """
    message = ""
    length_bits = block["settings"]["bits"]
    length_block = {
        "name": "array length",
        "type": "integer",
        "settings": {"bits": length_bits},
    }
    message += encode_block(len(value), length_block)
    max_length = min([2 ** length_bits - 1, len(value)])
    items = [
        block["settings"]["blocks"].copy() for _, v in zip(range(max_length), value)
    ]
    message += encode_items(value, items)[2:]
    return message


def encode_object(value, block, encode_items):
    """
    Encodes an object value according to block specifications.
    """
    items = block["settings"]["items"]
    values = [value[item["name"]] for item in items]
    return encode_items(values, items)


def encode_string(value, block, rev_alphabeth):
    """
    Encodes an object value according to block specifications.
    """
    message = "0b"
    value = (" " * (block["settings"]["length"] - len(value)) + value).replace(" ", "+")
    block = {"type": "integer", "settings": {"bits": 6, "offset": 0}}
    for letter in value:
        val = rev_alphabeth.get(letter, 63)
        message += encode_integer(val, block)[2:]
    return message


def encode_steps(value, block):
    """
    Encodes a steps value according to block specifications.
    """
    steps = block["settings"]["steps"]
    length = ([2 ** i >= len(steps) for i in range(7)] + [True]).index(True)
    value = ([value >= s for s in steps] + [False]).index(False)
    block = {"type": "integer", "settings": {"bits": length, "offset": 0}}
    return encode_integer(value, block)


def encode_categories(value, block):
    """
    Encodes a categories value according to block specifications.
    """
    categories = block["settings"]["categories"] + ["error"]
    length = ([2 ** i >= len(categories) for i in range(7)] + [True]).index(True)
    value = value if value in categories else "error"
    value = categories.index(value)
    block = {"type": "integer", "settings": {"bits": length, "offset": 0}}
    return encode_integer(value, block)


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
