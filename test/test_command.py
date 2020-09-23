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
            try:
                args = command.parse(["-p", payload_spec_file])
                for ps in args.payload_specs:
                    ps.close()
            except:  # noqa: E722
                self.fail(f"parser failing for spec {payload_spec_file}")

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

    def _test_encode_decode(self, payload_spec_file, payload_spec, format):
        message, payload_data = srandom.random_payload(payload_spec, format)

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
                format,
            ]
        )
        try:
            command.main(args)
        except:  # noqa: E722
            self.fail("error running command")
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
                format,
            ]
        )
        try:
            command.main(args)
        except:  # noqa: E722
            self.fail("error running command")
        tmp_in.close()
        tmp_out.close()

    def test_random_encode_decode(self):
        for name, payload_spec_file in self.test_specs.items():
            with self.subTest(f"{name}_command_random_encode_decode"):
                self._test_random_encode_decode(payload_spec_file, "bytes")
                self._test_random_encode_decode(payload_spec_file, "hex")
                self._test_random_encode_decode(payload_spec_file, "bin")

    def _test_random_encode_decode(self, payload_spec_file, format):
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
                format,
                "-r",
            ]
        )
        try:
            command.main(args)
        except:  # noqa: E722
            self.fail("error running command")
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
                format,
                "-r",
                "-d",
                "-m",
            ]
        )
        try:
            command.main(args)
        except:  # noqa: E722
            self.fail("error running command")
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
                format,
                "-I",
            ]
        )
        try:
            command.main(args)
        except:  # noqa: E722
            self.fail("error running command")
        tmp_in.close()
        tmp_out.close()

    def test_no_payload_specs_error(self):
        with self.assertRaises(SystemExit):
            command.parse([])

    def test_encode_with_multiple_specs_error(self):
        with self.assertRaises(SystemExit):
            args = command.parse(["-p"] + list(self.test_specs.values()))
            command.main(args)
