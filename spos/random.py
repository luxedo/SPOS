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
import random

from . import encode, utils
from .blocks import Block
from .typing import Any, Dict, Message, PayloadSpec, Tuple


def seed(a: Any = None, version: int = 2) -> None:
    """
    Alias for random.seed
    """
    random.seed(a, version)


class RandomBlock:
    def __init__(self, block_spec):
        self.block = Block(block_spec)
        self.random_encoders = {
            "array": self.array_random_message,
            "object": self.object_random_message,
            "steps": self.steps_random_message,
            "categories": self.categories_random_message,
        }
        self.random_decoders = {
            "pad": self.pad_random_value,
            "object": self.object_random_value,
            "steps": self.steps_random_value,
            "categories": self.categories_random_value,
        }

    def random_message(self) -> str:
        """
        Creates a random message
        """
        if self.block.cache_message:
            return self.block.cache_message

        if self.block.type in self.random_encoders:
            return self.random_encoders[self.block.type]()

        return utils.random_bits(self.block.bits)

    def random_value(self):
        """
        Creates a random value
        """
        if self.block.cache_value:
            return self.block.cache_value

        if self.block.type in self.random_decoders:
            return self.random_decoders[self.block.type]()

        return self.block.bin_decode(self.random_message())

    def pad_random_value(self):
        return None

    def array_random_message(self) -> str:
        message = "0b"
        if not self.block.fixed:
            length = random.randint(0, self.block.length)
            message += self.block.length_block.bin_encode(length)[2:]
        else:
            length = self.block.length
        random_blocks = RandomBlock(self.block.blocks.block_spec)
        message += "".join(
            [random_blocks.random_message()[2:] for _ in range(length)]
        )
        return message

    def object_random_message(self) -> str:
        message = "0b"
        for block in self.block.blocklist:
            random_block = RandomBlock(block.block_spec)
            message += random_block.random_message()[2:]
        return message

    def object_random_value(self):
        obj = {}
        for block in self.block.blocklist:
            random_block = RandomBlock(block.block_spec)
            obj[block.key] = random_block.random_value()
        obj = utils.nest_keys(obj)
        return obj

    def steps_random_value(self):
        steps = self.block.steps + [self.block.steps[0] - 1]
        return random.choice(steps)

    def steps_random_message(self) -> str:
        return self.block.bin_encode(self.random_value())

    def categories_random_value(self):
        return random.choice(self.block.categories)

    def categories_random_message(self) -> str:
        return self.block.bin_encode(self.random_value())

    # Mock methods for linters/mypy
    def cache_message(self):
        pass  # pragma: no cover


def block_random_value(block_spec):
    """
    Generates a random value within block specification.
    Returns the static value if it's defined in the block.

    Args:
        block_spec (dict): Block specification.

    Returns:
        value: Random value.
    """
    return RandomBlock(block_spec).random_value()


def block_random_message(block_spec):
    """
    Generates a random message within block specification.
    Returns the static value message if it's defined in the block.

    Args:
        block_spec (dict): Block specification.
    Returns:
        message: Random message.
    """
    return RandomBlock(block_spec).random_message()


def random_payload(
    payload_spec: PayloadSpec, output: str = "bin"
) -> Tuple[Message, Dict]:
    """
    Builds a random message conforming to `payload_spec`.

    Args:
        payload_spec (dict): Payload specification.
        output (str): Output format (bin, hex or bytes). default: "bin".

    Returns:
        message (bin | hex | bytes): Random message
        payload_data (object): Equivalent payload_data to generate
            message.
    """
    utils.validate_payload_spec(payload_spec)

    meta = block_random_value(
        {
            "key": "meta",
            "type": "object",
            "blocklist": [
                block_spec
                for block_spec in payload_spec.get("meta", {}).get(
                    "header", []
                )
                if "value" not in block_spec
            ],
        }
    )
    body = block_random_value(
        {
            "key": "body",
            "type": "object",
            "blocklist": payload_spec.get("body", []),
        }
    )
    payload_data = utils.merge_dicts(meta, body)
    message = encode(payload_data, payload_spec, output)
    return message, payload_data
