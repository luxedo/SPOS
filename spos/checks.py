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
import crc8


def create_crc8(message):
    """
    Creates an 8-bit CRC.

    Args:
        message (str): Binary or hex string of the message.

    Returns:
        crc8 (str): Binary string of the CRC8 hash for the message.
    """
    if message.startswith("0b"):
        _bytes = len(message[2:]) // 4
        message = "0x" + "{:x}".format(int(message, 2)).rjust(_bytes, "0")
    pad = "0" * (len(message[2:]) % 2)
    message = bytes.fromhex(pad + message[2:])
    hasher = crc8.crc8()
    hasher.update(message)
    crc = bin(int(hasher.hexdigest(), 16))
    crc = "0b" + "{0:0>8}".format(crc[2:])
    return crc


def check_crc8(message):
    """
    Checks if the message is valid. The last byte of the message must
    be the CRC8 hash of the previous data.

    Args:
        message (str): Binary or hex string of the message.

    Returns:
        valid (bool): True if the message is valid.
    """
    if message.startswith("0x"):
        bits = len(message[2:]) * 4
        message = "0b" + "{0}".format(bin(int(message, 16))[2:]).rjust(
            bits, "0"
        )
    crc_dec = "0b" + message[-8:]
    message = message[:-8]
    return create_crc8(message) == crc_dec
