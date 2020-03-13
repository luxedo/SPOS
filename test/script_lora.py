import spos

values = [[],
         ]

items = [{"name": "confidence", "type": "array", "settings": {"bits": 4, "blocks": []}} ## EDIT
        
         {"name": "msg_version", "type": "integer", "settings": {"bits": 6}},
         {"name": "date", "type", "integer", "settings": {"bits": 32}},
         {"name": "rpi_temperature", "type": "float", "settings": {"bits": 8, "lower": 30, "upper": 90}},
         {"name": "voltage", "type": "float", "settings": {"bits": 8, "lower": 10, "upper": 13}},
         {"name": "temperature", "type": "float", "settings": {"bits": 8, "lower": 5, "upper": 50}},
         {"name": "count_arm", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_eri", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_cos", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_fru", "type": "integer", "settings": {"bits": 6}},
         {"name": "count_sac", "type": "integer", "settings": {"bits": 6}},
    ]

payloads = []
for report in values:
    payloads.append(spos.encode_items(report, items))

for payload in payloads:
    print(payload)
    print(spos.decode_items(payload, items))
    print("\n\n")




