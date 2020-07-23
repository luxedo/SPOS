"""
SPOS - Small Payload Object Serializer
Copyright (C) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This library implements the encoders and decoders for each type in SPOS
Types must inherit `Block` Abstract Base Class.

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
import abc
from string import ascii_uppercase, ascii_lowercase, digits
import copy
import math
import re
import warnings

from .utils import truncate_bits, nest_keys
from .exceptions import StaticValueMismatchWarning


# ---------------------------------------------------------------------
# BLOCK ABC
# ---------------------------------------------------------------------
class BlockBase(abc.ABC):
    """
    Block ABC

    The block is the base object for encoding/decoding messages for
    SPOS.

    A block_spec is required for instantiating a block, required and
    optional keys must be described in class attributes with the same
    name.

    To create a block type it's necessary to inherit this abc and
    implement at least the methods `_bin_encode` and `_bin_decode`.

    """

    required = {}
    optional = {}

    def __init__(self, block_spec):
        self.block_spec = copy.deepcopy(block_spec)
        self.validate_block_spec_keys()
        self.key = block_spec.get("key")
        self.type = block_spec.get("type")
        if not hasattr(self, "value"):
            self.value = block_spec.get("value")
        if not hasattr(self, "bits"):
            self.bits = block_spec.get("bits", 0)

        self.initialize_block()
        self.cache_message = None
        self.cache_value = None
        if self.value is not None:
            self.cache_message = self.bin_encode(self.value)
            self.cache_value = self.bin_decode(self.cache_message)

    def __repr__(self):
        return f"block => {self.block_spec}"

    @abc.abstractmethod
    def _bin_encode(self, value):
        """
        Required method to be implemented for subclasses
        """

    def bin_encode(self, value):
        """
        Method for value binary encoding
        """
        if self.cache_message is not None:
            return self.cache_message
        return self._bin_encode(value)

    @abc.abstractmethod
    def _bin_decode(self, message):
        """
        Required method to be implemented for subclasses
        """

    def bin_decode(self, message):
        """
        Method for binary message decoding
        """
        value = self._bin_decode(message)
        if self.cache_value is not None:
            if value != self.cache_value:
                warnings.warn(
                    f"Decoded message and static value don't match {value} != {self.cache_value}",
                    StaticValueMismatchWarning,
                )
            return self.cache_value
        return value

    def initialize_block(self):
        """
        Optional method for initializing block_spec
        """

    def validate_block_spec_keys(self):
        """
        Validates the keys of `block_spec`. Keys must be specified as
        class attributes `required` and `optional`.
        """
        for key in self.required:
            if key not in self.block_spec:
                raise KeyError(
                    f"Required key {key} not found for block {self}"
                )
            if key == "blocks":
                self.blocks = Block(self.block_spec["blocks"])
            elif key == "blocklist":
                self.blocklist = [
                    Block(b_spec) for b_spec in self.block_spec["blocklist"]
                ]
            else:
                validate_type(self.required[key], self.block_spec[key])
                setattr(self, key, self.block_spec[key])

        for key in self.optional:
            if key in self.block_spec:
                validate_type(self.optional[key]["type"], self.block_spec[key])
                setattr(self, key, self.block_spec[key])
            else:
                setattr(self, key, self.optional[key]["default"])

        all_keys = (
            set(self.required)
            | set(self.optional)
            | set(("key", "value", "type"))
        )
        for key in self.block_spec:
            if key not in all_keys:
                raise KeyError(f"Unexpected key {key} found in {self}")

    def consume(self, message):
        """
        Decodes the block data while returning any unused bits.

        Args:
            message (str): Binary string of the message
        Returns:
            value: Decoded value
            message_tail (str): Unused message bits
        """
        bits = self.accumulate_bits(message)
        value = self.bin_decode(message[: bits + 2])
        return value, "0b" + message[bits + 2 :]

    def accumulate_bits(self, message):
        """
        Optional method that should return the number of bits of the
        instance type. This will change only for types that changes
        dinamically.
        """
        return self.bits


# ---------------------------------------------------------------------
# METHOD DECORATORS
# ---------------------------------------------------------------------
def validate_type(types, value):
    if isinstance(types, type):
        types = (types,)
    for t in types:
        if isinstance(value, t):
            break
    else:
        raise TypeError(f"Unexpected type {type(value)}")


def validate_encode_input_types(*types):
    def _validate_wrapper(fn):
        def _validate_type_inner(self, value):
            validate_type(types, value)
            return fn(self, value)

        return _validate_type_inner

    return _validate_wrapper


# ---------------------------------------------------------------------
# TYPES
# ---------------------------------------------------------------------
class BooleanBlock(BlockBase):
    bits = 1

    @validate_encode_input_types(bool, int)
    def _bin_encode(self, value):
        return "0b1" if value else "0b0"

    def _bin_decode(self, message):
        return message == "0b1"


class BinaryBlock(BlockBase):
    required = {"bits": int}

    @validate_encode_input_types(str)
    def _bin_encode(self, value):
        if not re.match("^(0b[0-1]*|0x[0-9a-fA-F]*)$", value):
            raise ValueError(
                f"Value for block '{self.key}' must be a binary string or an hex string, got {value}."
            )

        bit_str = (
            bin(int(value, 2))
            if value.startswith("0b")
            else bin(int(value, 16))
        )
        return truncate_bits(bit_str, self.bits)

    def _bin_decode(self, message):
        return truncate_bits(message, self.bits)


class IntegerBlock(BlockBase):
    required = {"bits": int}
    optional = {"offset": {"type": int, "default": 0}}
    offset = None  # Just to calm down the linter

    @validate_encode_input_types(int)
    def _bin_encode(self, value):
        value -= self.offset
        bits = self.bits
        overflow = 2 ** bits - 1
        bit_str = bin(min([max([value, 0]), overflow]))
        return truncate_bits(bit_str, bits)

    def _bin_decode(self, message):
        return int(message, 2) + self.offset


class FloatBlock(BlockBase):
    required = {"bits": int}
    optional = {
        "lower": {"type": (int, float), "default": 0},
        "upper": {"type": (int, float), "default": 1},
        "approximation": {
            "type": (str),
            "default": "round",
            "choices": ["round", "floor", "ceil"],
        },
    }
    lower, upper, approximation = None, None, None

    @validate_encode_input_types(int, float)
    def _bin_encode(self, value):
        approx = round
        if self.approximation == "floor":
            approx = math.floor
        elif self.approximation == "ceil":
            approx = math.ceil
        overflow = 2 ** self.bits - 1
        delta = self.upper - self.lower
        value = overflow * (value - self.lower) / delta
        bit_str = bin(approx(min([max([value, 0]), overflow])))
        return truncate_bits(bit_str, self.bits)

    def _bin_decode(self, message):
        delta = self.upper - self.lower
        overflow = 2 ** self.bits - 1
        return int(message, 2) * delta / overflow + self.lower


class PadBlock(BlockBase):
    required = {"bits": int}
    value = True

    def _bin_encode(self, value=None):
        return f"0b{'1' * self.bits}"

    def _bin_decode(self, message):
        return None


class ArrayBlock(BlockBase):
    required = {"bits": int, "blocks": "block"}
    blocks = None

    def initialize_block(self):
        self.max_length = 2 ** self.bits - 1
        self.length_block = IntegerBlock({"bits": self.bits, "offset": 0})

    @validate_encode_input_types(list, tuple, set)
    def _bin_encode(self, value):
        message = ""
        length = min([len(value), self.max_length])
        message += self.length_block.bin_encode(length)
        for i, v in enumerate(value):
            if i == self.max_length:
                break
            message += self.blocks.bin_encode(v)[2:]
        return message

    def _bin_decode(self, message):
        length, message = self.length_block.consume(message)
        values = []
        for _ in range(length):
            v, message = self.blocks.consume(message)
            values.append(v)
        return values

    def accumulate_bits(self, message):
        length, message = self.length_block.consume(message)
        return self.bits + length * self.blocks.accumulate_bits(message)


class ObjectBlock(BlockBase):
    required = {"blocklist": "blocklist"}
    blocklist = None

    def get_value(self, obj, key):
        """
        Gets a value from object `obj`. Dot '.' separates nested
        objects.

        Args:
            obj (dict): Object to get value
            key (str): Key to acess object

        Returns:
            value

        Raises:
            KeyError: If can't find key
        """
        if "." in key:
            dot_idx = key.index(".")
            k1, k2 = key[:dot_idx], key[dot_idx + 1 :]
            return self.get_value(obj[k1], k2)
        return obj[key]

    @validate_encode_input_types(dict)
    def _bin_encode(self, value):
        values = [
            self.get_value(value, block.key)
            if block.value is None
            else block.value
            for block in self.blocklist
        ]
        return "0b" + "".join(
            [
                block.bin_encode(v)[2:]
                for v, block in zip(values, self.blocklist)
            ]
        )

    def _bin_decode(self, message):
        obj = {}
        for block in self.blocklist:
            obj[block.key], message = block.consume(message)
        obj = nest_keys(obj)
        return obj

    def accumulate_bits(self, message):
        acc = 0
        for block in self.blocklist:
            bits = block.accumulate_bits(message)
            _, message = block.consume(message)
            acc += bits
        return acc


class StringBlock(BlockBase):
    required = {"length": int}
    optional = {"custom_alphabeth": {"type": (dict), "default": {}}}
    length, custom_alphabeth = None, None

    alphabeth = dict(
        enumerate(ascii_uppercase + ascii_lowercase + digits + "+/")
    )
    rev_alphabeth = {val: key for key, val in alphabeth.items()}

    def initialize_block(self):
        self.letter_bits = 6
        self.letter_block = IntegerBlock(
            {"bits": self.letter_bits, "offset": 0}
        )
        self.bits = self.length * self.letter_bits

    @validate_encode_input_types(str)
    def _bin_encode(self, value):
        message = "0b"
        value = value.rjust(self.length, " ")
        rev_custom_alphabeth = {
            val: key for key, val in self.alphabeth.items()
        }
        rev_space_map = {" ": 62}  # Maps spaces to +
        for letter in value:
            val = rev_custom_alphabeth.get(
                letter,
                rev_space_map.get(letter, self.rev_alphabeth.get(letter, 63)),
            )
            message += self.letter_block.bin_encode(val)[2:]
        return message

    def _bin_decode(self, message):
        alphabeth = self.alphabeth.copy()
        alphabeth.update(self.custom_alphabeth)
        value = ""
        for _ in range(self.length):
            l, message = self.letter_block.consume(message)
            value += alphabeth[l]
        return value


class StepsBlock(BlockBase):
    required = {"steps": list}
    optional = {"steps_names": {"type": list, "default": []}}
    steps, steps_names = None, None

    def initialize_block(self):
        if self.steps != sorted(self.steps):
            raise ValueError(
                f"Steps Block {self.key} must be ordered: {self.steps}"
            )
        self.bits = math.ceil(math.log(len(self.steps) + 1, 2))
        self.steps_block = IntegerBlock({"bits": self.bits, "offset": 0})
        if not self.steps_names:
            self.steps_names = (
                ["x<{0}".format(self.steps[0])]
                + [
                    "{0}<=x<{1}".format(lower, upper)
                    for lower, upper in zip(self.steps, self.steps[1:])
                ]
                + ["x>={0}".format(self.steps[0])]
            )
        if len(self.steps_names) != len(self.steps) + 1:
            raise ValueError(
                f"'steps_names' for block {self.key} has to have length 1 + len(steps)."
            )

    @validate_encode_input_types(int, float)
    def _bin_encode(self, value):
        value = ([value >= s for s in self.steps] + [False]).index(False)
        return self.steps_block.bin_encode(value)

    def _bin_decode(self, message):
        value = self.steps_block.bin_decode(message)
        return (
            self.steps_names[value]
            if value < len(self.steps_names)
            else "error"
        )


class CategoriesBlock(BlockBase):
    required = {"categories": list}
    categories = None

    def initialize_block(self):
        self.categories = self.categories + ["unknown"]
        self.bits = math.ceil(math.log(len(self.categories), 2))
        self.categories_block = IntegerBlock({"bits": self.bits, "offset": 0})

    @validate_encode_input_types(str)
    def _bin_encode(self, value):
        value = (
            len(self.categories) - 1
            if value not in self.categories
            else self.categories.index(value)
        )
        return self.categories_block.bin_encode(value)

    def _bin_decode(self, message):
        value = self.categories_block.bin_decode(message)
        return (
            self.categories[value] if value < len(self.categories) else "error"
        )


# ---------------------------------------------------------------------
# GENERIC BLOCK CLASS
# ---------------------------------------------------------------------
class Block:
    """
    The block is the base object for encoding/decoding messages for
    SPOS.

    This is a generic class to instantiate one payload types listed
    in: https://github.com/luxedo/SPOS#block

    Args:
        block_spec (dict): Block specification.
    """

    BLOCK_TYPES = {
        "boolean": BooleanBlock,
        "binary": BinaryBlock,
        "integer": IntegerBlock,
        "float": FloatBlock,
        "pad": PadBlock,
        "array": ArrayBlock,
        "object": ObjectBlock,
        "string": StringBlock,
        "steps": StepsBlock,
        "categories": CategoriesBlock,
    }
    key, type, value, bits = None, None, None, None

    def __new__(cls, block_spec):
        cls.validate_block_spec(cls, block_spec)
        return cls.BLOCK_TYPES[block_spec["type"]](block_spec)

    @staticmethod
    def validate_block_spec(cls, block_spec):
        """
        Check for general block specification keys: key and type.

        Args:
            block_spec (dict): Block specification.

        Raises:
            KeyError, TypeError, ValueError: When `block_spec` does
                not conforms to block specification. See:
                https://github.com/luxedo/SPOS#block
        """
        if "key" not in block_spec:
            raise KeyError(f"Block '{block_spec}' must have 'key'.")
        key = block_spec["key"]
        if not isinstance(key, str):
            raise TypeError(f"Block '{block_spec}' 'key' must be a string.")

        # Check type
        if "type" not in block_spec:
            raise KeyError(f"Block '{key}' must have 'type'.")
        b_type = block_spec["type"]
        if b_type not in cls.BLOCK_TYPES:
            raise ValueError(
                f"Block '{block_spec}' has an unknown 'type' {b_type}."
            )
