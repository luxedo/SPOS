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
import spos
from spos import random as srandom

from . import TestCase


class TestRandomMessageAndValue(TestCase):
    n_tests = 1000

    def evaluate_message(self, block_spec):
        block = spos.Block(block_spec)
        messages = set()
        values = list()
        for i in range(self.n_tests):
            message = srandom.block_random_message(block_spec)
            messages.add(message)
            values.append(block.bin_decode(message))

        if block.type == "pad":
            self.assertEqual(len(messages), 1)
            self.assertEqual(len(set(values)), 1)
            return

        if block.type not in ["array", "object"]:
            self.assertEqual(len(message) - 2, block.bits)

        self.assertGreaterEqual(len(messages), 2)
        self.assertGreaterEqual(len(values), 2)

    def evaluate_value(self, block_spec):
        block = spos.Block(block_spec)
        messages = set()
        values = list()
        for i in range(self.n_tests):
            value = srandom.block_random_value(block_spec)
            values.append(value)
            message = block.bin_encode(value)
            messages.add(message)

        if block.type not in ["array", "object"]:
            self.assertEqual(len(message) - 2, block.bits)

        if block.type == "pad":
            return
        self.assertGreaterEqual(len(messages), 2)
        self.assertGreaterEqual(len(values), 2)

    def test_seed(self):
        block_spec = {
            "key": "integer",
            "type": "integer",
            "bits": 16,
        }
        messages = set()
        values = list()
        block = spos.Block(block_spec)
        for i in range(self.n_tests):
            srandom.seed(1)
            message = srandom.block_random_message(block_spec)
            messages.add(message)
            values.append(block.bin_decode(message))

        if block.type not in ["array", "object"]:
            self.assertEqual(len(message) - 2, block.bits)

        self.assertEqual(len(messages), 1)
        self.assertEqual(len(set(values)), 1)

    def test_message_boolean(self):
        block_spec = {
            "key": "bool",
            "type": "boolean",
        }
        self.evaluate_message(block_spec)

    def test_message_binary(self):
        block_spec = {"key": "binary", "type": "binary", "bits": 16}
        self.evaluate_message(block_spec)

    def test_message_integer(self):
        block_spec = {"key": "integer", "type": "integer", "bits": 16}
        self.evaluate_message(block_spec)

    def test_message_float(self):
        block_spec = {"key": "float", "type": "float", "bits": 16}
        self.evaluate_message(block_spec)

    def test_message_pad(self):
        block_spec = {"key": "pad", "type": "pad", "bits": 16}
        self.evaluate_message(block_spec)

    def test_message_array(self):
        block_spec = {
            "key": "array",
            "type": "array",
            "length": 63,
            "blocks": {"key": "float", "type": "float", "bits": 4},
        }
        self.evaluate_message(block_spec)

    def test_message_array_fixed(self):
        block_spec = {
            "key": "array",
            "type": "array",
            "fixed": True,
            "length": 15,
            "blocks": {"key": "float", "type": "float", "bits": 4},
        }
        self.evaluate_message(block_spec)

    def test_message_object(self):
        block_spec = {
            "key": "object",
            "type": "object",
            "blocklist": [
                {"key": "float", "type": "float", "bits": 4},
                {"key": "boolean", "type": "boolean"},
                {
                    "key": "array",
                    "type": "array",
                    "length": 15,
                    "blocks": {"key": "integer", "type": "integer", "bits": 6},
                },
            ],
        }
        self.evaluate_message(block_spec)

    def test_message_string(self):
        block_spec = {"key": "string", "type": "string", "length": 16}
        self.evaluate_message(block_spec)

    def test_message_steps(self):
        block_spec = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 1, 2, 3, 4, 5],
        }
        self.evaluate_message(block_spec)

    def test_message_categories(self):
        block_spec = {
            "key": "categories",
            "type": "categories",
            "categories": ["one", "two", "three", "four"],
        }
        self.evaluate_message(block_spec)

    def test_value_boolean(self):
        block_spec = {
            "key": "bool",
            "type": "boolean",
        }
        self.evaluate_value(block_spec)

    def test_value_binary(self):
        block_spec = {"key": "binary", "type": "binary", "bits": 16}
        self.evaluate_value(block_spec)

    def test_value_integer(self):
        block_spec = {"key": "integer", "type": "integer", "bits": 16}
        self.evaluate_value(block_spec)

    def test_value_float(self):
        block_spec = {"key": "float", "type": "float", "bits": 16}
        self.evaluate_value(block_spec)

    def test_value_pad(self):
        block_spec = {"key": "pad", "type": "pad", "bits": 16}
        self.evaluate_value(block_spec)

    def test_value_array(self):
        block_spec = {
            "key": "array",
            "type": "array",
            "length": 63,
            "blocks": {"key": "float", "type": "float", "bits": 4},
        }
        self.evaluate_value(block_spec)

    def test_value_object(self):
        block_spec = {
            "key": "object",
            "type": "object",
            "blocklist": [
                {"key": "float", "type": "float", "bits": 4},
                {"key": "boolean", "type": "boolean"},
                {
                    "key": "array",
                    "type": "array",
                    "length": 15,
                    "blocks": {"key": "integer", "type": "integer", "bits": 6},
                },
            ],
        }
        self.evaluate_value(block_spec)

    def test_value_string(self):
        block_spec = {"key": "string", "type": "string", "length": 16}
        self.evaluate_value(block_spec)

    def test_value_steps(self):
        block_spec = {
            "key": "steps",
            "type": "steps",
            "steps": [0, 1, 2, 3, 4, 5],
        }
        self.evaluate_value(block_spec)

    def test_value_categories(self):
        block_spec = {
            "key": "categories",
            "type": "categories",
            "categories": ["one", "two", "three", "four"],
        }
        self.evaluate_value(block_spec)


class TestRandomPayload(TestCase):
    n_tests = 1000

    def evaluate(self, payload_spec):
        messages = set()
        for i in range(self.n_tests):
            message, payload_data = srandom.random_payload(payload_spec)
            messages.add(message)
            self.assertEqual(spos.encode(payload_data, payload_spec), message)
        self.assertGreaterEqual(len(messages), 2)

    def test_random_payload_0(self):
        payload_spec = {
            "name": "test random payload",
            "version": 1,
            "meta": {
                "crc8": True,
                "header": [
                    {"key": "root", "value": 123},
                    {"key": "xp", "type": "boolean"},
                ],
            },
            "body": [
                {"key": "holy", "type": "string", "length": 10},
                {"key": "version", "type": "integer", "value": 1, "bits": 6},
                {
                    "key": "buffer",
                    "type": "array",
                    "length": 255,
                    "blocks": {"key": "buf_val", "type": "integer", "bits": 8},
                },
                {"key": "date", "type": "float", "bits": 6},
            ],
        }
        self.evaluate(payload_spec)
