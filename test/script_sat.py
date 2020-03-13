import spos

values = [[0, 1, 0, 25, 8, 3, 5, 10, 15, 20, 25, '0b01001101'],
          [0, 2, 1, 35, 11, 10, 6, 12, 18, 24, 30, '0b10110110'],
          [0, 3, 0, 51, 12.5, 20.6, 7, 14, 21, 28, 35, '0b00100110'],
          [0, 4, 1, 77, 14, 60, 8, 16, 24, 32, 40, '0b00010010'],
          [0, 5, 0, 55.4, 11.5, 40.3, 9, 18, 27, 36, 45, '0b10100010']
         ]

items = [{"name": "FREE", "type": "pad", "settings": {"bits": 5}},
         {"name": "msg_version", "type": "integer", "settings": {"bits": 6}},
         {"name": "sent_yesterday", "type": "boolean"},
         {"name": "rpi_temperature", "type": "steps",
          "settings": {"steps": [30, 50, 75], "steps_names": ["T<30", "30<T<50", "50<T<75", "T>75"]}},
         {"name": "voltage", "type": "float", "settings": {"bits": 6, "lower": 10, "upper": 13}},
         {"name": "temperature", "type": "float", "settings": {"bits": 6, "lower": 5, "upper": 50}},
         {"name": "count_arm", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_eri", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_cos", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_fru", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_sac", "type": "integer", "settings": {"bits": 6}},
         {"name": "crc8", "type": "crc8"},
    ]

payloads = []
for report in values:
    payloads.append(spos.encode_items(report, items))

for payload in payloads:
    print(payload)
    print(spos.decode_items(payload, items))
    print("\n\n")




