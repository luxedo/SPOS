"""
Generates a payload based on a payload spec
"""

import os
import re
import random
import json

# =============================================#
# =============== CLASSES =====================#
# =============================================#


class Spec:
    def __init__(self, directory, filename):
        self.directory = directory
        self.filename = filename
        self.get_properties()
        self.get_spec()

    def get_properties(self):
        fsplit = self.filename.split("_")
        self.prefix = fsplit[0]
        self.protocol = fsplit[1]
        self.version = fsplit[2].split(".")[0]

    def get_spec(self):
        with open(os.path.join(self.directory, self.filename), "r") as fp:
            self.spec = json.load(fp)


class Payload:
    def __init__(self, spec, number, out):
        self.spec = spec
        self.number = number
        self.out = out
        self.payload = generate_payload(self.spec.spec)

    def export(self):
        dir = self.spec.protocol + "_" + self.spec.version
        if not os.path.exists(self.out):
            os.mkdir(self.out)
            os.mkdir(os.path.join(self.out, dir))
        elif not os.path.exists(os.path.join(self.out, dir)):
            os.mkdir(os.path.join(self.out, dir))

        with open(os.path.join(self.out, dir, str(self.number) + ".json"), "w") as fp:
            json.dump(self.payload, fp, indent=2)


# ============================================#
# =============== FUNCTIONS ==================#
# ============================================#
def generate_value(block):
    """
    Generates a random value within block specifications

    Args:
        item (dict): Spec's item containing its type and aditional infos
                     May contain a predefined value.
    Returns:
        1) random (?): Generated random value
        or
        2) value  (?): Predefined value given in block
    """
    if "value" in block:
        return block["value"]
    if block["type"] == "boolean":
        return random.randint(0, 1)

    elif block["type"] == "integer":
        return random.randint(0, 2 ** block["bits"])

    elif block["type"] == "float":
        if "lower" not in block:
            lower = 0
        else:
            lower = block["lower"]
        if "upper" not in block:
            upper = 2 ** block["bits"]
        else:
            upper = block["upper"]
        rand = lower - 1
        while rand < lower:
            rand = random.random() * upper
        return round(rand, 2)


def generate_payload(spec, object=False):
    """
    Generates a valid payload based on "spec" given

    Args:
        spec   (dict):
        object (bool): OPTIONAL. If true, looks for its items

    Returns:
        payload (dict): Final generated payload_data
    """
    payload = {}
    for key, value in spec.items():
        if key != "items" and not object:
            payload[key] = value
        else:
            for item in spec["items"]:
                if item["type"] != "object":
                    payload[item["key"]] = generate_value(item)
                else:
                    payload[item["key"]] = generate_payload(item, object=True)
    return payload


def get_specs(directory=".", prefix=".*", protocol=".*", version="v[0-9]+"):
    file_re = prefix + "_" + protocol + "_" + version + ".json"
    filenames = [file for file in os.listdir(directory) if re.match(file_re, file)]
    specs = []
    for filename in filenames:
        specs.append(Spec(directory, filename))
    return specs
