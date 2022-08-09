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
import json
import sys
import tempfile

from spos import command
from spos import random as srandom

from . import TestCase, test_specs


class TestCommand(TestCase):
    test_specs = test_specs

    def test_parser(self):
        for name, payload_spec_file in self.test_specs.items():
            args = command.parse(["-p", payload_spec_file])
            for ps in args.payload_specs:
                ps.close()

    def test_encode_decode(self):
        for name, payload_spec_file in self.test_specs.items():
            with self.subTest(f"{name}_command_encode_decode"):
                with open(payload_spec_file, "r") as fp:
                    payload_spec = json.load(fp)
                self._test_encode_decode(
                    payload_spec_file, payload_spec, "bytes"
                )
                self._test_encode_decode(
                    payload_spec_file, payload_spec, "hex"
                )
                self._test_encode_decode(
                    payload_spec_file, payload_spec, "bin"
                )

    def _test_encode_decode(self, payload_spec_file, payload_spec, fmt):
        message, payload_data = srandom.random_payload(payload_spec, fmt)

        tmp_in = tempfile.NamedTemporaryFile()
        tmp_out = tempfile.NamedTemporaryFile()
        tmp_in.write(json.dumps(payload_data).encode("utf-8"))
        tmp_in.flush()
        args = command.parse(
            [
                "-p",
                payload_spec_file,
                "-i",
                tmp_in.name,
                "-o",
                tmp_out.name,
                "-f",
                fmt,
            ]
        )
        command.main(args)

        tmp_in.close()
        tmp_out.close()

        message = (
            message if isinstance(message, bytes) else message.encode("utf-8")
        )
        tmp_in = tempfile.NamedTemporaryFile()
        tmp_out = tempfile.NamedTemporaryFile()
        tmp_in.write(message)
        tmp_in.flush()
        args = command.parse(
            [
                "-d",
                "-p",
                payload_spec_file,
                "-i",
                tmp_in.name,
                "-o",
                tmp_out.name,
                "-f",
                fmt,
            ]
        )
        command.main(args)

        tmp_in.close()
        tmp_out.close()

    def test_random_encode_decode(self):
        for name, payload_spec_file in self.test_specs.items():
            with self.subTest(f"{name}_command_random_encode_decode"):
                self._test_random_encode_decode(payload_spec_file, "bytes")
                self._test_random_encode_decode(payload_spec_file, "hex")
                self._test_random_encode_decode(payload_spec_file, "bin")

    def _test_random_encode_decode(self, payload_spec_file, fmt):
        tmp_in = tempfile.NamedTemporaryFile()
        tmp_out = tempfile.NamedTemporaryFile()
        args = command.parse(
            [
                "-p",
                payload_spec_file,
                "-i",
                tmp_in.name,
                "-o",
                tmp_out.name,
                "-f",
                fmt,
                "-r",
            ]
        )
        command.main(args)

        tmp_in.close()
        tmp_out.close()

        tmp_in = tempfile.NamedTemporaryFile()
        tmp_out = tempfile.NamedTemporaryFile()
        args = command.parse(
            [
                "-p",
                payload_spec_file,
                "-i",
                tmp_in.name,
                "-o",
                tmp_out.name,
                "-f",
                fmt,
                "-r",
                "-d",
                "-m",
            ]
        )
        command.main(args)

        tmp_in.close()
        tmp_out.close()

        tmp_in = tempfile.NamedTemporaryFile()
        tmp_out = tempfile.NamedTemporaryFile()
        args = command.parse(
            [
                "-p",
                payload_spec_file,
                "-i",
                tmp_in.name,
                "-o",
                tmp_out.name,
                "-f",
                fmt,
                "-I",
            ]
        )
        command.main(args)

        tmp_in.close()
        tmp_out.close()

    def test_no_payload_specs_error(self):
        with self.assertRaises(SystemExit):
            command.parse([])

    def test_encode_with_multiple_specs_error(self):
        with self.assertRaises(SystemExit):
            args = command.parse(["-p"] + list(self.test_specs.values()))
            command.main(args)

    def test_payload_stats(self):
        args = command.parse(["-s", "-p"] + list(self.test_specs.values()))
        command.main(args)
