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
import re
import subprocess

from spos import random as srandom
import spos
from . import TestCase, test_specs


class TestSposBin(TestCase):
    n_random = 20
    test_specs = test_specs

    def stdin_encode(self, spec, payload, output):
        proc = subprocess.run(
            ["bin/spos", "-f", output, "-p", spec],
            stdout=subprocess.PIPE,
            input=json.dumps(payload).encode("utf-8"),
        )
        return proc.stdout, proc

    def stdin_decode(self, spec, message, output):
        proc = subprocess.run(
            ["bin/spos", "-d", "-m", "-f", output, "-p", spec],
            stdout=subprocess.PIPE,
            input=message,
        )
        return proc.stdout, proc

    def random_encode(self, spec, output):
        proc = subprocess.run(
            ["bin/spos", "-r", "-f", output, "-p", spec],
            stdout=subprocess.PIPE,
        )
        return proc.stdout, proc

    def random_decode(self, spec, output):
        proc = subprocess.run(
            ["bin/spos", "-r", "-d", "-f", output, "-p", spec],
            stdout=subprocess.PIPE,
        )
        return proc.stdout, proc

    def test_random_encode(self):
        for name, payload_spec_file in self.test_specs.items():
            for i in range(self.n_random):
                with self.subTest(f"{name}_random_encode{i}"):
                    message, proc = self.random_encode(
                        payload_spec_file, "bytes"
                    )
                    self.assertEqual(proc.returncode, 0)
                    message, proc = self.random_encode(
                        payload_spec_file, "hex"
                    )
                    self.assertEqual(proc.returncode, 0)
                    message, proc = self.random_encode(
                        payload_spec_file, "bin"
                    )
                    self.assertEqual(proc.returncode, 0)

    def test_random_decode(self):
        for name, payload_spec_file in self.test_specs.items():
            for i in range(self.n_random):
                with self.subTest(f"{name}_random_decode_{i}"):
                    data, proc = self.random_decode(payload_spec_file, "bytes")
                    self.assertEqual(proc.returncode, 0)
                    data, proc = self.random_decode(payload_spec_file, "hex")
                    self.assertEqual(proc.returncode, 0)
                    data, proc = self.random_decode(payload_spec_file, "bin")
                    self.assertEqual(proc.returncode, 0)

    def test_random_encode_then_decode(self):
        for name, payload_spec_file in self.test_specs.items():
            for i in range(self.n_random):
                with self.subTest(f"{name}_random_encode_then_decode{i}"):
                    with open(payload_spec_file, "r") as fp:
                        payload_spec = json.load(fp)
                    self._test_random_encode_then_decode(
                        payload_spec, payload_spec_file, "bytes"
                    )
                    self._test_random_encode_then_decode(
                        payload_spec, payload_spec_file, "bin"
                    )
                    self._test_random_encode_then_decode(
                        payload_spec, payload_spec_file, "hex"
                    )

    def _test_random_encode_then_decode(
        self, payload_spec, payload_spec_file, fmt
    ):
        message, payload_data = srandom.random_payload(payload_spec, fmt)
        message_bin, proc = self.stdin_encode(
            payload_spec_file, payload_data, fmt
        )
        message_b = (
            message.encode("utf-8") if isinstance(message, str) else message
        )
        self.assertEqual(message_b, message_bin)
        payload_bin, proc = self.stdin_decode(
            payload_spec_file, message_b, fmt
        )
        self.assertEqual(
            spos.decode(message, payload_spec), json.loads(payload_bin),
        )

    def test_version(self):
        proc = subprocess.run(["bin/spos", "-v"], stdout=subprocess.PIPE,)
        self.assertTrue(
            re.match(
                "^spos v[0-9]+[.][0-9]+[.][0-9]+(-([ab]|rc[0-9]+))?$",
                str(proc.stdout, "utf-8").strip(),
            )
            is not None
        )


# class CandyTestCase(unittest.TestCase):
#     def testCandy(self):
#         candyOutput = candy.candy()
#
#         assert candyOutput == "candy"
