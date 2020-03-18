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


TYPES_KEYS = {
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
    "pad": {"encoder": encoders.encode_pad, "decoder": decoders.decode_pad},
    # Inject dependencies with lambda to keep the functions with the same interface
    "array": {
        "input": list,
        "encoder": lambda value, block: encoders.encode_array(
            value, block, encode_items
        ),
        "decoder": lambda message, block: decoders.decode_array(
            message, block, decode_message
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
    # Check key
    if "key" not in block:
        raise KeyError("Block '{0}: {1}' must have 'key'.".format(parent, block))
    key = block["key"]
    if not isinstance(key, str):
        raise TypeError("Block '{0}: {1}' 'key' must be a string.".format(parent, key))

    # Check type
    if "type" not in block:
        raise KeyError("Block '{0}: {1}' must have 'type'.".format(parent, key))
    b_type = block["type"]
    if block["type"] not in TYPES:
        raise ValueError(
            "Block '{0}: {1}' has an unknown 'type' {2}.".format(parent, key, b_type)
        )
    type_keys = TYPES_KEYS[block["type"]]

    # Check required keys
    for s_key, tp in type_keys.get("required", {}).items():
        if tp == "blocks":
            validate_block(block["blocks"], "{0}: {1}".format(parent, block["key"]))
        elif tp == "items":
            for b in block["items"]:
                validate_block(b, "{0}: {1}".format(parent, block["key"]))
        elif not isinstance(block[s_key], tp):
            raise TypeError(
                "Block '{0}: {1}' setting '{2}' has wrong type '{3}' instead of '{4}'.".format(
                    parent, key, s_key, type(block[s_key]), tp
                )
            )

    # Check optional keys
    for s_key, opts in type_keys.get("optional", {}).items():
        if s_key in block and not isinstance(block[s_key], opts["type"]):
            raise TypeError(
                "Block '{0}: {1}' optional setting '{2}' has wrong type '{3}' instead of '{4}'.".format(
                    parent, key, s_key, type(block[s_key]), opts["type"]
                )
            )

    # Check for unexpected keys
    allowed_keys = (
        list(type_keys.get("optional", {}).keys())
        + list(type_keys.get("required", {}).keys())
        + ["key", "type", "value", "bits"]
    )
    for key in block:
        if key not in allowed_keys:
            raise KeyError(
                "Block '{0}' block has an unexpected key '{1}'.".format(
                    block["key"], key
                )
            )


def fill_defaults(block):
    """
    Fills the default values for optional valeus in `block`.

    Args:
        block (dict): The block to fill.

    Returns:
        block (dict): A copy of the block with the optional values.
    """
    block = copy.deepcopy(block)
    type_keys = TYPES_KEYS[block["type"]]
    for s_key, opts in type_keys.get("optional", {}).items():
        if not s_key in block:
            block[s_key] = opts["default"]
    return block


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
    block = fill_defaults(block)
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
    block = fill_defaults(block)
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
    if "bits" in block:
        acc += block["bits"]
    if block["type"] == "boolean":
        acc = 1
    elif block["type"] == "crc8":
        acc = 8
    elif block["type"] == "string":
        acc += block["length"] * 6
    elif block["type"] == "array":
        bits = block["bits"]
        length = decoders.decode_integer(message[:bits], {"bits": bits, "offset": 0})
        acc += length * accumulate_bits(message[:bits], block["blocks"])
    elif block["type"] == "object":
        for b in block["items"]:
            bits = accumulate_bits(message, b)
            message = message[bits:]
            acc += bits
    elif block["type"] == "steps":
        bits = (
            [2 ** i >= (len(block["steps_names"])) for i in range(7)] + [True]
        ).index(True)
        acc += bits
    elif block["type"] == "categories":
        bits = (
            [2 ** i >= (len(block["categories"]) + 1) for i in range(7)] + [True]
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
    keys = [block["key"] for block in items]
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
