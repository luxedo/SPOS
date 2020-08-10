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
import spos
from . import TestCase


class TestValidatePayloadSpec(TestCase):
    def test_missing_version_key_error(self):
        payload_spec = {
            "name": "john",
            "body": [{"key": "jon", "type": "bool"}],
        }
        with self.assertRaises(KeyError):
            spos.bin_encode({"jon", False}, payload_spec)

    def test_missing_name_key_error(self):
        payload_spec = {
            "version": 1,
            "body": [{"key": "jon", "type": "bool"}],
        }
        with self.assertRaises(KeyError):
            spos.bin_encode({"jon", False}, payload_spec)

    def test_missing_body_key_error(self):
        payload_spec = {
            "name": "john",
            "version": 1,
        }
        with self.assertRaises(KeyError):
            spos.bin_encode({"jon", False}, payload_spec)

    def test_version_value_type_error(self):
        payload_spec = {
            "name": "john",
            "version": "wrong type",
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(TypeError):
            spos.bin_encode({"jon": False}, payload_spec)

    def test_name_value_type_error(self):
        payload_spec = {
            "name": 1,
            "version": 1,
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(TypeError):
            spos.bin_encode({"jon": False}, payload_spec)

    def test_body_value_type_error(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "body": {"key": "jon", "type": "boolean"},
        }
        with self.assertRaises(TypeError):
            spos.bin_encode({"jon": False}, payload_spec)

    def test_body_dupliacte_key_error(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "body": [
                {"key": "jon", "type": "boolean"},
                {"key": "jon", "type": "binary", "bits": 10},
            ],
        }
        with self.assertRaises(KeyError):
            spos.bin_encode({"jon": False}, payload_spec)

    def test_unexpected_keys(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "body": [{"key": "jon", "type": "boolean"}],
            "extra": "key",
        }
        with self.assertRaises(ValueError):
            spos.bin_encode({"jon": False}, payload_spec)

    def test_colliding_nested_keys(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "body": [
                {"key": "jon.fearless", "type": "boolean"},
                {
                    "key": "jon",
                    "type": "object",
                    "blocklist": [
                        {"key": "fearless", "type": "integer", "bits": 10}
                    ],
                },
            ],
        }
        with self.assertRaises(KeyError):
            spos.bin_encode({"jon": {"fearless": False}}, payload_spec)

    def test_empty_payload_spec_value_error(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "body": [],
        }
        with self.assertRaises(ValueError):
            spos.bin_encode({}, payload_spec)


class TestMeta(TestCase):
    def test_meta_wrong_type(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": "error",
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(ValueError):
            spos.bin_encode({"sensor_name": "abc", "jon": False}, payload_spec)

    def test_header(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {
                "header": [
                    {"key": "sensor_name", "type": "string", "length": 6}
                ]
            },
            "body": [{"key": "jon", "type": "boolean"}],
        }
        enc = spos.bin_encode(
            {"sensor_name": "abc", "jon": False}, payload_spec
        )
        dec = spos.bin_decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, {"jon": False})
        self.assertDict(
            dec_meta,
            {
                "name": "john",
                "version": 3,
                "header": {"sensor_name": "+++abc"},
            },
        )

    def test_header_key_collision_error(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {
                "header": [
                    {"key": "key1", "type": "string", "length": 6},
                    {"key": "key1", "type": "integer", "bits": 12},
                ]
            },
            "body": [{"key": "jon", "type": "boolean"}],
        }

        with self.assertRaises(KeyError):
            spos.bin_encode({"key1": "abc", "jon": False}, payload_spec)

    def test_encode_version(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {"encode_version": True, "version_bits": 4},
            "body": [{"key": "jon", "type": "boolean"}],
        }
        enc = spos.bin_encode(
            {"sensor_name": "abc", "jon": False}, payload_spec
        )
        dec = spos.bin_decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, {"jon": False})
        self.assertDict(
            dec_meta, {"name": "john", "version": 3},
        )

    def test_encode_version_type_error(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {"encode_version": "error", "version_bits": 4},
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(TypeError):
            spos.bin_encode({"sensor_name": "abc", "jon": False}, payload_spec)

    def test_version_bits_type_error(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {"encode_version": True, "version_bits": "error"},
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(TypeError):
            spos.bin_encode({"sensor_name": "abc", "jon": False}, payload_spec)

    def test_encode_version_mismatch_error(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {"encode_version": True, "version_bits": 4},
            "body": [{"key": "jon", "type": "boolean"}],
        }
        encoded = "0b00100000"
        with self.assertRaises(spos.VersionError):
            spos.bin_decode(encoded, payload_spec)

    def test_encode_version_missing_version_bits(self):
        payload_spec = {
            "name": "john",
            "version": 3,
            "meta": {"encode_version": True},
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(KeyError):
            spos.bin_encode({"jon": True}, payload_spec)

    def test_encode_version_version_overflow(self):
        payload_spec = {
            "name": "john",
            "version": 17,
            "meta": {"encode_version": True, "version_bits": 4},
            "body": [{"key": "jon", "type": "boolean"}],
        }
        with self.assertRaises(ValueError):
            spos.bin_encode({"jon": True}, payload_spec)

    def test_static_header(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "meta": {
                "encode_version": True,
                "version_bits": 4,
                "header": [{"key": "my key", "value": "hello!"}],
            },
            "body": [{"key": "jon", "type": "boolean"}],
        }
        t = {"jon": True}
        enc = spos.bin_encode(t, payload_spec)
        dec = spos.bin_decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, t)
        self.assertDict(
            dec_meta,
            {
                "name": payload_spec["name"],
                "version": payload_spec["version"],
                "header": {"my key": "hello!"},
            },
        )

    def test_static_header_key_key_error(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "meta": {
                "encode_version": True,
                "version_bits": 4,
                "header": [{"value": "hello!"}],
            },
            "body": [{"key": "jon", "type": "boolean"}],
        }
        t = {"jon": True}
        with self.assertRaises(KeyError):
            spos.bin_encode(t, payload_spec)

    def test_static_header_excess_keys_error(self):
        payload_spec = {
            "name": "john",
            "version": 1,
            "meta": {
                "encode_version": True,
                "version_bits": 4,
                "header": [
                    {"key": "my key", "value": "hello!", "error key": 1}
                ],
            },
            "body": [{"key": "jon", "type": "boolean"}],
        }
        t = {"jon": True}
        with self.assertRaises(KeyError):
            spos.bin_encode(t, payload_spec)


class TestEncodeDecode(TestCase):
    def test_get_subitems(self):
        payload_data = {"holy": {"grail": True, "deeper": {"mariana": 11}}}
        payload_spec = {
            "name": "test get subitems",
            "version": 1,
            "body": [
                {"key": "holy.grail", "type": "boolean"},
                {"key": "holy.deeper.mariana", "type": "integer", "bits": 6},
            ],
        }
        encoded = "0b10010110"
        decoded = {"holy": {"grail": True, "deeper": {"mariana": 11}}}
        enc = spos.bin_encode(payload_data, payload_spec)
        self.assertEqual(enc, encoded)
        dec = spos.bin_decode(encoded, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, decoded)
        self.assertDict(
            dec_meta,
            {"name": payload_spec["name"], "version": payload_spec["version"]},
        )

    def test_encode_static_value(self):
        payload_data = {"date": 0.221}
        payload_spec = {
            "name": "test encode",
            "version": 1,
            "meta": {"crc8": True},
            "body": [
                {
                    "key": "holy",
                    "type": "string",
                    "value": "abc",
                    "length": 10,
                },
                {"key": "type", "type": "integer", "value": 10, "bits": 6},
                {"key": "date", "type": "float", "bits": 6},
            ],
        }
        encoded = "0b11111011111011111011111011111011111011111001101001101101110000101000111000100100"
        decoded = {
            "holy": "+++++++abc",
            "type": 10,
            "date": 0.221,
        }
        enc = spos.bin_encode(payload_data, payload_spec)
        self.assertEqual(enc, encoded)
        dec = spos.bin_decode(encoded, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, decoded)
        self.assertDict(
            dec_meta,
            {
                "name": payload_spec["name"],
                "version": payload_spec["version"],
                "crc8": True,
            },
        )

    def test_bin_encode_decode_0(self):
        payload_data = {"holy": "grail", "buffer": [1, 2, 3, 4], "date": 0.98}
        payload_spec = {
            "name": "test encode",
            "version": 1,
            "meta": {"crc8": True},
            "body": [
                {"key": "holy", "type": "string", "length": 10},
                {"key": "version", "type": "integer", "value": 1, "bits": 6},
                {
                    "key": "buffer",
                    "type": "array",
                    "bits": 8,
                    "blocks": {"key": "buf_val", "type": "integer", "bits": 8},
                },
                {"key": "date", "type": "float", "bits": 6},
            ],
        }
        encoded = "0b111110111110111110111110111110100000101011011010100010100101000001000001000000000100000010000000110000010011111010000100"
        decoded = {
            "holy": "+++++grail",
            "version": 1,
            "buffer": [1, 2, 3, 4],
            "date": 0.98,
        }
        enc = spos.bin_encode(payload_data, payload_spec)
        self.assertEqual(enc, encoded)
        dec = spos.bin_decode(encoded, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, decoded)
        self.assertDict(
            dec_meta,
            {
                "name": payload_spec["name"],
                "version": payload_spec["version"],
                "crc8": True,
            },
        )

    def test_bin_encode_decode_1(self):
        payloads = [
            {
                "sent_yesterday": 0,
                "rpi_temperature": 25,
                "voltage": 8,
                "temperature": 23.3,
                "count_arm": 3,
                "count_eri": 5,
                "count_cos": 10,
                "count_fru": 15,
                "count_sac": 20,
            },
            {
                "sent_yesterday": 1,
                "rpi_temperature": 35,
                "voltage": 11.9,
                "temperature": 27.3,
                "count_arm": 10,
                "count_eri": 6,
                "count_cos": 12,
                "count_fru": 18,
                "count_sac": 24,
            },
            {
                "sent_yesterday": 0,
                "rpi_temperature": 51,
                "voltage": 12.5,
                "temperature": 11.8,
                "count_arm": 5,
                "count_eri": 20,
                "count_cos": 6,
                "count_fru": 7,
                "count_sac": 14,
            },
            {
                "sent_yesterday": 1,
                "rpi_temperature": 77,
                "voltage": 14.1,
                "temperature": 34.5,
                "count_arm": 60,
                "count_eri": 8,
                "count_cos": 16,
                "count_fru": 24,
                "count_sac": 32,
            },
            {
                "sent_yesterday": 0,
                "rpi_temperature": 55,
                "voltage": 4.5,
                "temperature": 24.5,
                "count_arm": 11,
                "count_eri": 5,
                "count_cos": 40,
                "count_fru": 3,
                "count_sac": 9,
            },
        ]

        payload_spec = {
            "name": "test payload 1",
            "version": 2,
            "meta": {"crc8": True},
            "body": [
                {"key": "pad", "type": "pad", "bits": 5},
                {
                    "key": "msg_version",
                    "type": "integer",
                    "value": 2,
                    "bits": 6,
                },
                {"key": "sent_yesterday", "type": "boolean"},
                {
                    "key": "rpi_temperature",
                    "type": "steps",
                    "steps": [30, 50, 75],
                    "steps_names": ["T<30", "30<T<50", "50<T<75", "T>75"],
                },
                {
                    "key": "voltage",
                    "type": "float",
                    "bits": 6,
                    "lower": 10,
                    "upper": 13,
                },
                {
                    "key": "temperature",
                    "type": "float",
                    "bits": 6,
                    "lower": 5,
                    "upper": 50,
                },
                {"key": "count_arm", "type": "integer", "bits": 6},
                {"key": "count_eri", "type": "integer", "bits": 6},
                {"key": "count_cos", "type": "integer", "bits": 6},
                {"key": "count_fru", "type": "integer", "bits": 6},
                {"key": "count_sac", "type": "integer", "bits": 6},
            ],
        }

        for payload_data in payloads:
            enc = spos.bin_encode(payload_data, payload_spec)
            dec = spos.bin_decode(enc, payload_spec)
            dec, dec_meta = dec["body"], dec["meta"]
            payload_data["sent_yesterday"] = bool(
                payload_data["sent_yesterday"]
            )
            payload_data["msg_version"] = 2
            if (
                payload_data["voltage"] < 10
            ):  # There's an underflow in the data
                payload_data["voltage"] = 10
            del dec["rpi_temperature"], payload_data["rpi_temperature"]
            self.assertDict(dec, payload_data, 3)
            self.assertDict(
                dec_meta,
                {
                    "name": payload_spec["name"],
                    "version": payload_spec["version"],
                    "crc8": True,
                },
            )

    def test_bin_encode_decode_2(self):
        payload_data = {
            "confidences": [0.9, 0.8, 0.7],
            "categories": ["bike", "bike", "scooter"],
            "timestamp": 1234567890,
            "voltage": 12,
            "temperature": 45,
            "rain": 20,
        }
        payload_spec = {
            "name": "test payload 2",
            "version": 2,
            "body": [
                {
                    "key": "confidences",
                    "type": "array",
                    "bits": 8,
                    "blocks": {
                        "key": "confidence",
                        "type": "float",
                        "bits": 4,
                    },
                },
                {
                    "key": "categories",
                    "type": "array",
                    "bits": 8,
                    "blocks": {
                        "key": "category",
                        "type": "categories",
                        "categories": ["bike", "skate", "scooter"],
                    },
                },
                {
                    "key": "msg_version",
                    "type": "integer",
                    "value": 1,
                    "bits": 6,
                },
                {"key": "timestamp", "type": "integer", "bits": 32},
                {
                    "key": "voltage",
                    "type": "float",
                    "bits": 8,
                    "lower": 10,
                    "upper": 13,
                },
                {
                    "key": "temperature",
                    "type": "float",
                    "bits": 8,
                    "lower": 5,
                    "upper": 50,
                },
                {"key": "rain", "type": "steps", "steps": [0, 10, 20, 30]},
            ],
        }
        enc = spos.bin_encode(payload_data, payload_spec)
        dec = spos.bin_decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        payload_data["msg_version"] = 1
        payload_data["rain"] = "20<=x<30"
        self.assertDict(dec, payload_data, 3)
        self.assertDict(
            dec_meta,
            {"name": payload_spec["name"], "version": payload_spec["version"]},
        )

    def test_hex_encode_decode_0(self):
        payload_data = {"holy": "grail", "buffer": [1, 2], "date": 0.98}
        payload_spec = {
            "name": "test encode",
            "version": 1,
            "body": [
                {"key": "holy", "type": "string", "length": 11},
                {
                    "key": "buffer",
                    "type": "array",
                    "bits": 8,
                    "blocks": {"key": "buf_val", "type": "integer", "bits": 9},
                },
                {"key": "date", "type": "float", "bits": 7},
            ],
        }
        decoded = {
            "holy": "++++++grail",
            "buffer": [1, 2],
            "date": 0.98,
        }
        enc = spos.encode(payload_data, payload_spec, "hex")
        dec = spos.decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, decoded)
        self.assertDict(
            dec_meta,
            {"name": payload_spec["name"], "version": payload_spec["version"]},
        )

    def test_encode_decode_0(self):
        payload_data = {"holy": "grail", "buffer": [1, 2, 3, 4], "date": 0.98}
        payload_spec = {
            "name": "test encode",
            "version": 1,
            "meta": {"crc8": True},
            "body": [
                {"key": "holy", "type": "string", "length": 10},
                {"key": "version", "type": "integer", "value": 1, "bits": 6},
                {
                    "key": "buffer",
                    "type": "array",
                    "bits": 8,
                    "blocks": {"key": "buf_val", "type": "integer", "bits": 8},
                },
                {"key": "date", "type": "float", "bits": 6},
            ],
        }
        encoded = b"\xfb\xef\xbe\xfa\n\xda\x8aPA\x00@\x80\xc1>\x84"
        decoded = {
            "holy": "+++++grail",
            "version": 1,
            "buffer": [1, 2, 3, 4],
            "date": 0.98,
        }
        enc = spos.encode(payload_data, payload_spec, "bytes")
        self.assertEqual(enc, encoded)
        dec = spos.decode(encoded, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, decoded)
        self.assertDict(
            dec_meta,
            {
                "name": payload_spec["name"],
                "version": payload_spec["version"],
                "crc8": True,
            },
        )

    def test_encode_decode_1(self):
        payload_spec = {
            "name": "test encode decode 1",
            "version": 2,
            "body": [
                {"key": "active", "type": "boolean"},
                {"key": "s3cr37", "type": "binary", "bits": 16},
                {"key": "timestamp", "type": "integer", "bits": 32},
                {"key": "wind speed", "type": "float", "bits": 7},
                {"key": "pad", "type": "pad", "bits": 7},
                {
                    "key": "sensor X",
                    "type": "object",
                    "blocklist": [
                        {"key": "value Y", "type": "integer", "bits": 6},
                        {"key": "value Z", "type": "float", "bits": 6},
                    ],
                },
                {"key": "user input", "type": "string", "length": 7},
                {
                    "key": "bird sightings",
                    "type": "steps",
                    "steps": [0, 5, 10, 15, 20],
                    "steps_names": [
                        "Bogey",
                        "Par",
                        "Birdie",
                        "Eagle",
                        "Albatross",
                        "Condor",
                    ],
                },
                {
                    "key": "battery",
                    "type": "categories",
                    "categories": ["critical", "low", "charged", "full"],
                },
                {
                    "key": "occurences",
                    "type": "array",
                    "bits": 6,
                    "blocks": {
                        "key": "species",
                        "type": "object",
                        "blocklist": [
                            {
                                "key": "name",
                                "type": "categories",
                                "categories": ["kitten", "doggo"],
                            },
                            {"key": "count", "type": "integer", "bits": 6},
                        ],
                    },
                },
            ],
        }
        payload_data = {
            "active": True,
            "s3cr37": "0b1011111011101111",
            "timestamp": 1584042831,
            "wind speed": 0.7,
            "sensor X": {"value Y": 10, "value Z": 0.3},
            "user input": "burguer",
            "bird sightings": 1337,
            "battery": "charged",
            "occurences": [
                {"name": "kitten", "count": 4},
                {"name": "doggo", "count": 10},
            ],
        }
        enc = spos.encode(payload_data, payload_spec)
        dec = spos.decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        payload_data["bird sightings"] = "Condor"
        self.assertDict(dec, payload_data)
        self.assertDict(
            dec_meta,
            {"name": payload_spec["name"], "version": payload_spec["version"]},
        )

    def test_decode_unknown_message_error(self):
        payload_spec = {
            "name": "test decode",
            "version": 2,
            "body": [{"key": "temperature", "type": "float", "bits": 10}],
        }
        with self.assertRaises(ValueError):
            spos.decode(["error"], payload_spec)

    def test_decode_string_message_error(self):
        payload_spec = {
            "name": "test decode",
            "version": 2,
            "body": [{"key": "temperature", "type": "float", "bits": 10}],
        }
        with self.assertRaises(ValueError):
            spos.decode("error string", payload_spec)

    def test_encode_decode_version_only(self):
        payload_spec = {
            "name": "test encode decode version only",
            "version": 17,
            "meta": {"encode_version": True, "version_bits": 6, "crc8": True},
            "body": [],
        }
        enc = spos.encode({}, payload_spec)
        dec = spos.decode(enc, payload_spec)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, {})
        self.assertDict(
            dec_meta,
            {
                "name": payload_spec["name"],
                "version": payload_spec["version"],
                "crc8": True,
            },
        )


class TestDecodeFromSpecs(TestCase):
    def setUp(self):
        self.payload_spec_0 = {
            "name": "my spec",
            "version": 0,
            "meta": {"encode_version": True, "version_bits": 6},
            "body": [
                {"key": "sensor x", "type": "boolean"},
                {"key": "sensor y", "type": "integer", "bits": 10},
            ],
        }
        self.payload_spec_1 = {
            "name": "my spec",
            "version": 1,
            "meta": {"encode_version": True, "version_bits": 6},
            "body": [
                {"key": "sensor a", "type": "float", "bits": 6},
                {"key": "sensor b", "type": "integer", "bits": 10},
            ],
        }
        self.payload_spec_2 = {
            "name": "my spec",
            "version": 2,
            "meta": {"encode_version": True, "version_bits": 6},
            "body": [
                {"key": "temperature", "type": "float", "bits": 10},
                {"key": "sunlight", "type": "float", "bits": 8},
            ],
        }
        self.payload_spec_3 = {
            "name": "my spec",
            "version": 3,
            "meta": {"encode_version": True, "version_bits": 6},
            "body": [
                {"key": "night", "type": "boolean"},
                {"key": "fog", "type": "boolean"},
            ],
        }
        self.specs = [
            self.payload_spec_0,
            self.payload_spec_1,
            self.payload_spec_2,
            self.payload_spec_3,
        ]

    def test_decode_from_specs(self):
        t = {"sensor x": False, "sensor y": 19}
        enc = spos.bin_encode(t, self.payload_spec_0)
        dec = spos.decode_from_specs(enc, self.specs)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, t)
        self.assertDict(
            dec_meta,
            {
                "name": self.payload_spec_0["name"],
                "version": self.payload_spec_0["version"],
            },
        )

        t = {"sensor a": 0.4, "sensor b": 500}
        enc = spos.bin_encode(t, self.payload_spec_1)
        dec = spos.decode_from_specs(enc, self.specs)
        dec, dec_meta = dec["body"], dec["meta"]
        self.assertDict(dec, t)
        self.assertDict(
            dec_meta,
            {
                "name": self.payload_spec_1["name"],
                "version": self.payload_spec_1["version"],
            },
        )

    def test_decode_from_specs_message_version_mismatch(self):
        t = {"sensor x": False, "sensor y": 19}
        enc = spos.bin_encode(t, self.payload_spec_0)
        enc = f"{enc[:2]}1{enc[3:]}"
        with self.assertRaises(spos.PayloadSpecError):
            spos.decode_from_specs(enc, self.specs)

    def test_decode_from_specs_name_mismatch(self):
        self.payload_spec_0["name"] = "not my spec"
        t = {"sensor x": False, "sensor y": 19}
        enc = spos.bin_encode(t, self.payload_spec_0)
        with self.assertRaises(spos.SpecsVersionError):
            spos.decode_from_specs(enc, self.specs)

    def test_decode_from_specs_duplicate_version(self):
        self.payload_spec_3["version"] = 1
        t = {"sensor x": False, "sensor y": 19}
        enc = spos.bin_encode(t, self.payload_spec_0)
        with self.assertRaises(spos.SpecsVersionError):
            spos.decode_from_specs(enc, self.specs)
