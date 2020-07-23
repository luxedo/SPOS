"""
Generates a payload based on a payload spec
"""
import random

import spos
from spos import utils


def seed(a=None, version=2):
    """
    Alias for random.seed
    """
    random.seed(a, version)


def block_random_value(block_spec):
    """
    Generates a random value within block specification.
    Returns the static value if it's defined in the block.

    Args:
        block_spec (dict): Block specification.

    Returns:
        value: Random value.
    """
    return spos.Block(block_spec).random_value()


def block_random_message(block_spec):
    """
    Generates a random message within block specification.
    Returns the static value message if it's defined in the block.

    Args:
        block_spec (dict): Block specification.
    Returns:
        message: Random message.
    """
    return spos.Block(block_spec).random_message()


def random_payloads(payload_spec, output="bin"):
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

    payload_data = {}
    for block_spec in payload_spec.get("meta", {}).get("header", []):
        if block_spec.get("value") is None:
            payload_data[block_spec["key"]] = block_random_value(block_spec)

    for block_spec in payload_spec.get("body", []):
        if block_spec.get("value") is None:
            payload_data[block_spec["key"]] = block_random_value(block_spec)

    message = spos.encode(payload_data, payload_spec, output)
    return message, payload_data
