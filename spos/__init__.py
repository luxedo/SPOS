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
from . import encoders, decoders, validators

TYPES = {
    "boolean": {
        "validator": validators.validate_boolean,
        "encoder": encoders.encode_boolean,
        "decoder": decoders.decode_boolean,
    },
    "binary": {
        "validator": validators.validate_binary,
        "encoder": encoders.encode_binary,
        "decoder": decoders.decode_binary,
    },
    "integer": {
        "validator": validators.validate_integer,
        "encoder": encoders.encode_integer,
        "decoder": decoders.decode_integer,
        "required": {"bits": int},
        "optional": {"offset": {"type": [int], "default": 0}},
    },
    "float": {
        "validator": validators.validate_float,
        "encoder": encoders.encode_float,
        "decoder": decoders.decode_float,
        "required": {"bits": int},
        "optional": {
            "lower": {"type": [int, float], "default": 0},
            "upper": {"type": [int, float], "default": 1},
            "approximation": {
                "type": [str],
                "default": "round",
                "choices": ["round", "floor", "ceil"],
            },
        },
    },
    "pad": {
        "validator": lambda value, name: None,
        "encoder": lambda value, block: "0b" + "1" * block["settings"]["bits"],
        "decoder": lambda message, block: None,
    },
    "array": {
        "validator": validators.validate_array,
        "encoder": encoders.encode_array,
        "decoder": decoders.decode_array,
        "required": {"bits": int},
        "optional": {
            "lower": {"type": [int, float], "default": 0},
            "upper": {"type": [int, float], "default": 1},
            "approximation": {
                "type": [str],
                "default": "round",
                "choices": ["round", "floor", "ceil"],
            },
        },
    },
}


def validate_block(block_spec):
    """
    Validates block specification.

    Args:
        block_spec (dict): Block specification.

    Raises:
        KeyError, ValueError, TypeError: For non conformant block_specs.
    """
    # Check name
    if "name" not in block_spec:
        raise KeyError("Block '{0}' must have 'name'.".format(block_spec))
    name = block_spec["name"]
    if not isinstance(name, str):
        raise TypeError("Block '{0}' 'name' must be a string.".format(name))

    # Check type
    if "type" not in block_spec:
        raise KeyError("Block '{0}' must have 'type'.".format(name))
    b_type = block_spec["type"]
    if block_spec["type"] not in TYPES:
        raise ValueError("Block '{0}' has an unknown 'type' {1}.".format(name, b_type))
    type_settings = TYPES[block_spec["type"]]

    # Check settings
    for s_name, tp in type_settings.get("required", {}).items():
        if s_name not in block_spec.get("settings", {}):
            raise KeyError("Block '{0}' requires setting '{1}'.".format(name, s_name))
        if not isinstance(block_spec["settings"][s_name], tp):
            raise TypeError(
                "Block '{0}' setting '{1}' has wrong type '{2}' instead of '{3}'.".format(
                    name, s_name, type(block_spec["settings"][s_name]), tp
                )
            )
    for s_name, opts in type_settings.get("optional", {}).items():
        if not s_name in block_spec["settings"]:
            block_spec["settings"][s_name] = opts["default"]
        if not any(
            isinstance(block_spec["settings"][s_name], tp) for tp in opts["type"]
        ):
            raise TypeError(
                "Block '{0}' optional setting '{1}' has wrong type '{2}' instead of '{3}'.".format(
                    name, s_name, type(block_spec["settings"][s_name]), tp
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
    type_conf["validator"](value, block)
    return type_conf["encoder"](value, block)


def decode_block(message, block):
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
    return type_conf["decoder"](message, block)
