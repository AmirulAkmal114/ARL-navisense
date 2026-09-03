charto6bits = {
    '0': '000000', '1': '000001', '2': '000010', '3': '000011', '4': '000100',
    '5': '000101', '6': '000110', '7': '000111', '8': '001000', '9': '001001',
    ':': '001010', ';': '001011', '<': '001100', '=': '001101', '>': '001110',
    '?': '001111', '@': '010000', 'A': '010001', 'B': '010010', 'C': '010011',
    'D': '010100', 'E': '010101', 'F': '010110', 'G': '010111', 'H': '011000',
    'I': '011001', 'J': '011010', 'K': '011011', 'L': '011100', 'M': '011101',
    'N': '011110', 'O': '011111', 'P': '100000', 'Q': '100001', 'R': '100010',
    'S': '100011', 'T': '100100', 'U': '100101', 'V': '100110', 'W': '100111',
    '`': '101000', 'a': '101001', 'b': '101010', 'c': '101011', 'd': '101100',
    'e': '101101', 'f': '101110', 'g': '101111', 'h': '110000', 'i': '110001',
    'j': '110010', 'k': '110011', 'l': '110100', 'm': '110101', 'n': '110110',
    'o': '110111', 'p': '111000', 'q': '111001', 'r': '111010', 's': '111011',
    't': '111100', 'u': '111101', 'v': '111110', 'w': '111111'
}

country_dict = {
    201: "Albania", 202: "Andorra", 203: "Austria", 204: "Azores", 205: "Belgium", 206: "Belarus", 207: "Bulgaria", 208: "Vatican City State", 209: "Cyprus", 210: "Cyprus",
    211: "Germany", 212: "Cyprus", 213: "Georgia", 214: "Moldova", 215: "Malta", 216: "Armenia", 218: "Germany", 219: "Denmark", 220: "Denmark", 224: "Spain", 225: "Spain",
    226: "France", 227: "France", 228: "France", 229: "Malta", 230: "Finland", 231: "Faroe Islands", 232: "United Kingdom", 233: "United Kingdom", 234: "United Kingdom",
    235: "United Kingdom", 236: "Gibraltar", 237: "Greece", 238: "Croatia", 239: "Greece", 240: "Greece", 241: "Greece", 242: "Morocco", 243: "Hungary", 244: "Netherlands",
    245: "Netherlands", 246: "Netherlands", 247: "Italy", 248: "Malta", 249: "Malta", 250: "Ireland", 251: "Iceland", 252: "Liechtenstein", 253: "Luxembourg", 254: "Monaco",
    255: "Madeira", 256: "Malta", 257: "Norway", 258: "Norway", 259: "Norway", 261: "Poland", 262: "Montenegro", 263: "Portugal", 264: "Romania", 265: "Sweden", 266: "Sweden",
    267: "Slovak Republic", 268: "San Marino", 269: "Switzerland", 270: "Czech Republic", 271: "Turkey", 272: "Ukraine", 273: "Russia", 274: "Macedonia", 275: "Latvia",
    276: "Estonia", 277: "Lithuania", 278: "Slovenia", 279: "Serbia", 301: "Anguilla", 303: "Alaska", 304: "Antigua and Barbuda", 305: "Antigua and Barbuda", 306: "Antilles",
    307: "Aruba", 308: "Bahamas", 309: "Bahamas", 310: "Bermuda", 311: "Bahamas", 312: "Belize", 314: "Barbados", 316: "Canada", 319: "Cayman Islands", 321: "Costa Rica",
    323: "Cuba", 325: "Dominica", 327: "Dominican Republic", 329: "Guadeloupe", 330: "Grenada", 331: "Greenland", 332: "Guatemala", 334: "Honduras", 336: "Haiti",
    338: "United States of America", 339: "Jamaica", 341: "Saint Kitts and Nevis", 343: "Saint Lucia", 345: "Mexico", 347: "Martinique", 348: "Montserrat", 350: "Nicaragua",
    351: "Panama", 352: "Panama", 353: "Panama", 354: "Panama", 355: "Panama", 356: "Panama", 357: "Panama", 358: "Puerto Rico", 359: "El Salvador", 361: "Saint Pierre and Miquelon",
    362: "Trinidad and Tobago", 364: "Turks and Caicos Islands", 366: "United States of America", 367: "United States of America", 368: "United States of America",
    369: "United States of America", 370: "Panama", 371: "Panama", 372: "Panama", 373: "Panama", 374: "Panama", 375: "Saint Vincent and the Grenadines", 376: "Saint Vincent and the Grenadines",
    377: "Saint Vincent and the Grenadines", 378: "British Virgin Islands", 379: "United States Virgin Islands", 401: "Afghanistan", 403: "Saudi Arabia", 405: "Bangladesh",
    408: "Bahrain", 410: "Bhutan", 412: "China", 413: "China", 414: "China", 416: "Taiwan", 417: "Sri Lanka", 419: "India", 422: "Iran", 423: "Azerbaijan", 425: "Iraq",
    428: "Israel", 431: "Japan", 432: "Japan", 434: "Turkmenistan", 436: "Kazakhstan", 437: "Uzbekistan", 438: "Jordan", 440: "Korea", 441: "Korea", 443: "State of Palestine",
    445: "Democratic People's Republic of Korea", 447: "Kuwait", 450: "Lebanon", 451: "Kyrgyz Republic", 453: "Macao", 455: "Maldives", 457: "Mongolia", 459: "Nepal", 461: "Oman",
    463: "Pakistan", 466: "Qatar (State of)", 468: "Syrian Arab Republic", 470: "United Arab Emirates", 471: "United Arab Emirates", 472: "Tajikistan", 473: "Yemen", 475: "Yemen",
    477: "Hong Kong", 478: "Bosnia and Herzegovina", 501: "Adelie Land", 503: "Australia", 506: "Myanmar", 508: "Brunei Darussalam", 510: "Micronesia", 511: "Palau",
    512: "New Zealand", 514: "Cambodia", 515: "Cambodia", 516: "Christmas Island", 518: "Cook Islands", 520: "Fiji", 523: "Cocos (Keeling) Islands", 525: "Indonesia", 529: "Kiribati",
    531: "Lao People's Democratic Republic", 533: "Malaysia", 536: "Northern Mariana Islands", 538: "Marshall Islands", 540: "New Caledonia", 542: "Niue", 544: "Nauru",
    546: "French Polynesia", 548: "Philippines", 550: "Timor-Leste", 553: "Papua New Guinea", 555: "Pitcairn Island", 557: "Solomon Islands", 559: "American Samoa", 561: "Samoa",
    563: "Singapore", 564: "Singapore", 565: "Singapore", 566: "Singapore", 567: "Thailand", 570: "Tonga", 572: "Tuvalu", 574: "Viet Nam", 576: "Vanuatu", 577: "Vanuatu",
    578: "Wallis and Futuna Islands", 601: "South Africa", 603: "Angola", 605: "Algeria", 607: "Saint Paul and Amsterdam Islands", 608: "Ascension Island", 609: "Burundi", 610: "Benin",
    611: "Botswana", 613: "Cameroon", 615: "Congo", 616: "Comoros", 617: "Cabo Verde", 618: "Crozet Archipelago", 619: "Ivory Coast", 620: "Comoros", 621: "Djibouti", 622: "Egypt",
    624: "Ethiopia", 625: "Eritrea", 626: "Gabonese Republic", 627: "Ghana", 629: "Gambia", 630: "Guinea-Bissau", 631: "Equatorial Guinea", 632: "Guinea", 633: "Burkina Faso",
    634: "Kenya", 635: "Kerguelen Islands", 636: "Liberia", 637: "Liberia", 638: "South Sudan", 642: "Libya", 644: "Lesotho", 645: "Mauritius", 647: "Madagascar",
    649: "Mali", 650: "Mozambique", 654: "Mauritania", 655: "Malawi", 656: "Niger", 657: "Nigeria", 659: "Namibia", 660: "Reunion", 661: "Rwanda", 662: "Sudan", 663: "Senegal",
    664: "Seychelles", 665: "Saint Helena", 666: "Somalia", 667: "Sierra Leone", 668: "Sao Tome and Principe", 669: "Eswatini", 670: "Chad", 671: "Togolese Republic", 672: "Tunisia",
    674: "Tanzania", 675: "Uganda", 676: "Democratic Republic of the Congo", 677: "Tanzania", 678: "Zambia", 679: "Zimbabwe", 701: "Argentine Republic", 710: "Brazil", 720: "Bolivia",
    725: "Chile", 730: "Colombia", 735: "Ecuador", 740: "Falkland Islands", 745: "Guiana", 750: "Guyana", 755: "Paraguay", 760: "Peru", 765: "Suriname", 770: "Uruguay", 775: "Venezuela"
}


def nmea_payload_to_bitstring(payload):
    return ''.join(charto6bits.get(char, '') for char in payload)


def get_country_from_mmsi(mmsi):
    mid = int(str(mmsi)[:3])
    return country_dict.get(mid, "Unknown")


def decode_ais(bitstring):
    if len(bitstring) < 38:
        return {"error": "Invalid AIS message length"}

    msg_type = int(bitstring[0:6], 2)

    if msg_type in [1, 2, 3]:
        return decode_position_report(bitstring)
    elif msg_type == 5:
        return decode_static_voyage(bitstring)
    elif msg_type == 4:
        return decode_base_station_report(bitstring)
    elif msg_type == 6:
        return decode_binary_addressed(bitstring)
    elif msg_type == 7:
        return decode_binary_ack(bitstring)
    elif msg_type == 8:
        return decode_binary_broadcast(bitstring)
    elif msg_type == 10:
        return decode_utc_inquiry(bitstring)
    elif msg_type == 15:
        return decode_interrogation(bitstring)
    elif msg_type == 18:
        return decode_position_report_class_b(bitstring)
    elif msg_type == 19:
        return decode_extended_class_b_position(bitstring)
    elif msg_type == 24:
        return decode_static_data_class_b(bitstring)
    else:
        return {"message_type": msg_type, "info": "Unsupported AIS message type"}


def decode_utc_inquiry(bitstring):
    mmsi = int(bitstring[8:38], 2)
    dest_mmsi = int(bitstring[40:70], 2)

    return {
        "source": 0,
        "type": 10,
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "destination_mmsi": dest_mmsi
    }


def decode_interrogation(bitstring):
    mmsi = int(bitstring[8:38], 2)

    interrogations = []

    dest1 = int(bitstring[40:70], 2)
    msg_type1 = int(bitstring[70:76], 2)
    slot1 = int(bitstring[76:88], 2)

    interrogations.append({
        "destination_mmsi": dest1,
        "requested_type": msg_type1,
        "slot_offset": slot1
    })

    if len(bitstring) >= 160:
        dest2 = int(bitstring[88:118], 2)
        msg_type2 = int(bitstring[118:124], 2)
        slot2 = int(bitstring[124:136], 2)

        interrogations.append({
            "destination_mmsi": dest2,
            "requested_type": msg_type2,
            "slot_offset": slot2
        })

    return {
        "source": 0,
        "type": 15,
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "interrogations": interrogations
    }


def decode_binary_broadcast(bitstring):
    mmsi = int(bitstring[8:38], 2)

    dac = int(bitstring[40:50], 2)
    fi = int(bitstring[50:56], 2)

    binary_data = bitstring[56:]

    return {
        "source": 0,
        "type": 8,
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "dac": dac,
        "fi": fi,
        "binary_payload": binary_data
    }


def decode_binary_addressed(bitstring):
    mmsi = int(bitstring[8:38], 2)

    dest_mmsi = int(bitstring[40:70], 2)
    sequence = int(bitstring[70:72], 2)

    dac = int(bitstring[72:82], 2)
    fi = int(bitstring[82:88], 2)

    binary_data = bitstring[88:]

    return {
        "source": 0,
        "type": 6,
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "destination_mmsi": dest_mmsi,
        "sequence": sequence,
        "dac": dac,
        "fi": fi,
        "binary_payload": binary_data
    }


def decode_binary_ack(bitstring):
    mmsi = int(bitstring[8:38], 2)

    acknowledgements = []

    start = 40
    while start + 32 <= len(bitstring):
        seq = int(bitstring[start:start + 2], 2)
        dest_mmsi = int(bitstring[start + 2:start + 32], 2)

        if dest_mmsi != 0:
            acknowledgements.append({
                "dest_mmsi": dest_mmsi,
                "sequence": seq
            })

        start += 32

    return {
        "source": 0,
        "type": 7,
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "acks": acknowledgements
    }


def decode_position_report(bitstring):
    mmsi = int(bitstring[8:38], 2)
    lon = int(bitstring[61:89], 2)
    lat = int(bitstring[89:116], 2)
    lon = (lon if lon < (1 << 27) else lon - (1 << 28)) / 600000.0
    lat = (lat if lat < (1 << 26) else lat - (1 << 27)) / 600000.0

    return {
        "source": 0,
        "type": int(bitstring[0:6], 2),
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "status": int(bitstring[38:42], 2),
        "turn": int(bitstring[42:50], 2),
        "speed": int(bitstring[50:60], 2) / 10.0,
        "lon": lon,
        "lat": lat,
        "course": int(bitstring[116:128], 2) / 10.0,
        "heading": int(bitstring[128:137], 2),
        "channel": "A",
    }


def decode_base_station_report(bitstring):
    mmsi = int(bitstring[8:38], 2)

    year = int(bitstring[38:52], 2)
    month = int(bitstring[52:56], 2)
    day = int(bitstring[56:61], 2)
    hour = int(bitstring[61:66], 2)
    minute = int(bitstring[66:72], 2)
    second = int(bitstring[72:78], 2)

    accuracy = int(bitstring[78], 2)

    lon_raw = int(bitstring[79:107], 2)
    lat_raw = int(bitstring[107:134], 2)

    lon = (lon_raw if lon_raw < (1 << 27) else lon_raw - (1 << 28)) / 600000.0
    lat = (lat_raw if lat_raw < (1 << 26) else lat_raw - (1 << 27)) / 600000.0

    epfd = int(bitstring[134:138], 2)
    raim = int(bitstring[148], 2)
    radio = int(bitstring[148:168], 2)

    return {
        "source": 0,
        "type": 4,
        "mmsi": mmsi,
        "country": get_country_from_mmsi(mmsi),
        "utc": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second
        },
        "accuracy": accuracy,
        "lon": lon,
        "lat": lat,
        "epfd": epfd,
        "raim": raim,
        "radio": radio
    }


def decode_static_voyage(bitstring):
    mmsi = int(bitstring[8:38], 2)
    imo = int(bitstring[40:70], 2)
    callsign = ''.join([chr(int(bitstring[i:i + 6], 2) + 64) for i in range(70, 112, 6)]).strip('@')
    vessel_name = ''.join([chr(int(bitstring[i:i + 6], 2) + 64) for i in range(112, 232, 6)]).strip('@')
    ship_type = int(bitstring[232:240], 2)

    return {
        "message_type": 5,
        "mmsi": mmsi,
        "imo": imo,
        "callsign": callsign,
        "vessel_name": vessel_name,
        "ship_type": ship_type
    }


def decode_position_report_class_b(bitstring):
    mmsi = int(bitstring[8:38], 2)
    lon = int(bitstring[57:85], 2)
    lat = int(bitstring[85:112], 2)
    lon = (lon if lon < (1 << 27) else lon - (1 << 28)) / 600000.0
    lat = (lat if lat < (1 << 26) else lat - (1 << 27)) / 600000.0

    return {
        "source": 0,
        "type": 18,
        "mmsi": mmsi,
        "speed": int(bitstring[46:56], 2) / 10.0,
        "lon": lon,
        "lat": lat,
        "course": int(bitstring[112:124], 2) / 10.0,
        "heading": int(bitstring[124:133], 2),
        "timestamp": int(bitstring[133:139], 2)
    }


def decode_static_data_class_b(bitstring):
    mmsi = int(bitstring[8:38], 2)
    part_number = int(bitstring[38:40], 2)

    if part_number == 0:
        vessel_name = ''.join([chr(int(bitstring[i:i + 6], 2) + 64) for i in range(40, 160, 6)]).strip('@')
        return {
            "message_type": 24,
            "part": 0,
            "mmsi": mmsi,
            "vessel_name": vessel_name
        }
    elif part_number == 1:
        callsign = ''.join([chr(int(bitstring[i:i + 6], 2) + 64) for i in range(40, 70, 6)]).strip('@')
        ship_type = int(bitstring[70:78], 2)
        return {
            "message_type": 24,
            "part": 1,
            "mmsi": mmsi,
            "callsign": callsign,
            "ship_type": ship_type
        }
    return {"message_type": 24, "part": part_number, "mmsi": mmsi, "info": "Unknown part"}


def decode_extended_class_b_position(bitstring):
    mmsi = int(bitstring[8:38], 2)
    sog = int(bitstring[46:56], 2) / 10.0
    lon_raw = int(bitstring[57:85], 2)
    lat_raw = int(bitstring[85:112], 2)
    cog = int(bitstring[112:124], 2) / 10.0
    heading = int(bitstring[124:133], 2)
    timestamp = int(bitstring[133:139], 2)

    lon = (lon_raw if lon_raw < (1 << 27) else lon_raw - (1 << 28)) / 600000.0
    lat = (lat_raw if lat_raw < (1 << 26) else lat_raw - (1 << 27)) / 600000.0

    name = ''.join([chr(int(bitstring[i:i + 6], 2) + 64) for i in range(143, 263, 6)]).strip('@')
    ship_type = int(bitstring[263:271], 2)
    dimension_to_bow = int(bitstring[271:280], 2)
    dimension_to_stern = int(bitstring[280:289], 2)
    dimension_to_port = int(bitstring[289:295], 2)
    dimension_to_starboard = int(bitstring[295:301], 2)

    return {
        "message_type": 19,
        "mmsi": mmsi,
        "speed_over_ground": sog,
        "longitude": lon,
        "latitude": lat,
        "course_over_ground": cog,
        "true_heading": heading,
        "timestamp": timestamp,
        "vessel_name": name,
        "ship_type": ship_type,
        "dimension_to_bow": dimension_to_bow,
        "dimension_to_stern": dimension_to_stern,
        "dimension_to_port": dimension_to_port,
        "dimension_to_starboard": dimension_to_starboard
    }
