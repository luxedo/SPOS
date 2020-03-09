# SPOS

> **SPOS** stands for **Small Payload Object Serializer**.

`SPOS` is a tool for serializing objects. This tool focuses in
maintaining a consistent payload size while sacrificing precision.
Applications with limited bandwidth like [LoRa](https://lora-alliance.org/)
or [Globalstar](https://www.globalstar.com/en-us/) are ideal candidates
for `SPOS`.

## Quick Start

To encode data, `SPOS` needs two arguments to serialize the data: The `payload_data` to be serialized and the [payload specification](#Payload-Specification).

```python
import spos
payload_spec = {
  "name": "example payload",
  "version": "1.0.0",
  "items": [{
    "type": "integer",
    "name": "payload_version",
    "value": 1,  # 01
    "bits": 2
  }, {
    "type": "integer",
    "name": "integer 1",
    "key": "int_data",
    "bits": 6
  }, {
    "type": "float",
    "name": "float 1",
    "key": "float_data",
    "bits": 6
}]
payload_data = {
  "int_data": 13,    # 001101
  "float_data": 0.6  # 010011 (19/32 or 0.59375)
}

message = spos.encode(payload_data, payload_spec)
"0b010011010010011
```

Decoding data

```python
import spos
payload_spec = {
  "name": "example payload",
  "version": "1.0.0",
  "items": [{
    "type": "integer",
    "name": "payload_version",
    "value": 1,  # 01
    "bits": 2
  }, {
    "type": "integer",
    "name": "integer 1",
    "key": "int_data",
    "bits": 6
  }, {
    "type": "float",
    "name": "float 1",
    "key": "float_data",
    "bits": 6
}]
message = "0b010011010010011"
payload_data = spos.decode(message, payload_spec)
{
  "payload_version": 1,
  "int_data": 13,
  "float_data": 0.59375
}
```

## Payload Specification

The payload specification must contain the key `items`, which must be
an array containing objects that describe each `block` of the binary
serialization.

```python
payload_spec = {
  "items": [{
    "type:": "integer",
    "name": "temperature",
    "bits": 6,
    "key": "temp",
    "settings": {
      "offset": 273
}}]
```

Additional keys can be provided and keys not listed are ignored.

### Payload Specification keys

#### `items`

The array of `blocks` describing the message.

#### `name`

Message name

#### `version`

Message version

#### `defaults` (dict)

Overrides default `settings` for the `blocks`. `settings` declared
inside the `block` takes precedence over the defaults.

##### keys:

- `offset`
- `lower`
- `upper`
- `custom_alphabeth`

## Block Specification

The required keys for `block` objects are: `type`, `name`,
`key` or `value`, `bits`, and `settings`.

The value to be encoded is either a `key` in the `payload_data` object or
a statuc `value`.

Additional `settings` may be required according to the chosen `type`.

The encoded data is _big-endian_ and truncations occour in the least
significant bits when applicable. Data overflow are set to the maximum
value and underflow to the minimum.

### `name`

The name of the `block`.

### `bits`

Size of the block in bits.

### `key`

The key of the data in `payload_data`.

### `value`

A static value to be used in every message.

### `settings`

Additional settings for each type.

### `type`

There are 12 types avaliable for serializing data:
`boolean`, `binary`, `integer`, `float`, `string`, `array`, `object`,
`steps`, `categories`, `dynamic_array`, `pad` and `crc8`.

---

The basic types are:

#### `boolean`

Boolean value. For this type, the `bits` key is not required.

Settings: `None`.

#### `binary`

Binary value.

This data is truncated in the least significant bits if the size of
the string is bigger than `bits`.

Settins: `None`.

#### `integer`

Integer value. The value can be an int or hex.

Settings:

- `offset` (int): An integer to offset the final value. Default: 0.

#### `float`

Float value.

This type divides the interval between the `lower` and `upper`
boundaries in equal parts according to the avaliable `bits`. The
serialized value is the closest to the real one by default
("approximation": "round").

Settings:

- `lower` (float): Float lower boundary. Default 0.
- `upper` (float): Float upper boundary. Default 1.
- `approximation` (str): Float approximation method. Values can be: "round", "floor", "ceil". Default: "round"

#### `string`

String value. The bits argument is not required.

This data type encodes the string to base64. Characters outside the
[base64 index table](https://en.wikipedia.org/wiki/Base64#Base64_table)
are replaced with `/` (index 62) and spaces are replaced with `+`
(index 63).

The size in bits of this type is 6 \$ast; `length`.

Settings:

- `length` (int): String maximum length.
- `custom_alphabeth` (dict): Remaps the characters to another index.
  eg: Adding support for a `json` string but sacrificing the first 7
  indexes (ABCDEFG).

```python
payload_spec = {
  "items": [{
    "type:": "string",
    "name": "text",
    "length": 128,
    "key": "text1",
    "settings": {
      "custom_alphabeth": {
        0: "{",
        1: "}",
        2: "[",
        3: "]",
        4: '"',
        5: ',',
        6: '.',
      }
    }
}]

```

#### `array`

Array value with fixed length. The bits argument is not required.

The size in bits of this type is `length` \* `data` &rarr; `bits`.

Settings:

- `length` (int): Array maximum length.
- `blocks` (block): The `blocK` of the objects in the array.

#### `object`

Object value. Maps the data to an object. The bits argument is not required.

The size in bits of this type is the sum of sizes of blocks declared
for this `block`.

Settings:

- `items` (items): The `items` describing the object. The keys for
  the object will be the value of `name` in each `block`.

---

Advanced types:

#### `steps`

Maps a numeric value to named steps. Eg:

```python
payload_spec = {
  "items": [{
    "type:": "steps",
    "name": "battery",
    "key": "bat",
    "settings": {
      "steps": [0.1, 0.6, 0.95],
      "steps_names": ["critical", "low", "discharging", "charged"]
      # [-Inf, 0.1) critical, [0.1, 0.6) low, [0.6, 0.95) discharging, [0.95, Inf) charged
}}]
payload_data = {"bat": 0.3}  # low
```

The number of bits for this type is the exponent of the next power of
two of the length of `steps` + 1. In the example above it is 2 bits.

Settings:

- `steps` (array): Array listing the boundaries of each step.
- `steps_names` (array): Names for each step. If not provided the names
  are created based on steps.

#### `categories`

Maps strings to categories: Eg:

```python
payload_spec = {
  "items": [{
    "type:": "categories",
    "name": "color",
    "key": "color",
    "settings": {
      "categories": ["red", "green", "blue", "iridescent"],
}}]
payload_data = {"color": "red"}  # low
```

The number of bits for this type is the exponent of the next power of
two of the length of `steps` + 1. In the example above it is 2 bits.
The category "unknown" is added to represent data that are not present
in the `categories` array.

Settings:

- `categories` (array): The array of categories strings.

#### `dynamic_array`

#### `pad`

Pads the message. No data is collected from this block.
The bits argument is not reuired.

Settings: `None`.

#### `crc8`

Calculates the [CRC8](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
for the message. The bits argument is not required. The size in bits
for this `block` is always 8.

Settings: `None`.

## Command line usage

```python
# Encode data
cat payload_data | spos packet_spec.json

# Decode data
cat message | spos -d packet_spec.json
```

## Language Support

`SPOS` is built with Python3 as a library and a command.

## License

> SPOS - Small Payload Object Serializer
> Copyright (C) 2020 Luiz Eduardo Amaral
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
