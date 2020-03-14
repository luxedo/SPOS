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
import copy
from string import ascii_uppercase, ascii_lowercase, digits
from . import encoders, decoders, validators


TYPES_SETTINGS = {
    "boolean": {},
    "binary": {"required": {"bits": int}},
    "integer": {
        "required": {"bits": int},
        "optional": {"offset": {"type": int, "default": 0}},
    },
    "float": {
        "required": {"bits": int},
        "optional": {
            "lower": {"type": (int, float), "default": 0},
            "upper": {"type": (int, float), "default": 1},
            "approximation": {
                "type": (str),
                "default": "round",
                "choices": ["round", "floor", "ceil"],
            },
        },
    },
    "pad": {"required": {"bits": int},},
    "array": {"required": {"bits": int, "blocks": "blocks"},},
    "object": {"required": {"items": "items"}},
    "string": {
        "required": {"length": int},
        "optional": {"custom_alphabeth": {"type": (dict), "default": {}}},
    },
    "steps": {
        "required": {"steps": list},
        "optional": {"steps_names": {"type": list, "default": []}},
    },
    "categories": {"required": {"categories": list},},
    "crc8": {},
}

TYPES = {
    "boolean": {
        "input": (bool, int),
        "encoder": encoders.encode_boolean,
        "decoder": decoders.decode_boolean,
    },
    "binary": {
        "input": str,
        "validator": validators.validate_binary,
        "encoder": encoders.encode_binary,
        "decoder": decoders.decode_binary,
    },
    "integer": {
        "input": int,
        "encoder": encoders.encode_integer,
        "decoder": decoders.decode_integer,
    },
    "float": {
        "input": (int, float),
        "encoder": encoders.encode_float,
        "decoder": decoders.decode_float,
    },
    "pad": {
        "encoder": lambda value, block: "0b" + "1" * block["settings"]["bits"],
        "decoder": lambda message, block: None,
    },
    # We inject dependencies here to keep the functions with the same interface
    "array": {
        "input": list,
        "encoder": lambda value, block: encoders.encode_array(
            value, block, encode_block, encode_items
        ),
        "decoder": lambda message, block: decoders.decode_array(
            message, block, decode_block, decode_message
        ),
    },
    "object": {
        "input": dict,
        "encoder": lambda value, block: encoders.encode_object(
            value, block, encode_items
        ),
        "decoder": lambda message, block: decoders.decode_object(
            message, block, decode_message
        ),
    },
    "string": {
        "input": str,
        "encoder": lambda value, block: encoders.encode_string(
            value, block, BASE64_REV_ALPHABETH
        ),
        "decoder": lambda value, block: decoders.decode_string(
            value, block, BASE64_ALPHABETH, decode_message
        ),
    },
    "steps": {
        "input": (int, float),
        "encoder": encoders.encode_steps,
        "decoder": decoders.decode_steps,
    },
    "categories": {
        "input": str,
        "encoder": encoders.encode_categories,
        "decoder": decoders.decode_categories,
    },
    "crc8": {
        "input": str,
        "validator": validators.validate_crc8,
        "encoder": encoders.encode_crc8,
        "decoder": decoders.decode_crc8,
    },
}

BASE64_ALPHABETH = dict(enumerate(ascii_uppercase + ascii_lowercase + digits + "+/"))
BASE64_REV_ALPHABETH = {val: key for key, val in BASE64_ALPHABETH.items()}


def validate_block(block, parent="root"):
    """
    Validates block specification.

    Args:
        block (dict): Block specification.

    Raises:
        KeyError, ValueError, TypeError: For non conformant blocks.
    """
    # Check name
    if "name" not in block:
        raise KeyError("Block '{0}: {1}' must have 'name'.".format(parent, block))
    name = block["name"]
    if not isinstance(name, str):
        raise TypeError(
            "Block '{0}: {1}' 'name' must be a string.".format(parent, name)
        )

    # Check type
    if "type" not in block:
        raise KeyError("Block '{0}: {1}' must have 'type'.".format(parent, name))
    b_type = block["type"]
    if block["type"] not in TYPES:
        raise ValueError(
            "Block '{0}: {1}' has an unknown 'type' {2}.".format(parent, name, b_type)
        )
    type_settings = TYPES_SETTINGS[block["type"]]

    # Check required settings
    for s_name, tp in type_settings.get("required", {}).items():
        if s_name not in block.get("settings", {}):
            raise KeyError(
                "Block '{0}: {1}' requires setting '{2}'.".format(parent, name, s_name)
            )
        if tp == "blocks":
            validate_block(
                block["settings"]["blocks"], "{0}: {1}".format(parent, block["name"])
            )
        elif tp == "items":
            for b in block["settings"]["items"]:
                validate_block(b, "{0}: {1}".format(parent, block["name"]))
        elif not isinstance(block["settings"][s_name], tp):
            raise TypeError(
                "Block '{0}: {1}' setting '{2}' has wrong type '{3}' instead of '{4}'.".format(
                    parent, name, s_name, type(block["settings"][s_name]), tp
                )
            )

    # Check optional settings
    for s_name, opts in type_settings.get("optional", {}).items():
        if not s_name in block["settings"]:
            block["settings"][s_name] = opts["default"]
        if not isinstance(block["settings"][s_name], opts["type"]):
            raise TypeError(
                "Block '{0}: {1}' optional setting '{2}' has wrong type '{3}' instead of '{4}'.".format(
                    parent, name, s_name, type(block["settings"][s_name]), opts["type"]
                )
            )

    # Check for unexpected settings
    allowed_settings = list(type_settings.get("optional", {}).keys()) + list(
        type_settings.get("required", {}).keys()
    )
    for key in block.get("settings", {}):
        if key not in allowed_settings and key != "bits":
            raise KeyError(
                "Block '{0}' settings has an unexpected key '{1}'.".format(
                    block["name"], key
                )
            )


def encode_block(value, block):
    """
    Encodes value according to block specifications.

    Args:
        value: The value to be encoded
        block (dict): Block specifications

    Returns:
        message (str): Binary string of the message.
    """
    validate_block(block)
    type_conf = TYPES[block["type"]]
    if "input" in type_conf:
        validators.validate_input(value, type_conf["input"], block)
    if "validator" in type_conf:
        type_conf["validator"](value, block)
    return type_conf["encoder"](value, block)


def decode_block(message, block):
    """
    Encodes value according to block specifications.

    Args:
        value: The value to be encoded
        block (dict): Block specifications

    Returns:
        value: Value of the message.
        bits (int): Number of consumed bits in the operation.
    """
    validate_block(block)
    type_conf = TYPES[block["type"]]
    return type_conf["decoder"](message, block)


def encode_items(values, items):
    """
    Encodes a list of blocks.

    Args:
        values (list): The list of values to encode.
        items (list): A list of blocks.

    Returns:
        message (str): Binary string of the message.

    Raises:
        ValueError: If the length of value and items differ or if any
            of the arrays is empty
    """
    messages = []
    if len(values) != len(items):
        raise ValueError("Arrays 'values' and 'items' differ.")
    if len(values) == 0:
        raise ValueError("Empty 'values' array")
    if len(items) == 0:
        raise ValueError("Empty 'items' array")
    for value, block in zip(values, items):
        messages.append(encode_block(value, block))
    return messages


def decode_items(messages, items):
    """
    Decodes list of blocks.

    Args:
        messages (list): The list of messages to decode
        items (list): A list of blocks.

    Returns:
        values (list): The list of values for the blocks.
    """
    values = []
    acc_message = "0b"
    if len(messages) != len(items):
        raise ValueError("Arrays 'messages' and 'items' differ.")
    if len(messages) == 0:
        raise ValueError("Empty 'messages' array")
    if len(items) == 0:
        raise ValueError("Empty 'items' array")
    for message, block in zip(messages, items):
        acc_message += message[2:]
        if block["type"] == "crc8":
            values.append(decode_block(acc_message, block))
        else:
            values.append(decode_block(message, block))
    return values


def decode_message(message, items):
    """
    Decodes a concatenated message of multiple items.

    Args:
        message (str): Message to decode
        items (list): A list of blocks.

    Returns:
        values (list): The list of values for the blocks.
    """
    messages = split_messages(message, items)
    return decode_items(messages, items)


def split_messages(message, items):
    """
    Receives a concatenated message and breaks it into a list of
    messages according to items.

    Args:
        message (str): Binary string of the concatenated messages.
        items (list): A list of blocks.

    Returns:
        messages (list): A list of binary strings.
    """
    messages = []
    message = message[2:]
    for block in items:
        bits = accumulate_bits(message, block)
        messages.append("0b" + message[:bits])
        message = message[bits:]
    return messages


def accumulate_bits(message, block):
    """
    Calculates the bits of the block in the message.

    Args:
        message (str): Binary string of the message.
        block (dict): Block specifications

    Returns:
        bits (int): Number of bits in the block.
    """
    acc = 0
    if "bits" in block.get("settings", {}):
        acc += block["settings"]["bits"]
    if block["type"] == "boolean":
        acc = 1
    elif block["type"] == "crc8":
        acc = 8
    elif block["type"] == "string":
        acc += block["settings"]["length"] * 6
    elif block["type"] == "array":
        bits = block["settings"]["bits"]
        length = decoders.decode_integer(
            message[:bits], {"settings": {"bits": bits, "offset": 0}}
        )
        acc += length * accumulate_bits(message[:bits], block["settings"]["blocks"])
    elif block["type"] == "object":
        for b in block["settings"]["items"]:
            bits = accumulate_bits(message, b)
            message = message[bits:]
            acc += bits
    elif block["type"] == "steps":
        bits = (
            [2 ** i >= (len(block["settings"]["steps_names"])) for i in range(7)]
            + [True]
        ).index(True)
        acc += bits
    elif block["type"] == "categories":
        bits = (
            [2 ** i >= (len(block["settings"]["categories"]) + 1) for i in range(7)]
            + [True]
        ).index(True)
        acc += bits
    return acc


def encode(payload_data, payload_spec):
    """
    Encodes a message from payload_data according to payload_spec.
    Returns the message as a binary string.

    Args:
        payload_data (dict): The list of values to encode.
        payload_spec (dict): Payload specifications.

    Returns:
        message (str): Binary string of the message.
    """
    values = []
    for block in payload_spec["items"]:
        if block["type"] in ["crc8", "pad"]:
            values.append("0xff")
            continue
        if "key" in block and "value" in block:
            raise KeyError(
                "Block '{0}' must have only one key or value, not both.".format(block)
            )
        if "key" not in block and "value" not in block:
            raise KeyError(
                "Block '{0}' must have either key or value, not neither.".format(block)
            )
        if "value" in block:
            values.append(block["value"])
        else:
            values.append(payload_data[block["key"]])

    messages = encode_items(values, payload_spec["items"])
    partial_msg = "0b"
    for idx, block in enumerate(payload_spec["items"]):
        if block["type"] == "crc8":
            messages[idx] = encode_block(partial_msg, block)
        partial_msg += messages[idx][2:]
    return partial_msg


def decode(message, payload_spec):
    """
    Decodes a binary message according to payload_spec.

    Args:
        message (str): Binary string of the message.
        payload_spec (dict): Payload specifications.

    Returns:
        payload_data (dict): Payload data.
    """
    items = payload_spec["items"]
    values = decode_message(message, items)
    keys = [block["name"] for block in items]
    payload_data = dict(zip(keys, values))
    for key, block in zip(keys, items):
        if block["type"] == "pad" and key in payload_data:
            del payload_data[key]
    return payload_data


def hex_encode(payload_data, payload_spec):
    """
    Encodes a message from payload_data according to payload_spec.
    Returns the message as an hex string.

    Args:
        payload_data (dict): The list of values to encode.
        payload_spec (dict): Payload specifications.

    Returns:
        message (str): Binary string of the message.
    """
    message = encode(payload_data, payload_spec)
    message = message[2:] + "0" * (8 - (len(message) - 2) % 8)
    output = "0x"
    for i in range(len(message) // 8):
        output += "{0:02X}".format(int(message[8 * i : 8 * (i + 1)], 2))
    return output


def hex_decode(message, payload_spec):
    """
    Decodes an hex message according to payload_spec.

    Args:
        message (str): Hex string of the message.
        payload_spec (dict): Payload specifications.

    Returns:
        payload_data (dict): Payload data.
    """
    bits = len(message[2:]) * 4
    message = bin(int(message, 16))[2:]
    message = "0b" + message.zfill(bits)
    return decode(message, payload_spec)
