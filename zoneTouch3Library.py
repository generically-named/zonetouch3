import asyncio
import logging

_LOGGER = logging.getLogger('custom_components.zonetouch3')

def zone_on(zone_number: int):
    control_message_assembler(zone_number, "on")

def zone_off(zone_number: int):
    control_message_assembler(zone_number,"off")

def zone_set_percentage(zone_number: int, percentage: int):
    control_message_assembler(zone_number,"set",percentage)

async def control_message_assembler(zone_number: int, state: str, percentage = 0):
    zone_on_byte = int('00000011',2)
    zone_off_byte = int('00000010',2)
    zone_turbo_byte = int('00000101',2)
    zone_set_percentage_byte = int('10000000',2)
    zone_increase_percentage_byte = int('01100000',2)
    zone_decrease_percentage_byte = int('01000000',2)
    #Each control message has the same preliminary data before the control data,
    #when modifying a single zone.
    message = [0x80,0xB0,0x12,0xC0,0x00,0x0C,0x20,0x00,0x00,0x00,0x00,0x04,0x00,0x01]
    match state:
        case "on":
            #turning on a zone
            message.append(zone_number)
            message.append(zone_on_byte)
            message.append(0x00)
            message.append(0x00)
            formatted_message = format_message(message)
            _LOGGER.warning("Formatted message: "+formatted_message)
            return formatted_message

        case "off":
            #turning off a zone
            message.append(zone_number)
            message.append(zone_off_byte)
            message.append(0x00)
            message.append(0x00)
            return format_message(message)

        case "turbo":
            message.append(zone_number)
            message.append(zone_turbo_byte)
            message.append(0x00)
            message.append(0x00)
            return format_message(message)

        case "set":
            #setting a zone open percentage
            message.append(zone_number)
            message.append(zone_set_percentage_byte)
            message.append(percentage)
            message.append(0x00)
            return format_message(message)

        case "increase":
            #increasing zone open percentage 5%
            message.append(zone_number)
            message.append(zone_increase_percentage_byte)
            message.append(0x00)
            message.append(0x00)
            return format_message(message)

        case "decrease":
            #decreasing zone open percentage 5%
            message.append(zone_number)
            message.append(zone_decrease_percentage_byte)
            message.append(0x00)
            message.append(0x00)
            return format_message(message)

        case _:
            raise Exception("Invalid state provided to control_message_assembler")

def format_message(message: list):
    message_string = hex_string(message)
    crc_hex = crc16_modbus(message_string)
    final_message = "555555aa"+ message_string + crc_hex #first string is header, not to be included in CRC
    return final_message

def hex_string(hex_data: list) -> str:
    hex_string = ""
    for i in hex_data:
        hex_string += format(i,'02X')
    return hex_string

def crc16_modbus(data_hex: str) -> str:
        import struct
        #CRC16 checksum required to be appended to set commands with ZT3
        def calc_crc16(data: bytes, poly: int = 0xA001) -> int:
            crc = 0xFFFF
            for b in data:
                crc ^= b
                for _ in range(8):
                    if crc & 0x0001:
                        crc = (crc >> 1) ^ poly
                    else:
                        crc >>= 1
            return crc

        # Convert hex string to byte array
        data_bytes = bytes.fromhex(data_hex)
        
        # Calculate CRC16 checksum
        crc = calc_crc16(data_bytes)
        
        # Convert CRC to a hex string
        crc_hex = format(crc, "04X").upper()
        crc_hex_string = str(crc_hex[0]) + str(crc_hex[1])
        _LOGGER.warning(crc_hex)
        return crc_hex_string

def split_string_into_hexpairs(input_string):
    # List to hold chunks of two characters
    pair_list = []
    
    # Iterate through the string in steps of 2
    for i in range(0, len(input_string), 2):
        # Slice the string from index i to i+2
        chunk = input_string[i:i+2]
        # If chunk has two characters, add it to the list
        if len(chunk) == 2:
            pair_list.append(int(chunk,16))
        # If chunk has only one character, you could decide to append it or ignore
        # For now, let's append any single-character chunk as well
        elif len(chunk) == 1:
            pair_list.append(chunk)
    
    return pair_list

def process_status_response(data):
    hex_data = split_string_into_hexpairs(data)
    zone_count = hex_data[18]
    zones = []
    for i in range(0,zone_count):
        position = 18 + (i * 8)
        on_off_number_binary = format(hex_data[position], 'b')
        id = i
        status = "on" 
        turbo = False
        if on_off_number_binary[6:7] == "00":
            status = "off"
        elif on_off_number_binary[6:7] == "11":
            status = "on"
            turbo = True
        percent = int(hex_data[position+1])
        support_turbo = format(hex_data[position+6], 'b')[7] == "1"
        spill = format(hex_data[position+6], 'b')[1] == "1"
        zones.append({'id': id, 'state': status, 'percentage': percent, 'spill': spill, 'turbo': turbo,'support_turbo':support_turbo})
    return zones

def process_extended_response(data):
    # Convert the hex response string back to bytes
    hex_data = split_string_into_hexpairs(data)
    _LOGGER.debug(data)
    zone_count = hex_data[119]
    zones = []
    # Iterate over the zones
    for i in range(zone_count):
        byte_index = 123 + (i * 22)
        id = i
        
        # Extract the status and percentage
        status_byte = format(hex_data[byte_index],'08b')
        status_binary = status_byte[6:7]
        turbo = False
        status = "on"
        if status_binary[6:7] == "00":
            status = "off"
        elif status_binary[6:7] == "11":
            status = "on"
            turbo = True
        elif status_binary[6:7] == "01":
            status = "on"
        
        percent = hex_data[byte_index + 1]
        spill_turbo_binary = format(hex_data[byte_index + 6],'08b')
        supports_turbo = spill_turbo_binary[1:1] == "1"
        spill = spill_turbo_binary[7:7] == "1"
        name = ""
        for j in hex_data[byte_index +10:byte_index+22]:
            if j != 0x00:
                name += chr(j)

        zones.append({'id': id, 'name': name, 'state': status, 'percentage': percent, 'spill': spill, 'turbo': turbo, 'supports_turbo': supports_turbo})
    return zones

async def send_message(message: list, server_ip, server_port) -> str:
    # Convert hex data to bytes
    data_bytes = bytes.fromhex(message)

    # Connect to the server asynchronously
    reader, writer = await asyncio.open_connection(server_ip, server_port)

    try:
        # Send the data
        writer.write(data_bytes)
        await writer.drain()

        # Receive the response
        response_bytes = await reader.read(348)
        response_hex = response_bytes.hex().upper()
        return response_hex
    finally:
        # Close the connection
        writer.close()
        await writer.wait_closed()

def crc16_modbus(data_hex: str) -> str:
        import struct
        #CRC16 checksum required to be appended to set commands with ZT3
        def calc_crc16(data: bytes, poly: int = 0xA001) -> int:
            crc = 0xFFFF
            for b in data:
                crc ^= b
                for _ in range(8):
                    if crc & 0x0001:
                        crc = (crc >> 1) ^ poly
                    else:
                        crc >>= 1
            return crc

        # Convert hex string to byte array
        data_bytes = bytes.fromhex(data_hex)
        
        # Calculate CRC16 checksum
        crc = calc_crc16(data_bytes)
        
        # Convert CRC to a hex string
        crc_hex = format(crc, "04x").upper()
        return crc_hex