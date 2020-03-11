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
from . import utils

def decode_boolean(message, block):
    """
    Decodes a boolean value according to block specifications.
    """
    return message == "0b1"


def decode_binary(message, block):
    """
    Decodes a binary value according to block specifications.
    """
    return utils.truncate_bits(message, block["settings"]["bits"])


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


def decode_array(message, block):
    """
    Decodes an array value according to block specifications.
    """
    bits = block["settings"]["bits"]
    upper = block["settings"]["upper"]
    lower = block["settings"]["lower"]
    delta = upper - lower
    overflow = 2 ** bits - 1
    return int(message, 2) * delta / overflow + lower
