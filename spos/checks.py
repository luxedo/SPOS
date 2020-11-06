"""
SPOS - Small Payload Object Serializer
MIT License

Copyright (c) 2020 [Luiz Eduardo Amaral](luizamaral306@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import crc8

from .typing import Message


def create_crc8(message: str) -> str:
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
    message_bytes = bytes.fromhex(pad + message[2:])
    hasher = crc8.crc8()
    hasher.update(message_bytes)
    crc = bin(int(hasher.hexdigest(), 16))
    crc = "0b" + "{0:0>8}".format(crc[2:])
    return crc


def check_crc8(message: str) -> bool:
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
