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
