# Table of Contents

- [SPOS](#spos)
  - [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Payload Specification](#payload-specification)
    - [Payload specification keys](#payload-specification-keys)
  - [Block](#block)
    - [Block keys](#block-keys)
    - [Types](#types)
      - [boolean](#boolean)
      - [binary](#binary)
      - [integer](#integer)
      - [float](#float)
      - [pad](#pad)
      - [array](#array)
      - [object](#object)
      - [string](#string)
      - [steps](#steps)
      - [categories](#categories)
  - [Encode and Decode Functions](#encode-and-decode-functions)
  - [Decoding messages of multiple versions](#decoding-messages-of-multiple-versions)
  - [Random payloads](#random-payloads)
  - [Command line usage](#command-line-usage)
  - [Contributors](#contributors)
  - [License](#license)

# SPOS

> **SPOS** stands for **Small Payload Object Serializer**.

[![codecov](https://codecov.io/gh/luxedo/spos/branch/master/graph/badge.svg)](https://codecov.io/gh/luxedo/spos)
[![CodeFactor](https://www.codefactor.io/repository/github/luxedo/spos/badge)](https://www.codefactor.io/repository/github/luxedo/spos)
[![PyPI version](https://badge.fury.io/py/spos.svg)](https://badge.fury.io/py/spos)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`SPOS` is a tool for serializing simple objects. This tool focuses in
maintaining a consistent payload size while sacrificing precision.
Applications with limited bandwidth like [LoRa](https://lora-alliance.org/)
or [Globalstar](https://www.globalstar.com/en-us/) are ideal candidates
for `SPOS`. `SPOS` has implementations for
python3 ([SPOS](https://github.com/luxedo/SPOS)) and
node.js ([node-SPOS](https://github.com/luxedo/node-SPOS)).

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
    "value": 2,      # 10
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
                     # padding 00
}

message = spos.encode(payload_data, payload_spec, output="bin")
"0b1000110101001100"
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

message = "0b1000110101001100"
decoded = spos.decode(message, payload_spec)
decoded
{
  "meta": {
    "name": "example payload",
    "version": 1,
  },
  "body": {
    "constant_data": 2,
    "int_data": 13,
    "float_data": 0.59375
  }
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
  "version": 1,
  "meta": {
    "encode_version": True,
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
}
```

### Payload specification keys

- **name** (string): String that briefly describes the payload.

- **version** (integer): Positive integer representing message version.

- **meta** (object): Additional configuration may be added to the payload, this
  is done by configuring values in the `meta` object. The following
  keys are allowed:

  - **encode_version** (boolean): `SPOS` will send the version as the first block
    of the message if set to `True`. This is useful when handling
    multiple messages with different versions. If this flag is set,
    `version_bits` becomess a required key.

  - **version_bits** (integer): Sets the number of bits used to encode
    the version in the header of the message.

  - **crc8** (boolean): If `True`, calculates the [CRC8](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
    (8bits) for the message and appends it to payload. The decoder also
    checks if the CRC8 is valid.

  - **header** (blocklist): The `header` should be an array of [blocks](#Block)
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

- **body** (blocklist): The `body` should be an array of [blocks](#Block) describing
  each section of the serialized message.

---

## Block

The block describes each portion of the serialized message by specifying
a `key` and a data `type`. `value` is an optional key. For each `type`
there might be aditional required keys and/or optional keys.

The value to be encoded is either a `key` in found in the `payload_data`
object or a static `value`.

The encoded data is _big-endian_ and truncations of data may occour in
the least significant bits when applicable. Data overflow is set to
the maximum value and underflow to the minimum.

### Block keys

- **key** (string): The key is used to name the value for the `block` in
  `payload_data`, and then to describe it's value in the decoded message.
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

- **type** (string): Data type for encoding the message. There are 10 avaliable types
  for serializing data: `boolean`, `binary`, `integer`, `float`, `pad`,
  `array`, `object`, `string`, `steps` and `categories`.

- **value** (any), optional: Static value for the `block`. Must be consistent with defined type.

- **alias** (string), optional: Overrides `key` when decoding. Does nothing when encoding. Eg:

```python
payload_spec = {
  "name": "example location access",
  "version": 2,
  "body": [{
    "type": "integer",
    "bits": 8,
    "key": "far.away.key"
    "alias": "my key",
  }]
payload_data = {
  "far": {
    "away": {
      "key": 255
    }
  }
}
message = spos.encode(payload_data, payload_spec, output="bin")
# "0b11111111"
spos.decode(message, payload_spec, output="bin")
# payload_data = {
#   "my key": 255
# }
```

---

### Types

#### boolean

Input: `boolean`, `integer` (0 ? False : True).

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

Additional keys:

- `bits` (int): Length of the block in bits
- `offset` (int), optional: An integer to offset the final value. Default: 0.
- `mode` (str): How to handle with underflows and overflows.
  Values can be: "truncate", "remainder". Default: "truncate"

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

An array containing `block` values. There are two avaliable modes for
this type, a fixed length array and a dynamic length array.

For fixed mode, the array always have `length` \* `blocks` &rarr; `bits`.
The input array must have `length` items.

The dynamic mode sends the current length of the array in the message,
so it's size is between ceil(log2(`length`)) `bits` for 0 items in the
array and ceil(log2(`length`)) + `length` \* `blocks` &rarr; `bits` for
a full array.

Input: An `array` of values allowed for the defined `block`.

Additional keys:

- `length` (int): Maximum length of the array.
- `fixed` (bool): Fixed length array. Default: false.
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
    # (-Inf, 0.1) critical, [0.1, 0.6) low, [0.6, 0.95) discharging, [0.95, Inf) charged
}]
payload_data = {"bat": 0.3}  # low
```

The number of bits for this type is the closest integer above
log2(length `steps` + 1). In the example above it is 2 bits.

An additional step **error** may be given on decoding if the message
overflows for this type.

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
    "error": "unknown"
}]
payload_data_1 = {"color": "red"}  # red
payload_data_2 = {"color": "brown"} # unknown
```

The `error` key is optional and creates a new category to represent data that
are not present in the `categories` array. Therefore, the number of bits for
this type is the closest integer above log2(length `categories` + 1).
In the example above it is 3 bits.

```python
payload_spec = {
  "body": [{
    "type:": "categories",
    "key": "color",
    "categories": ["red", "green", "blue", "iridescent"],
}]
payload_data_1 = {"color": "blue"}  # blue
payload_data_2 = {"color": "yellow"} # Raises an Error
```

If `error` is not defined (default value **None**), no extra category is created. In this case,
an error is raised if the value is not present in `categories`. The number of
bits is the closest integer above log2(length `categories`). In the example above, 2 bits.

It is also possible to assign an existing category to `error`. In this case, invalid
values are 'converted' to it and the number of bits is equal to the **None** case.

On decoding, an additional category **error** may be given if the message overflows
for this type.

Input: `string`.

Additional keys:

- `categories` (array): The array of categories strings.
- `error` (str), optional: Category to represent invalid values. Default: None

## Encode and Decode Functions

```python
def encode(payload_data, payload_spec, output="bin"):
    """
    Encodes a message from payload_data according to payload_spec.

    Args:
        payload_data (dict): Payload data.
        payload_spec (dict): Payload specification.
        output (str): Return format (bin, hex or bytes). default: "bin".

    Returns:
        message (bin | hex | bytes): Message.
    """
```

```python
def decode(message, payload_spec):
    """
    Decodes a message according to payload_spec.

    Args:
        message (bin | hex | bytes): Message.
        payload_spec (dict): Payload specification.

    Returns:
        body (dict): Payload data.
        meta (dict): Payload metadata.
    """
```

```python
def decode_from_specs(message, specs):
    """
    Decodes message from an avaliable pool of payload specificaions by
    matching message version with specification version.

    All the payload specifications must have `meta.encode_version` set
    and also the same value for `meta.version_bits`.

    Raises:
        PayloadSpecError: If message version is not in 'specs'
        SpecsVersionError: If names doesn't match or has duplicate versions
        Other Exceptions: For incorrect payload specification syntax.
            see spos.utils.validate_payload_spec and
            block.Block.validate_block_spec_keys

    Args:
        message (bin | hex | bytes): Message.

    Returns:
        body (dict): Payload data.
        meta (dict): Payload metadata.
    """
```

## Decoding messages of multiple versions

One possible use case of `SPOS` is to use the same bus to send messages
of different versions. If this is the case, `SPOS` will send the version
in the header of the message and the receiver can decode with an array
of expected payload specifications.

```python
specs = [
    payload_spec_v0,
    payload_spec_v1,
    payload_spec_v2,
    payload_spec_v3,
    payload_spec_v4,
]
decoded = spos.decode_from_specs(message, specs)
```

To do this, all payload specifications must set `encode_version` to
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

```bash
# Encode data
cat payload_data | spos -p payload_spec.json

# Decode data
cat message | spos -d -p payload_spec.json

# Avaliable Options
spos --help
usage: spos [-h] [-d] -p PAYLOAD_SPEC [PAYLOAD_SPEC ...] [-f {bin,hex,bytes}] [-r | -I] [-m] [-i [INPUT]]
            [-o [OUTPUT]] [-v]

Spos is a tool for serializing objects.

optional arguments:
  -h, --help            show this help message and exit
  -d, --decode          decodes a message.
  -p PAYLOAD_SPEC [PAYLOAD_SPEC ...], --payload-specs PAYLOAD_SPEC [PAYLOAD_SPEC ...]
                        json file payload specifications.
  -f {bin,hex,bytes}, --format {bin,hex,bytes}
                        Output format
  -r, --random          Creates a random message/decoded_message
  -I, --random-input    Creates a random payload data input
  -m, --meta            Outputs the metadata when decoding
  -s, --stats           Returns payload spec statistics
  -i [INPUT], --input [INPUT]
                        Input file
  -o [OUTPUT], --output [OUTPUT]
                        Output file
  -v, --version         Software version
```

## Contributors

- [Arthur Lindemute](https://github.com/arthurlindemute)

## License

> MIT License
>
> Copyright (c) 2020 [Luiz Eduardo Amaral](luizamaral306@gmail.com)
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
