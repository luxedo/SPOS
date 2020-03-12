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


BASE64_ALPHABETH = {
    idx: val
    for idx, val in enumerate(ascii_uppercase + ascii_lowercase + digits + "+/")
}
BASE64_REV_ALPHABETH = {val: key for key, val in BASE64_ALPHABETH.items()}

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
            message, block, decode_block
        ),
    },
    "object": {
        "input": dict,
        "encoder": lambda value, block: encoders.encode_object(
            value, block, encode_items
        ),
        "decoder": lambda message, block: decoders.decode_object(
            message, block, decode_items
        ),
    },
    "string": {
        "input": str,
        "encoder": lambda value, block: encoders.encode_string(
            value, block, BASE64_REV_ALPHABETH
        ),
        "decoder": lambda value, block: decoders.decode_string(
            value, block, BASE64_ALPHABETH, decode_items
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
}


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
                    parent, name, s_name, type(block["settings"][s_name]), tp
                )
            )

    # Check for unexpected settings
    allowed_settings = list(type_settings.get("optional", {}).keys()) + list(
        type_settings.get("required", {}).keys()
    )
    for key in block.get("settings", {}):
        if key not in allowed_settings:
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
        validators.validate_type(value, type_conf["input"], block)
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
    """
    message = "0b"
    for value, block in zip(values, items):
        message += encode_block(value, block)[2:]
    return message


def decode_items(message, items):
    """
    Decodes list of blocks.

    Args:
        message (str): Binary string of the message.
        items (list): A list of blocks.

    Returns:
        values (list): The list of values for the blocks.
    """
    values = []
    offset = 2
    items = fill_bits_settings(message, items)
    for block in items:
        bits = block["settings"]["bits"]
        values.append(decode_block("0b" + message[offset : offset + bits], block))
        offset += bits
    return values


def fill_bits_settings(message, items):
    """
    Fills the bits values for each block in items if
    Args:
        message (str): Binary string of the message.
        items (list): A list of blocks.

    Returns:
        items (list): The list of blocks with the bits values filled.
    """
    items = copy.deepcopy(items)
    for block in items:
        block["settings"] = block.get("settings", {})
        if block["type"] == "boolean":
            block["settings"]["bits"] = 1
        if block["type"] == "object":
            block["settings"]["bits"] = 0
            block["settings"]["items"] = fill_bits_settings(
                message, block["settings"]["items"]
            )
    return items

    ## Adds fixed parameters
    # for s_name, val in type_settings.get("fixed", {}).items():
    #    if "settingsg" not in block:
    #        block["settings"] = {}
    #    block["settings"][s_name] = val

    # if "bits" in block.get("settings", {}):
    #     acc += block["settings"]["bits"]
    # if block["type"] == "object":
    #     for b in block["settings"]["items"]:
    #         acc += accumulate_bits(message, b)
    # return acc
