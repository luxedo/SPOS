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
import collections
import copy

from .exceptions import SpecsVersionError


def truncate_bits(bit_str, bits):
    """
    Truncates the `bit_str` to up to `bits`.
    Args:
        bit_str (str): Bit string.
        bits (int): Number of bits to truncate.

    Returns:
        trunc_bit_str (str): Truncated bit string.
    """
    return "0b" + "0" * (bits - len(bit_str) + 2) + bit_str[2 : bits + 2]


def validate_payload_spec(payload_spec):
    """
    Checks payload_spec for valid keys and values. Does not validates
    blocks.

    Args:
        payload_spec (dict): Payload specification.

    Raises:
        ValueError, KeyError, TypeError: When `payload_spec` does not
            follows correct specifications. See https://github.com/luxedo/SPOS
    """
    extra_keys = [
        key
        for key in payload_spec.keys()
        if key not in ["name", "version", "body", "meta"]
    ]
    if any(extra_keys):
        raise ValueError(f"Found unexpected keys {extra_keys} in payload_spec.")
    required_keys = {"name": str, "version": int, "body": list}
    for key, tp in required_keys.items():
        if key not in payload_spec:
            raise KeyError(f"payload_spec {payload_spec} must have key '{key}'")
        if not isinstance(payload_spec[key], tp):
            raise TypeError(
                f"payload_spec {payload_spec['name']} key '{key}' must be of type '{tp}'"
            )

    dup_keys_body = duplicate_keys(payload_spec["body"])
    if any(dup_keys_body):
        raise KeyError(f"Duplicate keys found in body: {dup_keys_body}.")

    meta = payload_spec.get("meta", {})
    if not isinstance(meta, dict):
        raise ValueError(f"meta key expected to be a dict, got {type(meta)}.")
    if meta.get("send_version"):
        if not isinstance(meta["send_version"], bool):
            raise TypeError(
                f"meta.send_version expected to be boolean, got {type(meta['send_version'])}."
            )
        if not meta.get("version_bits"):
            raise KeyError("Missing key meta.version_bits.")
        if not isinstance(meta["version_bits"], int):
            raise TypeError(
                "meta.version_bits expected to be integer, got {type(meta['version_bits'])}."
            )
        if payload_spec["version"] >= 2 ** meta["version_bits"]:
            raise ValueError(
                f"Version overflow: {payload_spec['version']} >= {2**meta['version_bits']}"
            )

    header_bl = meta.get("header", {})
    validate_header(header_bl)
    dup_keys_head = duplicate_keys(header_bl)
    if any(dup_keys_head):
        raise KeyError(f"Duplicate keys found in header: {dup_keys_head}.")


def duplicate_keys(blocklist):
    """
    Checks if `blocklist` has duplicate keys.

    Args:
        blocklist

    Returns:
        dup_keys (list): List of duplicate keys.
    """
    return [
        key
        for key, count in collections.Counter(
            [block["key"] for block in blocklist]
        ).items()
        if count > 1
    ]


def validate_header(header_bl):
    """
    Run checks for static value in the header block.

    Args:
        header_bl (list): List of blocks for the header.

    Raises:
        KeyError: If header block does not contain 'key'.
        KeyError: If static header block does not contain 'value'.
    """
    header_static = [block_spec for block_spec in header_bl if "value" in block_spec]

    for block in header_static:
        if "key" not in block:
            raise KeyError(f"Static block {block} must have key 'key'")
        if len(block.keys()) > 2:
            raise KeyError(
                f"Static block {block['key']} must have onlye two keys: 'key' and 'value'"
            )


def validate_specs(specs, match_versions=False):
    """
    Validates an array of specs.

    Args:
        specs (list): Array of specs.
        match_versions (bool): If True raises SpecsVersionError
            if the array has conflicting versions or different
            version_bits.

    Raises:
        SpecsVersionError: When `match_versions` is set to True and
            there's duplicate versions or name mismatch.
        Other exceptions: Listed in spos.utils.validate_payload_spec.
    """
    for payload_spec in specs:
        validate_payload_spec(payload_spec)
    if match_versions:
        versions = []
        name = None
        for payload_spec in specs:
            name = payload_spec["name"] if name is None else name
            if payload_spec["version"] in versions:
                raise SpecsVersionError(
                    f"Duplicated version in 'specs': {payload_spec['version']}."
                )
            if name != payload_spec["name"]:
                raise SpecsVersionError("Name mismatch in 'specs'.")
            versions.append(payload_spec["version"])


def remove_null_values(d):
    """
    Removes None from dictionary `d` recursively.

    Args:
        d (dict)

    Returns:
        d (dict): Dictionary without None values.
    """
    bd = copy.deepcopy(d)
    del_keys = {key for key, value in bd.items() if value is None}
    for key in del_keys:
        del bd[key]
    for key in [key for key, value in bd.items() if isinstance(value, dict)]:
        bd[key] = remove_null_values(bd[key])
    return bd
