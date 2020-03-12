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


def validate_type(value, v_type, block):
    """
    Validates the correct type for the block value.
    """
    if not isinstance(value, v_type):
        raise TypeError(
            "Value for block '{0}' must be of type '{1}', not '{2}'".format(
                block["name"], v_type, type(value)
            )
        )


def validate_binary(value, block):
    """
    Validates a binary block value.
    """
    if not (value.startswith("0b") or value.startswith("0x")):
        raise TypeError(
            "Value for block '{0}' must be a binary string or an hex string.".format(
                block["name"]
            )
        )
