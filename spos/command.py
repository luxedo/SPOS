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
import argparse
import io
import json
import random
import re
import sys

from . import __version__, decode, decode_from_specs, encode, stats
from .random import random_payload
from .typing import List, Message, PayloadSpec


def read_and_close_json(buf):
    d = json.load(buf)
    buf.close()
    return d


def _encode(_input, output, payload_spec: PayloadSpec, fmt: str) -> None:
    payload_data = read_and_close_json(_input)
    message: Message = encode(payload_data, payload_spec, fmt)
    message = (
        message
        if isinstance(message, bytes)
        else bytes(message, encoding="ascii")
    )
    if hasattr(output, "name") and output.name == "<stdout>":
        sys.stdout.buffer.write(message)
    else:
        output.write(message)
    output.close()


def _decode(
    _input, output, payload_specs: List[PayloadSpec], fmt: str, show_meta: bool
) -> None:
    if hasattr(_input, "name") and _input.name == "<stdin>":
        message: Message = sys.stdin.buffer.read()
    else:
        message = _input.read()
        _input.close()

    if fmt != "bytes" and isinstance(message, bytes):
        message = message.decode("ascii")
        if fmt == "hex":
            message = (
                message
                if re.match("^0[xX][0-9a-fA-F]+$", message)
                else f"0x{message}"
            )
        elif fmt == "bin":
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
        "-s",
        "--stats",
        action="store_true",
        help="Returns payload spec statistics",
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

    if args.stats:
        sys.stdout.write(
            json.dumps([stats(ps) for ps in payload_specs], indent=2) + "\n"
        )
        return 0

    if args.random or args.random_input:
        args.input.detach()
        payload_specs = [random.choice(payload_specs)]
        message, payload_data = random_payload(
            payload_specs[0], output=args.format
        )

        if args.random_input:
            sys.stdout.write(json.dumps(payload_data, indent=2))
            return 0

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
