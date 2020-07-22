# SPOS

> **SPOS** stands for **Small Payload Object Serializer**.

[![codecov](https://codecov.io/gh/luxedo/spos/branch/master/graph/badge.svg)](https://codecov.io/gh/luxedo/spos)
[![CodeFactor](https://www.codefactor.io/repository/github/luxedo/spos/badge)](https://www.codefactor.io/repository/github/luxedo/spos)
[![PyPI version](https://badge.fury.io/py/spos.svg)](https://badge.fury.io/py/spos)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

`SPOS` is a tool for serializing simple objects. This tool focuses in
maintaining a consistent payload size while sacrificing precision.
Applications with limited bandwidth like [LoRa](https://lora-alliance.org/)
or [Globalstar](https://www.globalstar.com/en-us/) are ideal candidates
for `SPOS`. `SPOS` has implementations for
python3 [SPOS](https://github.com/luxedo/SPOS) and
node.js [node-SPOS](https://github.com/luxedo/node-SPOS).

> In this document we will be using JSON notation to describe payload
> specifications and payload data. For each programming language there's
> usually an analogous data type for each notation. Eg:
> `object <=> dict`, `array <=> list`, etc.

## Quick Start

To encode data, `SPOS` needs two arguments: The `payload_data` (object)
to be serialized and the [payload specification](#Payload-Specification).

```python
import spos
payload_spec = {
  "name": "example payload",
  "version": 1,
  "body": [{
    "type": "integer",
    "key": "constant_data",
    "value": 2,  # 10
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

message = spos.encode(payload_data, payload_spec, output="bin")
"0b10001101010011"
```

Then, to decode the `message`:

```python
import spos
payload_spec = {
  "name": "example payload",
  "version": 1,
  "body": [{
    "type": "integer",
    "key": "constant_data",
    "value": 2,
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
message = "0b10001101010011"
payload_data, meta = spos.decode(message, payload_spec)

meta
{
  "name": "example payload",
  "version": 1,
}

payload_data
{
  "constant_data": 2,
  "int_data": 13,
  "float_data": 0.59375
}
```

## Installation

```
pip install spos
```

## Payload Specification

The payload specification consists of an object with four keys:
`name`, `version`, `meta`, an optional object witch describes additional
payload configuration and data, and `body` which describes the data
being sent.

```python
payload_spec = {
  "name": "my payload",
  "version": 1
  "meta": {
    "send_version": True,
    "version_bits": 4,
    "crc8": True,
    "header": [{
      "type": "integer",
      "key": "meaning",
      "value": 42
    }]
  },
  "body": [{
    "type:": "integer",
    "key": "temperature",
    "bits": 6,
    "offset": 273
  }],
  "my_key": "additional data"
}
```

### Payload specification keys

- **name**: String that briefly describes the payload.

- **version**: Positive integer representing message version.

- **meta**: Additional configuration may be added to the payload, this
  is done by configuring values in the `meta` object. The following
  keys are allowed:

  - **send_version**: `SPOS` will send the version as the first block
    of the message if set to `True`. This is useful when handling
    multiple messages with different versions. If this flag is set,
    `version_bits` becomess a required key.

  - **version_bits**: Integer that sets the number of bits used to
    encode the version in the header of the message.

  - **crc8**: If `True` calculates the [CRC8](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
    (8bits) for the message and appends it to payload. The decoder also
    checks if the CRC8 is valid.

  - **header**: The `header` should be an array of [blocks](#Block)
    which we call `blocklist`. In the `header` any static [value](#value)
    is not encoded in the message and when decoding the value is gathered
    from payload specification. This static block does not needs to
    specify any extra keys other than `key` and `value`. Eg:
    ```
    payload_spec = {
      "name": "payload meta",
      "version": 1,
      "meta": {
        "header": [{
            "key": "static key",
            "value": 1024
          }, {
            "key": "normal key",
            "type": "integer,
            "bits": 6
        }]
      }
    }
    ```

- **Body**: The `body` should be an array of [blocks](#Block) describing
  each section of the serialized message.

---

## Block

The block describes each portion of the serialized message by specifying
a `key` and a data `type`. `value` is an optional key. For each `type`
there might be aditional required keys and/or optional keys.

The value to be encoded is either a `key` in found in the `payload_data`
object or a statuc `value`.

The encoded data is _big-endian_ and truncations of data may occour in
the least significant bits when applicable. Data overflow is set to
the maximum value and underflow to the minimum.

### Block keys

- **key**: The key is used to get the value for the `block` in
  `payload_data`, and then to describe it's value in the decoded messasge.
  Optionally, the `key` can accesss a value in a nested objects using a
  dot `.` to separate the levels. Eg:

```python
payload_spec = {
  "name": "example nested value",
  "version": 10,
  "body": [{
    "type": "integer",
    "bits": 8,
    "key": "nested.value"  # HERE
  }]
payload_data = {
  "nested": {
    "value": 255
  }
}
spos.encode(payload_data, payload_spec, output="bin")
"0b11111111"
```

- **value**: Static value for the `block` (optional).

- **type**: Data type for encoding the message. There are 10 avaliable types
  for serializing data: `boolean`, `binary`, `integer`, `float`, `pad`,
  `array`, `object`, `string`, `steps`, and `categories`.

---

### Types

#### boolean

Input: `boolean`, `integer`.
Additional keys: `None`.

#### binary

The data can be a binary string or an hex string. Eg

```
"0b10101010"  # binary
"0xdeadbeef"  # hex
```

This data is truncated in the least significant bits if the size of
the string in binary is bigger than `bits`.

Input: `string`.
Additional keys:

- `bits` (int): length of the block in bits

#### integer

Input: `integer`.
Additional key:

- `bits` (int): length of the block in bits
- `offset` (int): An integer to offset the final value. Default: 0.

#### float

This type divides the interval between the `lower` and `upper`
boundaries in equal parts according to the avaliable `bits`. The
serialized value is the closest to the real one by default
("approximation": "round").

Input: `int|float`.
Additional keys:

- `bits` (int): length of the block in bits
- `lower` (int|float), optional: Float lower boundary. Default 0.
- `upper` (int|float), optional: Float upper boundary. Default 1.
- `approximation` (str), optional: Float approximation method.
  Values can be: "round", "floor", "ceil". Default: "round"

#### pad

Pads the message. No data is collected from this block.

Input: `None`.
Additional keys:

- `bits` (int): length of the block in bits

#### array

An array containing `block` values.

The size in bits of this type is between `bits` (0 length) and
`bits` + `length` \* `blocks` &rarr; `bits` (full array).

Input: An `array` of values allowed for the defined `block`.
Additional keys:

- `bits` (int): Number of bits to store the maximum length of the array.
- `blocks` (block): The `block` specification of the data in the array.

#### object

Maps the data to an object.

The size in bits of this type is the sum of sizes of blocks declared
for this `block`.

Input: `object`.
Additional keys:

- `blocklist` (blocklist): The `array` of `blocks` describing the object.

#### string

This data type encodes the input string to base64. Characters outside the
[base64 index table](https://en.wikipedia.org/wiki/Base64#Base64_table)
are replaced with `/` (index 62) and spaces are replaced with `+`
(index 63).

The size in bits of this type is 6 \* `length`.

Input: `string`.
Additional keys:

- `length` (int): String length.
- `custom_alphabeth` (object), optional: Remaps the characters to
  another index. eg: Adding support for `json` string but sacrificing
  the first 7 uppercase letters (ABCDEFG).

```python
payload_spec = {
  "body": [{
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

#### steps

Maps a numeric value to named steps. Eg:

```python
payload_spec = {
  "body": [{
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

#### categories

Maps strings to categories: Eg:

```python
payload_spec = {
  "body": [{
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

## Encode and Decode Functions

```python
def encode(payload_data, payload_spec, output="bin"):
    """
    Encodes a message from payload_data according to payload_spec.
    Returns the message as bytes.

    Args:
        payload_data (dict): Payload data.
        payload_spec (dict): Payload specification.
        output (str): Output format (bin, hex or bytes). default: "bin".

    Returns:
        message (bytes): Message.
    """
```

```python
def decode(message, payload_spec):
    """
    Decodes an hex message according to payload_spec.

    Args:
        message (bin | hex | bytes): Message.
        payload_spec (dict): Payload specification.

    Returns:
        payload_data (dict): Payload data.
        meta (dict): Payload data.
    """
```

## Decoding messages of multiple versions

One possible use case of `SPOS` is to use the same bus to send messages
of different versions. If this is the case, `SPOS` will send the version
in the header of the message and the receiver can decode with an array
of expected payload specifications.

```
specs = [
    payload_spec_v0,
    payload_spec_v1,
    payload_spec_v2,
    payload_spec_v3,
    payload_spec_v4,
]
payload_data, meta = spos.decode_from_specs(message, specs)
```

To do this, all payload specifications must set `send_version` to
`True`, set the same ammounts of `version_bits` and use the same `name`.
There must be only one specification for each version.

## Random payloads

It may be interesting to generate random payloads for testing. The
module `spos.random` contains functions to generate those messages
and payload data.

```python
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
