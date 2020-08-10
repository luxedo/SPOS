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
import re

from .blocks import Block
from .exceptions import (
    VersionError,
    PayloadSpecError,
    SpecsVersionError,
    StaticValueMismatchWarning,
)
from .checks import create_crc8, check_crc8
from . import utils


def encode_block(value, block_spec):
    """
    Encodes value according to block specifications.

    Args:
        value: The value to be encoded
        block_spec (dict): Block specification

    Returns:
        message (str): Binary string of the message.
    """
    return Block(block_spec).bin_encode(value)


def decode_block(message, block_spec):
    """
    Encodes value according to block specifications.

    Args:
        value: The value to be encoded
        block (dict): Block specifications

    Returns:
        value: Value of the message.
    """
    return Block(block_spec).bin_decode(message)


def _build_meta_block(payload_spec):
    """
    Performs validations in the meta specification and returns o

    Args:
        payload_spec (dict): Payload specifications.

    Returns:
        version_block (Block): A block to encode the version if
            'meta.encode_version' is set otherwise returns None.
        header_block (BlocK): A block to encode the header values.
        header_static (dict): Static values declared in the header.
    """
    meta_spec = payload_spec.get("meta", {})
    version_block = (
        None
        if not meta_spec.get("encode_version")
        else Block(
            {
                "key": "version",
                "type": "integer",
                "bits": meta_spec["version_bits"],
            }
        )
    )

    header_bl = meta_spec.get("header", [])
    header_encode = [block for block in header_bl if "value" not in block]
    header_block = Block(
        {"key": "header", "type": "object", "blocklist": header_encode}
    )

    header_static = {
        block["key"]: block["value"] for block in header_bl if "value" in block
    }
    return version_block, header_block, header_static


def bin_encode(payload_data, payload_spec):
    """
    Encodes a message from payload_data according to payload_spec.
    Returns the message as a binary string.

    Args:
        payload_data (dict): Payload data.
        payload_spec (dict): Payload specification.

    Returns:
        message (str): Binary string of the message.
    """
    utils.validate_payload_spec(payload_spec)
    message = "0b"

    version_block, header_block, header_static = _build_meta_block(
        payload_spec
    )

    if version_block:
        message += version_block.bin_encode(payload_spec["version"])[2:]
    message += header_block.bin_encode(payload_data)[2:]

    body = payload_spec.get("body", [])
    body_block = Block({"key": "body", "type": "object", "blocklist": body})
    message += body_block.bin_encode(payload_data)[2:]

    message += "0" * (
        (8 - (len(message[2:]) % 8)) % 8
    )  # pad message to fill a byte

    if payload_spec.get("meta", {}).get("crc8"):
        message += create_crc8(message)[2:]

    return message


def bin_decode(message, payload_spec):
    """
    Decodes a binary message according to payload_spec.

    Args:
        message (str): Binary string of the message.
        payload_spec (dict): Payload specification.

    Returns:
        body (dict): Payload data.
        meta (dict): Payload metadata.
    """
    utils.validate_payload_spec(payload_spec)
    meta = {"name": payload_spec["name"], "version": payload_spec["version"]}

    version_block, header_block, header_static = _build_meta_block(
        payload_spec
    )

    if payload_spec.get("meta", {}).get("crc8"):
        meta["crc8"] = check_crc8(message)
        message = message[:-8]

    if version_block:
        msg_version, message = version_block.consume(message)
        if msg_version != meta["version"]:
            raise VersionError(
                f"Versions don't match. Expected {meta['version']}, got {msg_version}."
            )

    header, body_msg = header_block.consume(message)
    header.update(header_static)

    if header:
        meta["header"] = utils.remove_null_values(header)

    body = payload_spec.get("body", {})
    body_block = Block({"key": "body", "type": "object", "blocklist": body})
    body, msg_tail = body_block.consume(body_msg)
    body = utils.remove_null_values(body)
    return {"meta": meta, "body": body}


def encode(payload_data, payload_spec, output="bin"):
    """
    Encodes a message from payload_data according to payload_spec.

    Args:
        payload_data (dict): Payload data.
        payload_spec (dict): Payload specification.
        output (str): Return format (bin, hex or bytes). default: "bin".

    Returns:
        message (bytes): Message.
    """
    message = bin_encode(payload_data, payload_spec)
    if output in ("hex", "bytes"):
        message = message[2:]
        message = "0x" + "".join(
            "{0:02X}".format(int(message[8 * i : 8 * (i + 1)], 2))
            for i in range(len(message) // 8)
        )
        message = (
            message
            if output == "hex"
            else bytes(bytearray.fromhex(message[2:]))
        )
    return message


def decode(message, payload_spec):
    """
    Decodes a message according to payload_spec.

    Args:
        message (bin | hex | bytes): Message.
        payload_spec (dict): Payload specification.

    Returns:
        body (dict): Payload data.
        meta (dict): Payload metadata.
    """
    if isinstance(message, str):
        if not (
            re.match("^0b[01]+$", message)
            or re.match("^0x[0-9a-fA-F]+$", message)
        ):
            raise ValueError(
                "String message must be either a binary string (0b) or an hex string (0x)"
            )
    elif not isinstance(message, bytes):
        raise ValueError(
            f"Message must be either str or bytes, got {type(message)}"
        )
    message = message.strip() if isinstance(message, str) else message
    message = f"0x{message.hex()}" if isinstance(message, bytes) else message
    if message.startswith("0x"):
        bits = len(message[2:]) * 4
        message = bin(int(message, 16))[2:]
        message = "0b" + message.zfill(bits)
    return bin_decode(message, payload_spec)


def decode_from_specs(message, specs):
    """
    Decodes message from an avaliable pool of payload specificaions by
    matching message version with specification version.

    All the payload specifications must have `meta.encode_version` set
    and also the same value for `meta.version_bits`.

    Raises:
        PayloadSpecError: If message version is not in 'specs'
        SpecsVersionError: If names doesn't match or has duplicate versions
        Other Exceptions: For incorrect payload specification syntax.
            see spos.utils.validate_payload_spec and
            block.Block.validate_block_spec_keys

    Args:
        message (bin | hex | bytes): Message.

    Returns:
        body (dict): Payload data.
        meta (dict): Payload metadata.
    """
    utils.validate_specs(specs, match_versions=True)
    for payload_spec in specs:
        try:
            return decode(message, payload_spec)
        except VersionError:
            pass
    raise PayloadSpecError("Message does not match any version in 'specs'.")
