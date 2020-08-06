"""
Generates a payload based on a payload spec
"""
import random

from . import utils, encode
from .blocks import Block


def seed(a=None, version=2):
    """
    Alias for random.seed
    """
    random.seed(a, version)


class RandomBlock(Block):
    def __new__(cls, *args, **kwargs):
        random_encoders = {
            "array": cls.array_random_message,
            "object": cls.object_random_message,
            "steps": cls.steps_random_message,
            "categories": cls.categories_random_message,
        }
        random_decoders = {
            "pad": cls.pad_random_value,
            "object": cls.object_random_value,
            "steps": cls.steps_random_value,
            "categories": cls.categories_random_value,
        }
        instance = super().__new__(cls, *args, **kwargs)
        setattr(
            instance,
            "random_message",
            cls.random_message.__get__(instance, instance.__class__),
        )
        setattr(
            instance,
            "_random_message",
            cls._random_message.__get__(instance, instance.__class__),
        )
        setattr(
            instance,
            "random_value",
            cls.random_value.__get__(instance, instance.__class__),
        )
        setattr(
            instance,
            "_random_value",
            cls._random_value.__get__(instance, instance.__class__),
        )
        for name, fn in random_encoders.items():
            if instance.type == name:
                setattr(
                    instance,
                    "_random_message",
                    fn.__get__(instance, instance.__class__),
                )
        for name, fn in random_decoders.items():
            if instance.type == name:
                setattr(
                    instance,
                    "_random_value",
                    fn.__get__(instance, instance.__class__),
                )
        return instance

    def random_message(self):
        """
        Creates a random message
        """
        return (
            self._random_message()
            if not self.cache_message
            else self.cache_message
        )

    def _random_message(self):
        return utils.random_bits(self.bits)

    def random_value(self):
        """
        Creates a random value
        """
        return (
            self._random_value() if not self.cache_value else self.cache_value
        )

    def _random_value(self):
        return self.bin_decode(self.random_message())

    def pad_random_value(self):
        return self._bin_encode(None)

    def array_random_message(self):
        length = random.randint(0, self.max_length)
        len_message = self.length_block.bin_encode(length)
        random_blocks = RandomBlock(self.blocks.block_spec)
        return f"{len_message}{''.join([random_blocks.random_message()[2:] for _ in range(length)])}"

    def object_random_message(self):
        message = "0b"
        for block in self.blocklist:
            random_block = RandomBlock(block.block_spec)
            message += random_block.random_message()[2:]
        return message

    def object_random_value(self):
        obj = {}
        for block in self.blocklist:
            random_block = RandomBlock(block.block_spec)
            obj[block.key] = random_block.random_value()
        obj = utils.nest_keys(obj)
        return obj

    def steps_random_value(self):
        steps = self.steps + [self.steps[0] - 1]
        return random.choice(steps)

    def steps_random_message(self):
        return self.bin_encode(self.random_value())

    def categories_random_value(self):
        return random.choice(self.categories[:-1])

    def categories_random_message(self):
        return self.bin_encode(self.random_value())


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


def random_payload(payload_spec, output="bin"):
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
