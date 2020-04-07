# SPOS

> **SPOS** stands for **Small Payload Object Serializer**.

[![codecov](https://codecov.io/gh/luxedo/spos/branch/master/graph/badge.svg)](https://codecov.io/gh/luxedo/spos) [![CodeFactor](https://www.codefactor.io/repository/github/luxedo/spos/badge)](https://www.codefactor.io/repository/github/luxedo/spos) [![PyPI version](https://badge.fury.io/py/spos.svg)](https://badge.fury.io/py/spos) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

`SPOS` is a tool for serializing objects. This tool focuses in
maintaining a consistent payload size while sacrificing precision.
Applications with limited bandwidth like [LoRa](https://lora-alliance.org/)
or [Globalstar](https://www.globalstar.com/en-us/) are ideal candidates
for `SPOS`. `SPOS` is built as a library for `python3` and a command line
tool.

## Quick Start

To encode data, `SPOS` needs two arguments to serialize the data: The
`payload_data` to be serialized and the [payload specification](#Payload-Specification).

```python
import spos
payload_spec = {
  "name": "example payload",
  "version": "1.0.0",
  "crc8": False,
  "items": [{
    "type": "integer",
    "key": "payload_version",
    "value": 1,  # 01
    "bits": 2
  }, {
    "type": "integer",
    "key": "int_data",
    "bits": 6
  }, {
    "type": "float",
    "key": "float_data",
    "bits": 6
}]
payload_data = {
  "int_data": 13,    # 001101
  "float_data": 0.6  # 010011 (19/32 or 0.59375)
}

message = spos.bin_encode(payload_data, payload_spec)
"0b01001101010011"
```

Decoding data

```python
import spos
payload_spec = {
  "name": "example payload",
  "version": "1.0.0",
  "crc8": False,
  "items": [{
    "type": "integer",
    "key": "payload_version",
    "value": 1,  # 01
    "bits": 2
  }, {
    "type": "integer",
    "key": "int_data",
    "bits": 6
  }, {
    "type": "float",
    "key": "float_data",
    "bits": 6
}]
message = "0b01001101010011"
payload_data = spos.bin_decode(message, payload_spec)
{
  "payload_version": 1,
  "int_data": 13,
  "float_data": 0.59375
}
```

## Installation

```
pip install spos
```

## Payload Specification

The payload specification must contain the key `items`, which must be
an array containing objects that describe each `block` of the
serialized message.

```python
payload_spec = {
  "items": [{
    "type:": "integer",
    "key": "temperature",
    "bits": 6,
    "offset": 273
}]}
```

Additional keys can be provided and keys not listed are ignored.

### Payload Specification keys

#### `items`

The array of `blocks` describing the message.

#### `name`

Message name

#### `version`

Message version

#### `crc8`

If "True", calculates the [CRC8](https://en.wikipedia.org/wiki/Cyclic_redundancy_check) (8bits) for the message and appends it to payload.

## Block

The required keys for `block` objects are: `key` and `type`. `value` is
an optional key. For each `type` there might be aditional required keys
and/or optional keys.

The value to be encoded is either a `key` in the `payload_data` object or
a statuc `value` if present.

The encoded data is _big-endian_ and truncations occour in the least
significant bits when applicable. Data overflow is set to the maximum
value and underflow to the minimum.

### Block keys

#### `key`

The key to get the value of the `block` in `payload_data`.
Optionally, the `key` can accesss a value in a nested object using a
dot `.` to separate the levels. Eg:

```javascript
import spos
payload_spec = {
  "name": "example nested value",
  "items": [{
  "type": "integer",
  "bits": 8,
  "key": "nested.value"
  }]
payload_data = {
  "nested": {
    "value": 255
  }
}
spos.bin_encode(payload_data, payload_spec)
"0b11111111"
```

#### `value`

A static value for the `block` (optional).

#### `type`

There are 10 types avaliable for serializing data: `boolean`, `binary`,
`integer`, `float`, `pad`, `array`, `object`, `string`, `steps`, and
`categories`.

The basic types are:

##### `boolean`

Boolean value.

Input: `boolean`.
Additional keys: `None`.

##### `binary`

Binary value. The data can be a binary string or an hex string. Eg

```
"0b10101010"  # binary
"0xdeadbeef"  # hex
```

This data is truncated in the least significant bits if the size of
the string in binary is bigger than `bits`.

Input: `string`.
Additional keys:

- `bits` (int): length of the block in bits

##### `integer`

Integer value.

Input: `integer`.
Additional key:

- `bits` (int): length of the block in bits
- `offset` (int): An integer to offset the final value. Default: 0.

##### `float`

Float value.

This type divides the interval between the `lower` and `upper`
boundaries in equal parts according to the avaliable `bits`. The
serialized value is the closest to the real one by default
("approximation": "round").

Input: `int|float`.
Additional keys:

- `bits` (int): length of the block in bits
- `lower` (int|float), optional: Float lower boundary. Default 0.
- `upper` (int|float), optional: Float upper boundary. Default 1.
- `approximation` (str), optional: Float approximation method. Values can be: "round", "floor", "ceil". Default: "round"

##### `pad`

Pads the message. No data is collected from this block.

Input: `None`.
Additional keys:

- `bits` (int): length of the block in bits

---

Advanced types:

##### `array`

An array containing `block` values.

The size in bits of this type is `bits` + `length` \* `blocks` &rarr; `bits`.

Input: An `array` of values allowed for `blocks`.
Additional keys:

- `bits` (int): Number of bits to store the maximum length of the array.
- `blocks` (block): The `block` specification of the objects in the array.

##### `object`

Object value. Maps the data to an object.

The size in bits of this type is the sum of sizes of blocks declared
for this `block`.

Input: `object`.
Additional keys:

- `items` (items): The `array` of `blocks` describing the object.

##### `string`

String value.

This data type encodes the string to base64. Characters outside the
[base64 index table](https://en.wikipedia.org/wiki/Base64#Base64_table)
are replaced with `/` (index 62) and spaces are replaced with `+`
(index 63).

The size in bits of this type is 6 \* `length`.

Input: `string`.
Additional keys:

- `length` (int): Strings maximum length.
- `custom_alphabeth` (object), optional: Remaps the characters to another index.
  eg: Adding support for a `json` string but sacrificing the first 7
  indexes (ABCDEFG).

```python
payload_spec = {
  "items": [{
    "type:": "string",
    "key": "text",
    "length": 128,
    "custom_alphabeth": {
      0: "{",
      1: "}",
      2: "[",
      3: "]",
      4: '"',
      5: ',',
      6: '.',
    }
}]

```

#### `steps`

Maps a numeric value to named steps. Eg:

```python
payload_spec = {
  "items": [{
    "type:": "steps",
    "key": "battery",
    "steps": [0.1, 0.6, 0.95],
    "steps_names": ["critical", "low", "discharging", "charged"]
    # [-Inf, 0.1) critical, [0.1, 0.6) low, [0.6, 0.95) discharging, [0.95, Inf) charged
}]
payload_data = {"bat": 0.3}  # low
```

The number of bits for this type is the exponent of the next power of
two of the length of `steps` + 1. In the example above it is 2 bits.

Input: `int|float`.
Additional keys:

- `steps` (array): Array listing the boundaries of each step.
- `steps_names` (array), optional: Names for each step. If not provided the names
  are created based on steps.

#### `categories`

Maps strings to categories: Eg:

```python
payload_spec = {
  "items": [{
    "type:": "categories",
    "key": "color",
    "categories": ["red", "green", "blue", "iridescent"],
}]
payload_data = {"color": "red"}  # low
```

The number of bits for this type is the exponent of the next power of
two of the length of `steps` + 1. In the example above it is 2 bits.
The category "unknown" is added to represent data that are not present
in the `categories` array.

Input: `string`.
Additional keys:

- `categories` (array): The array of categories strings.

## Functions

```python
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
```

```python
def decode(message, payload_spec):
    """
    Decodes a binary message according to payload_spec.

    Args:
        message (str): Binary string of the message.
        payload_spec (dict): Payload specifications.

    Returns:
        payload_data (dict): Payload data.
    """
```

```python
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

```

```python
def hex_decode(message, payload_spec):
    """
    Decodes an hex message according to payload_spec.

    Args:
        message (str): Hex string of the message.
        payload_spec (dict): Payload specifications.

    Returns:
        payload_data (dict): Payload data.
    """
```

## Command line usage

```python
# Encode data
cat payload_data | spos -p payload_spec.json

# Decode data
cat message | spos -d -p payload_spec.json
```

## Contributors

- [Arthur Lindemute](https://github.com/arthurlindemute)

## License

> SPOS - Small Payload Object Serializer
> Copyright (C) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
