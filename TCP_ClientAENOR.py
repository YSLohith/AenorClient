import socket
import time


def add_dle(input_list):
    dle_out = []

    for data_byte in input_list:
        if data_byte in DLE_list:
            dle_out.append('10')
            dle_out.append(str(int(data_byte) | 80))
        else:
            dle_out.append(data_byte)

    return dle_out

def calculate_crc(buffer):
    polynomial = 0x1021  # CRC polynomial
    crc = 0x0000  # Initialize CRC to 0xFFFF
    for elem in buffer:
        byte = int(elem, 16)
        crc ^= (byte << 8)  # XOR CRC with next byte shifted left by 8 bits
        for _ in range(8):
            if crc & 0x8000:  # Check if MSB of CRC is set
                crc = (crc << 1) ^ polynomial  # If MSB set, perform polynomial XOR
            else:
                crc <<= 1  # If MSB not set, shift CRC left by one bit
    return crc  & 0xFFFF # Return the 16-bit CRC value

def get_two_byte_hex_list(input_list):
    hex_list = []
    for elem in input_list:
        if len(elem) > 2:
            hex_elem = format(int(elem[2:]), '02x')
            hex_list.append(hex_elem)

            hex_elem = format(int(elem[:2]), '02x')
            hex_list.append(hex_elem)
        #hex_str = [format(int(elem), '04x') if len(elem) > 2 else format(int(elem), '02x')][0]
        else:
            hex_elem = format(int(elem), '02x')
            hex_list.append((hex_elem))
    
    return hex_list


def print_packet(packet_list):
    day = packet_list[0]
    month = packet_list[1]
    yearLSB = packet_list[2]
    yearMSB = packet_list[3]
    hour = packet_list[4]
    min = packet_list[5]
    sec = packet_list[6]
    print(f"Time: \t         {day}.{month}.{yearMSB}{yearLSB}   {hour}:{min}:{sec}")
    print(f"Static field: \t {packet_list[8:14]}")
    print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
    for i in range(14, len(packet_list), 30):
        print(f"\t         {packet_list[i:(i+30)]}")


def print_history_output():   
    headerSize = 3
    bodySize = 255
    x=headerSize
    # print(decoded_list[0:x])
    print(f"STX:\t           {decoded_list[0]}")
    print(f"Response code:\t {decoded_list[1]}, (hex = {hex(decoded_list[1])})")
    print(f"Number of packets {decoded_list[2]}")
    flag = True
    while(flag):
        y=x
        x=x+bodySize
        # print(f" y value {y}, x value {x}, len {len(decoded_list)}")
        print_packet(decoded_list[y:x])
        if((x+bodySize) > len(decoded_list)):
            # print(decoded_list[y:(x-1)])
            print(f"crc {decoded_list[-3:-1]}")
            print(f"etx {decoded_list[-1]}")
            flag = False


def print_output():
    print(f"STX:\t           {decoded_list[0]}")
    print(f"Response code:\t {decoded_list[1]}, (hex = {hex(decoded_list[1])})")
    day = decoded_list[2]
    month = decoded_list[3]
    yearLSB = decoded_list[4]
    yearMSB = decoded_list[5]
    hour = decoded_list[6]
    min = decoded_list[7]
    sec = decoded_list[8]
    print(f"Time: \t         {day}.{month}.{yearMSB}{yearLSB}   {hour}:{min}:{sec}")
    print(f"Static field: \t {decoded_list[10:16]}")
    print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
    for i in range(16, len(decoded_list)-3, 30):
        print(f"\t         {decoded_list[i:(i+30)]}")
    print(f"CRC: \t          {decoded_list[len(decoded_list)-3:len(decoded_list)-1]}")
    print(f"ETX: \t          {decoded_list[len(decoded_list)-1]}")

def removeDLE():
    skip_next = False
    for byte in range(0, len(recevied_data), 1):
        value = int(recevied_data[byte],16)
        #  print(value,DLE)

        if skip_next:
            skip_next = False
            decoded_byte = (value & AENOR_DLE_DECODE_CHARACTER )
            decoded_list.append(decoded_byte)
        else:
            if value==DLE:
                skip_next = True
            #   print("DLE byte")
            else:
                decoded_byte = value
                decoded_list.append(decoded_byte)

def close_connection():
    removeDLE()
    # print(decoded_list)
    # print_output()
    if (int(choice) == 1):
        print_output()
    else:
        print_history_output()
   
# def parse_received_packet():
#     # index = 0
#     # if recevied_data[index]!=STX:
#     #     return
#     # else:
#     # removeDLE()
#     # print_output_test()


def tcp_client(host, port, message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        socket.timeout(30)
        # Connect to the server
        client_socket.connect((host, port))

        # Send data to the server
        # client_socket.sendall(bytes.fromhex(message))
        for byte in range(0, len(message), 2):
            client_socket.send(bytes.fromhex(message[byte:byte+2]))
            # print(f"sending {bytes.fromhex(message[byte:byte+2])}")
            time.sleep(0.2)
        print(f"sent: {message}  ")

        while True:
            # Receive data from the server
            data = client_socket.recv(1500).hex()
            for i in range(0, len(data), 2):
                data_hex = data[i:i+2]
                data_decimal = int(data_hex, 16)
                recevied_data.append(data_hex)
                # print(f"{data_decimal} ",end='')
            # print("Received from server:", data)
            
            if data_decimal==CLOSE_ETX:
                print(f"\nPattern '{ETX}' found. Closing the connection.")
                break  

    except socket.timeout:
        print("\nTimeout closing connection")     
        client_socket.close()
        close_connection()

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Closing the connection.")
        # client_socket.close()
        # close_connection()        

    except Exception as e:
        print(f"Error: {e}")
        client_socket.close()
        close_connection()        

    finally:
        client_socket.close()
        close_connection()
        

if __name__ == "__main__":
    server_host = "192.168.99.26"
    server_port = 9001
    # message_to_send = "02201085564303" // wrong crc order 
    #message_to_send =   "0220108612108318140f1e12108318140f32000074be03"  #outpu from test1.py  
   
    ETX = '03'
    STX = '02'
    CLOSE_ETX = 3
    recevied_data =[]
    decoded_list = []
    AENOR_DLE_DECODE_CHARACTER = 0x7F
    DLE = 0x10
    DLE_list = ['03', '02', '10', '06', '05']

    STR_ADDR = '32'
    REQUEST = '06'
    INDICATION = '0000'
    
    choice = input(" type 1 for LAST period data or type 2 for History data:")

    if(int(choice) == 1):
        message_to_send = "02201085435603"  #correct CRC order for LAST period data 
    elif(int(choice) == 2):
        start_time = input("Start date and time comma saperated (dd,mm,yyyy,hh,min)")
        end_time = input("Start date and time comma saperated (dd,mm,yyyy,hh,min)")
        input_string = f'{STR_ADDR},{REQUEST},{start_time},{end_time},{INDICATION}'
        print(f"{input_string}")

        input_list = input_string.split(',')

        hex_list = get_two_byte_hex_list(input_list)
        print(f'hex list: {hex_list}')

        crc = calculate_crc(hex_list)
        crc_hex = format(crc, 'x')

        crc_hex_list = hex_list
        if len(crc_hex) > 2:
            crc_hex_list.append(crc_hex[2:])
            crc_hex_list.append(crc_hex[:2])
        else:
            crc_hex_list.append(crc_hex)

        hex_list = add_dle(crc_hex_list)
        print(f"{hex_list}")

        joinedList = ''.join(hex_list)
        message_to_send= f'{STX}{joinedList}{ETX}'
        # message_to_send = "02201085435603"  #correct CRC order for LAST period data 
        print(message_to_send)
    else:
        print(f"Invalid input")
    tcp_client(server_host, server_port, message_to_send)
