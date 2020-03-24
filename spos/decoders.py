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
from .encoders import truncate_bits


def decode_boolean(message, block):
    """
    Decodes a boolean value according to block specifications.
    """
    return message == "0b1"


def decode_binary(message, block):
    """
    Decodes a binary value according to block specifications.
    """
    return truncate_bits(message, block["bits"])


def decode_integer(message, block):
    """
    Decodes an integer value according to block specifications.
    """
    return int(message, 2) + block["offset"]


def decode_float(message, block):
    """
    Decodes a float value according to block specifications.
    """
    bits = block["bits"]
    upper = block["upper"]
    lower = block["lower"]
    delta = upper - lower
    overflow = 2 ** bits - 1
    return int(message, 2) * delta / overflow + lower


def decode_pad(message, block):
    """
    Decodes a pad value according to block specifications.
    """
    return None


def decode_array(message, block, decode_message):
    """
    Decodes an array value according to block specifications.
    """
    inner_block = block["blocks"]
    length_bits = block["bits"]
    length = decode_integer(
        message[: length_bits + 2], {"bits": length_bits, "offset": 0},
    )
    values = []
    items = [inner_block for i in range(length)]
    if length > 0:
        return decode_message("0b" + message[length_bits + 2 :], items)
    return []


def decode_object(message, block, decode_message):
    """
    Decodes an array value according to block specifications.
    """
    items = block["items"]
    keys = [item["key"] for item in items]
    values = decode_message(message, items)
    return dict(zip(keys, values))


def decode_string(message, block, alphabeth):
    """
    Decodes a string value according to block specifications.
    """
    _alphabeth = alphabeth.copy()
    _alphabeth.update(block["custom_alphabeth"])
    value = "".join(
        [
            _alphabeth.get(index)
            for index in [
                decode_integer(
                    message[2:][6 * i : 6 * (i + 1)], {"bits": 6, "offset": 0}
                )
                for i in range(len(message) // 6)
            ]
        ]
    )
    return value


def decode_steps(message, block):
    """
    Decodes a steps value according to block specifications.
    """
    steps = block["steps"]
    steps_names = block["steps_names"]
    bits = math.ceil(math.log(len(block["steps_names"]), 2))
    value = decode_integer(message, {"bits": bits, "offset": 0,})
    return steps_names[value]


def decode_categories(message, block):
    """
    Decodes a categories value according to block specifications.
    """
    categories = block["categories"] + ["error"]
    bits = math.ceil(math.log(len(block["categories"]), 2))
    value = decode_integer(message, {"bits": bits, "offset": 0,})
    return categories[value]
