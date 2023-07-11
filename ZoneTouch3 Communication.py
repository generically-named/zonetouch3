import socket
from collections import defaultdict
# initial_zone_states, continuous_update_zone_states, and update_zone_states are all information processors.
# they do the same thing but just interpret the data slightly differently, the setup for all 3 is fairly similar.
def initial_zone_states(tcpDump):
    ''' At the moment the zones are hard coded in, without re-configuring my ZT3 I can't verify
        which hexpair denotes the number of zones, my suspicion is pair 117 based on it being
        the only value in the header that is 7 when converted to ASCII. I'm sure ASCII is
        the correct choice as hexpairs 19-26 spell Polyaire and I could pull the name of each
        zone from the initialisation response as it lists the state, percentage and name for each zone.'''
    
    bytePairs = [tcpDump[i:i+2] for i in range(0, len(tcpDump), 2)] #splitting the hex data into byte pairs as this is how it should be treated.
    zoneStates = defaultdict(list)
    #Each of the below statement checks the state of the zones:
    zoneStates["zone0"].append(bytePairs[123][0] == '4') #If a zone is on the hexpair is 4?, if off it is 0? where ? is the zone number
    zoneStates["zone0"].append(int(bytePairs[124], 16))  #Check to get zone set percentage
    zoneStates["zone0"].append(int(bytePairs[126], 16))  #Check to get zone actual percentage

    zoneStates["zone1"].append(bytePairs[145][0] == '4')  
    zoneStates["zone1"].append(int(bytePairs[146], 16))  
    zoneStates["zone1"].append(int(bytePairs[148], 16))  

    zoneStates["zone2"].append(bytePairs[167][0] == '4')  
    zoneStates["zone2"].append(int(bytePairs[168], 16))  
    zoneStates["zone2"].append(int(bytePairs[170], 16))  

    zoneStates["zone3"].append(bytePairs[189][0] == '4')  
    zoneStates["zone3"].append(int(bytePairs[190], 16))  
    zoneStates["zone3"].append(int(bytePairs[192], 16))  

    zoneStates["zone4"].append(bytePairs[211][0] == '4')  
    zoneStates["zone4"].append(int(bytePairs[212], 16))  
    zoneStates["zone4"].append(int(bytePairs[214], 16))  
     
    zoneStates["zone5"].append(bytePairs[233][0] == '4')  
    zoneStates["zone5"].append(int(bytePairs[234], 16))  
    zoneStates["zone5"].append(int(bytePairs[236], 16))  

    zoneStates["zone6"].append(bytePairs[255][0] == '4')  
    zoneStates["zone6"].append(int(bytePairs[256], 16))  
    zoneStates["zone6"].append(int(bytePairs[258], 16))  

    return zoneStates

def continuous_update_zone_states(returnString: str):
    #This is used when the program is connected to the ZT3 and another client modifies zone settings
    bytePairs = [returnString[i:i+2] for i in range(0, len(returnString), 2)]
    print(bytePairs)
    zoneStates = defaultdict(list)

    zoneStates["zone0"].append(bytePairs[18][0] == '4')  #Same as initial zone states, this is the on/off determiner
    zoneStates["zone0"].append(int(bytePairs[19], 16))   #This is the set percentage, not actual percentage
    
    zoneStates["zone1"].append(bytePairs[26][0] == '4')  
    zoneStates["zone1"].append(int(bytePairs[27], 16))  

    zoneStates["zone2"].append(bytePairs[34][0] == '4')  
    zoneStates["zone2"].append(int(bytePairs[35], 16))  
    
    zoneStates["zone3"].append(bytePairs[42][0] == '4')  
    zoneStates["zone3"].append(int(bytePairs[43], 16))  
   
    zoneStates["zone4"].append(bytePairs[50][0] == '4')  
    zoneStates["zone4"].append(int(bytePairs[51], 16))  

    zoneStates["zone5"].append(bytePairs[58][0] == '4')  
    zoneStates["zone5"].append(int(bytePairs[59], 16))  

    zoneStates["zone6"].append(bytePairs[66][0] == '4')  
    zoneStates["zone6"].append(int(bytePairs[67], 16))  

    return zoneStates

def update_zone_states(returnString: str):
    bytePairs = [returnString[i:i+2] for i in range(0, len(returnString), 2)]
    print(bytePairs)
    zoneStates = defaultdict(list)
    #Same as continuous but data is located in different places

    zoneStates["zone0"].append(bytePairs[18][0] == '4')  #Same as initial zone states, this is the on/off determiner
    zoneStates["zone0"].append(int(bytePairs[21], 16))   #This is the set percentage, not actual percentage

    zoneStates["zone1"].append(bytePairs[26][0] == '4')  
    zoneStates["zone1"].append(int(bytePairs[29], 16)) 

    zoneStates["zone2"].append(bytePairs[34][0] == '4')  
    zoneStates["zone2"].append(int(bytePairs[37], 16)) 

    zoneStates["zone3"].append(bytePairs[42][0] == '4')  
    zoneStates["zone3"].append(int(bytePairs[45], 16))  

    zoneStates["zone4"].append(bytePairs[50][0] == '4')  
    zoneStates["zone4"].append(int(bytePairs[53], 16))  

    zoneStates["zone5"].append(bytePairs[58][0] == '4')  
    zoneStates["zone5"].append(int(bytePairs[61], 16))  

    zoneStates["zone6"].append(bytePairs[66][0] == '4')  
    zoneStates["zone6"].append(int(bytePairs[69], 16)) 

    return zoneStates

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
    

def user_input_zone():
    #For testing in commandline, used to have normal names before github publish
    uInput = input("Enter the zone name: (Example - zone0, zone1): ")
    zone_dict = {
        "zone0": "00",
        "zone1": "01",
        "zone2": "02",
        "zone3": "03",
        "zone4": "04",
        "zone5": "05",
        "zone6": "06"
    }
    zone = zone_dict[uInput]
    return zone

def user_input_zone_state():
    state = input("Enter the zone state (on/off/per): ").lower()  # add parentheses after lower
    originalState = state
    percentage = '00'
    if state == "on":
        state = '03'
    elif state == "off":
        state = '02'
    elif state == "per":
        state = '80'
        percentage = hex(int(input("Percentage: ")))[2:]  # add parentheses after lower
    return state, percentage, originalState

def hex_string(hex_data: list) -> str:
    hex_string = ""
    for i in hex_data:
        hex_string += i
    return hex_string

def send_hex_data(server_ip: str, server_port: int, hex_data: str) -> str:
    # Convert hex data to bytes
    data_bytes = bytes.fromhex(hex_data)
    print(hex_data)

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect((server_ip, server_port))
        
        # Send the data
        s.sendall(data_bytes)

        # Receive and print the response
        response_bytes = s.recv(1024)
        response_hex = response_bytes.hex().upper()
        return response_hex

def connect_ZT3(server_ip: str, server_port: int):
    initialQueryData = send_hex_data(server_ip, server_port, initialisation_data)
    #Initialisation data is what the ZT3 app sends to the ZT3 when opening communication, I just sniffed it and use it here.
    return initial_zone_states(initialQueryData)

def send_zone_information(zone, state, percentage):
    hex_data = ['55', '55', '55', 'aa', '80', 'b0', '12', 'c0', '00', '0c', '20', '00', '00', '00', '00', '04', '00', '01', '00', '03', '00', '00', '65', '79']
    hex_data[18] = zone
    hex_data[19] = state
    hex_data[20] = percentage
    
    data = hex_string(hex_data[4:22])
    checksum = hex_string(crc16_modbus(data))
    hex_data[22] = checksum[0:2]
    hex_data[23] = checksum[2:4]
    response_hex = send_hex_data(server_ip, server_port, hex_string(hex_data))
    return response_hex

#Global Variables (user changeable)
server_ip = "10.0.2.125"  # Replace this with the IP address of your network device


#Global Variables (set and unchanged)
initialisation_data = "555555aa90b0071f0002fff0ad8c" #This likely needs more research to work on anything by my ZT3, idk
hex_query_data = ["55", "55", "55", "aa", "90", "b0", "05", "1f", "00", "02", "ff", "f0"]
server_port = 7030

#Below code enables user input into python script and return of information to command line.
state, percentage, original_state = user_input_zone_state()
zone = user_input_zone()
response_hex = send_zone_information(zone, state, percentage)
print("Response from server as raw TCP hex:", )
print(update_zone_states(response_hex, typeCheck))