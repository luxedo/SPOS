#!/usr/bin/env python3
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
import argparse
import io
import json
import random
import re
import sys

from . import encode, decode, decode_from_specs, __version__
from .random import random_payload


def read_and_close_json(buf):
    d = json.load(buf)
    buf.close()
    return d


def _encode(input, output, payload_spec, format):
    payload_data = read_and_close_json(input)
    message = encode(payload_data, payload_spec, format)
    message = (
        message if format == "bytes" else bytes(message, encoding="ascii")
    )
    if hasattr(output, "name") and output.name == "<stdout>":
        sys.stdout.buffer.write(message)
    else:
        output.write(message)
    output.close()


def _decode(input, output, payload_specs, format, show_meta):
    if hasattr(input, "name") and input.name == "<stdin>":
        message = sys.stdin.buffer.read()
    else:
        message = input.read()
        input.close()

    if format != "bytes":
        message = message.decode("ascii")
        if format == "hex":
            message = (
                message
                if re.match("^0[xX][0-9a-fA-F]+$", message)
                else f"0x{message}"
            )
        elif format == "bin":
            message = (
                message if re.match("^0b[01]+$", message) else f"0b{message}"
            )
    if len(payload_specs) == 1:
        decoded = decode(message, payload_specs[0])
    else:
        decoded = decode_from_specs(message, payload_specs)
    if show_meta:
        output.write(
            bytes(json.dumps(decoded, indent=2) + "\n", encoding="utf-8")
        )
    else:
        output.write(
            bytes(
                json.dumps(decoded["body"], indent=2) + "\n", encoding="utf-8"
            )
        )
    output.close()


def parse(argv=None):
    parser = argparse.ArgumentParser(
        description="Spos is a tool for serializing objects."
    )

    parser.add_argument(
        "-d", "--decode", action="store_true", help="decodes a message."
    )
    parser.add_argument(
        "-p",
        "--payload-specs",
        metavar="PAYLOAD_SPEC",
        type=argparse.FileType("r"),
        nargs="+",
        required=True,
        help="json file payload specifications.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["bin", "hex", "bytes"],
        default="bytes",
        help="Output format",
    )
    random_group = parser.add_mutually_exclusive_group()
    random_group.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Creates a random message/decoded_message",
    )
    random_group.add_argument(
        "-I",
        "--random-input",
        action="store_true",
        help="Creates a random payload data input",
    )
    parser.add_argument(
        "-m",
        "--meta",
        action="store_true",
        help="Outputs the metadata when decoding",
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="?",
        type=argparse.FileType("rb"),
        default=sys.stdin.buffer,
        help="Input file",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        type=argparse.FileType("wb"),
        default=sys.stdout.buffer,
        help="Output file",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"spos v{__version__}",
        help="Software version",
    )

    return parser.parse_args(argv)


def main(args):
    payload_specs = [
        read_and_close_json(payload_spec)
        for payload_spec in args.payload_specs
    ]

    if args.random or args.random_input:
        args.input.detach()
        payload_specs = [random.choice(payload_specs)]
        message, payload_data = random_payload(
            payload_specs[0], output=args.format
        )
        if args.random_input:
            sys.stdout.write(json.dumps(payload_data, indent=2))
            return 0
        else:
            if args.decode:
                message = (
                    message
                    if isinstance(message, bytes)
                    else bytes(message, encoding="ascii")
                )
                args.input = io.BytesIO(message)
            else:
                args.input = io.BytesIO(
                    bytes(json.dumps(payload_data), encoding="ascii")
                )

    if args.decode:
        _decode(args.input, args.output, payload_specs, args.format, args.meta)
    else:
        if len(payload_specs) > 1:
            sys.stdout.write(
                "Specify only one specification (-p, --payload-spec) for encoding"
            )
            sys.exit(2)
        _encode(args.input, args.output, payload_specs[0], args.format)
    return 0
