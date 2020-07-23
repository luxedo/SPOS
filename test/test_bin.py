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
import subprocess
import tempfile

from . import TestCase


class TestSposBin(TestCase):
    test_files = {
        "test_0": {
            "spec": "test/json/test_spec_0.json",
            "payload": "test/json/test_payload_0.json",
            "expected": "test/json/test_expected_0.json",
            "message": "test/json/test_message_0.bin",
        },
        "test_1": {
            "spec": "test/json/test_spec_1.json",
            "payload": "test/json/test_payload_1.json",
            "expected": "test/json/test_expected_1.json",
            "message": "test/json/test_message_1.bin",
        },
    }

    def encode(self, spec, payload, output):
        proc = subprocess.run(
            ["spos", "-f", output, "-p", spec, payload],
            stdout=subprocess.PIPE,
        )
        return proc.stdout

    def decode(self, spec, message, output):
        proc = subprocess.run(
            ["spos", "-d", "-f", output, "-p", spec, message],
            stdout=subprocess.PIPE,
        )
        return proc.stdout

    def test_encode(self):
        for name, files in self.test_files.items():
            with self.subTest(f"{name}_encode_bytes"):
                message = self.encode(files["spec"], files["payload"], "bytes")
                with open(files["message"], "rb") as fp:
                    self.assertEqual(message, fp.read())

            with self.subTest(f"{name}_encode_hex"):
                message = self.encode(
                    files["spec"], files["payload"], "hex"
                ).decode("ascii")
                with open(files["message"], "rb") as fp:
                    expected = f"0x{fp.read().hex().upper()}"
                    self.assertEqual(message, expected)

            with self.subTest(f"{name}_encode_bin"):
                message = self.encode(
                    files["spec"], files["payload"], "bin"
                ).decode("ascii")
                with open(files["message"], "rb") as fp:
                    expected = fp.read().hex()
                    bits = len(expected) * 4
                    expected = bin(int(expected, 16))[2:]
                    expected = "0b" + expected.zfill(bits)
                    self.assertEqual(message, expected)

    def test_decode(self):
        for name, files in self.test_files.items():
            with self.subTest(f"{name}_decode_bytes"):
                data = self.decode(
                    files["spec"], files["message"], "bytes"
                ).decode("ascii")
                with open(files["expected"], "r") as fp:
                    self.assertDict(json.loads(data)["body"], json.load(fp))

            with self.subTest(f"{name}_decode_hex"):
                tmp = tempfile.NamedTemporaryFile()
                with open(files["message"], "rb") as fp:
                    tmp.write(bytes(fp.read().hex(), encoding="ascii"))
                tmp.seek(0)
                data = self.decode(files["spec"], tmp.name, "hex").decode(
                    "ascii"
                )
                tmp.close()
                with open(files["expected"], "r") as fp:
                    self.assertDict(json.loads(data)["body"], json.load(fp))

            with self.subTest(f"{name}_decode_bin"):
                tmp = tempfile.NamedTemporaryFile()
                with open(files["message"], "rb") as fp:
                    bin_message = fp.read().hex()
                    bits = len(bin_message) * 4
                    bin_message = bin(int(bin_message, 16))[2:]
                    bin_message = bin_message.zfill(bits)
                    tmp.write(bytes(bin_message, encoding="ascii"))
                tmp.seek(0)
                data = self.decode(files["spec"], tmp.name, "bin").decode(
                    "ascii"
                )
                tmp.close()
                with open(files["expected"], "r") as fp:
                    self.assertDict(json.loads(data)["body"], json.load(fp))
