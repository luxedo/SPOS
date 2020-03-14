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
from .encoders import truncate_bits, encode_crc8


def decode_boolean(message, block):
    """
    Decodes a boolean value according to block specifications.
    """
    return message == "0b1"


def decode_binary(message, block):
    """
    Decodes a binary value according to block specifications.
    """
    return truncate_bits(message, block["settings"]["bits"])


def decode_integer(message, block):
    """
    Decodes an integer value according to block specifications.
    """
    return int(message, 2) + block["settings"]["offset"]


def decode_float(message, block):
    """
    Decodes a float value according to block specifications.
    """
    bits = block["settings"]["bits"]
    upper = block["settings"]["upper"]
    lower = block["settings"]["lower"]
    delta = upper - lower
    overflow = 2 ** bits - 1
    return int(message, 2) * delta / overflow + lower


def decode_array(message, block, decode_block, decode_message):
    """
    Decodes an array value according to block specifications.
    """
    inner_block = block["settings"]["blocks"]
    length_bits = block["settings"]["bits"]
    length = decode_block(
        message[: length_bits + 2],
        {"name": "array lenght", "type": "integer", "settings": {"bits": length_bits}},
    )
    values = []
    if inner_block["type"] == "array":
        raise ValueError("Can't use a nested array.")
    items = [inner_block for i in range(length)]
    if length > 0:
        return decode_message("0b" + message[length_bits + 2 :], items)
    return []


def decode_object(message, block, decode_message):
    """
    Decodes an array value according to block specifications.
    """
    items = block["settings"]["items"]
    keys = [item["name"] for item in items]
    values = decode_message(message, items)
    return dict(zip(keys, values))


def decode_string(message, block, alphabeth, decode_message):
    """
    Decodes a string value according to block specifications.
    """
    integer_block = {
        "type": "integer",
        "name": "letter",
        "settings": {"bits": 6, "offset": 0},
    }
    custom_alphabeth = block["settings"]["custom_alphabeth"]
    items = [integer_block for _ in range(block["settings"]["length"])]
    value = "".join(
        [custom_alphabeth.get(i, alphabeth[i]) for i in decode_message(message, items)]
    )
    return value


def decode_steps(message, block):
    """
    Decodes a steps value according to block specifications.
    """
    steps = block["settings"]["steps"]
    steps_names = block["settings"]["steps_names"]
    if len(steps_names) == 0:
        steps_names = (
            ["x<{0}".format(steps[0])]
            + ["{0}<x<={1}".format(l, u) for l, u in zip(steps, steps[1:])]
            + ["x>={0}".format(steps[0])]
        )
    if len(steps_names) != len(steps) + 1:
        raise ValueError(
            "'steps_names' for block {0} has to have length 1 + len(steps).".format(
                block["name"]
            )
        )
    length = ([2 ** i >= len(steps) for i in range(7)] + [True]).index(True)
    integer_block = {
        "type": "integer",
        "settings": {"bits": length, "offset": 0},
    }
    value = decode_integer(message, integer_block)
    return steps_names[value]


def decode_categories(message, block):
    """
    Decodes a categories value according to block specifications.
    """
    categories = block["settings"]["categories"] + ["error"]
    bits = ([2 ** i >= len(categories) for i in range(7)] + [True]).index(True)
    integer_block = {
        "type": "integer",
        "settings": {"bits": bits, "offset": 0},
    }
    value = decode_integer(message, integer_block)
    return categories[value]


def decode_crc8(message, block):
    """
    Decodes a crc value according to block specifications.
    """
    crc_dec = "0b" + message[-8:]
    message = message[:-8]
    crc_enc = encode_crc8(message, block)
    return crc_dec == crc_enc
