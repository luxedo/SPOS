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
    return spos.decode_block(block_random_message(block_spec), block_spec)


def block_random_message(block_spec):
    """
    Generates a random message within block specification.
    Returns the static value message if it's defined in the block.

    Args:
        block_spec (dict): Block specification.
    Returns:
        message: Random message.
    """
    block = spos.Block(block_spec)
    if block.type == "array":
        length_spec = {"key": "length", "type": "integer", "bits": block.bits}
        length = block_random_value(length_spec)
        message = spos.Block(length_spec).bin_encode(length)
        for _ in range(length):
            message += block_random_message(block_spec["blocks"])[2:]
        return message

    if block.type == "object":
        message = "0b"
        for b_spec in block_spec["blocklist"]:
            message += block_random_message(b_spec)[2:]
        return message

    message = f"0b{''.join([str(random.randint(0, 1)) for _ in range(block.bits)])}"
    if block.type in ("steps", "categories"):
        try:
            block.bin_decode(message)
            return message
        except IndexError:
            return block_random_message(block_spec)
    return message


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
