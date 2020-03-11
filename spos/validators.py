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


def validate_boolean(value, name):
    """
    Validates a boolean block.
    """
    if not isinstance(value, bool):
        raise TypeError(
            "Value for block '{0}' must be a boolean, not '{1}'".format(
                name, type(value)
            )
        )


def validate_binary(value, name):
    """
    Validates a binary block.
    """
    if not isinstance(value, str):
        raise TypeError(
            "Value for block '{0}' must be a string, not '{1}.'".format(
                name, type(value)
            )
        )
    if not (value.startswith("0b") or value.startswith("0x")):
        raise TypeError(
            "Value for block '{0}' must be a binary string or an hex string.".format(
                name
            )
        )


def validate_integer(value, name):
    """
    Validates a float block.
    """
    if not isinstance(value, int):
        raise TypeError(
            "Value for block '{0}' must be an 'int', not '{1}.'".format(
                name, type(value)
            )
        )


def validate_float(value, name):
    """
    Validates a float block.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            "Value for block '{0}' must be an 'int' or 'float', not '{1}.'".format(
                name, type(value)
            )
        )


def validate_array(value, name):
    """
    Validates an array block.
    """
    if not (isinstance(value, int) or isinstance(value, float)):
        raise TypeError(
            "Value for block '{0}' must be an 'int' or 'float', not '{1}.'".format(
                name, type(value)
            )
        )
