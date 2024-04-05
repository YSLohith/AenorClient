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
    hex_list_yearCorrected = []
    for elem in input_list:
        # if len(elem) > 2:
        #     hex_elem = format(int(elem[2:]), '02x')
        #     hex_list.append(hex_elem)
        #     hex_elem = format(int(elem[:2]), '02x')
        #     hex_list.append(hex_elem)
        # #hex_str = [format(int(elem), '04x') if len(elem) > 2 else format(int(elem), '02x')][0]
        # else:
        #     hex_elem = format(int(elem), '02x')
        #     hex_list.append((hex_elem))
    # return hex_list
        if len(elem) > 2:
            hex_elem = format(int(elem), '04x')
        else:
            hex_elem = format(int(elem), '02x')
        hex_list.append((hex_elem))

    for elem in hex_list:
        if len(elem) > 2:
            hex_list_yearCorrected.append(elem[2:])
            hex_list_yearCorrected.append(elem[:2])
        else:
            hex_list_yearCorrected.append(elem)
    print(f" year corrected values \n {hex_list_yearCorrected}")
    return hex_list_yearCorrected


def print_header(headerList):
    print(f"STX:               {decoded_list[0]}")
    print(f"Address:           {decoded_list[1]} , (hex = {hex(decoded_list[1])})")
    print(f"Response code:     {decoded_list[2]}, (hex = {hex(decoded_list[2])})")

def print_footer(footerList):
    print(f"\nCRC: \t          {footerList[0:2]}  (hex = {hex(footerList[0])}, {hex(footerList[1])})")
    print(f"ETX: \t          {footerList[2]}")

def print_dateTime(dateList,type):
    # print(dateList)
    day     = dateList[0]
    month   = dateList[1]
    yearLSB = format(dateList[2], '02x')
    yearMSB = format(dateList[3], '02x')
    yearFullForm = int(yearMSB+yearLSB,16)  
    hour    = dateList[4]
    min     = dateList[5]
    if(type == 0):
        sec     = dateList[6]
        # print(f"Time: \t         {day}.{month}.{yearMSB}{yearLSB}   {hour}:{min}:{sec}")
        print(f"Time: \t         {day}.{month}.{yearFullForm}   {hour}:{min}:{sec}")
    else:
        # print(f"Time: \t         {day}.{month}.{yearMSB}{yearLSB}   {hour}:{min}")
        print(f"Time: \t         {day}.{month}.{yearFullForm}   {hour}:{min}")

def print_packet(packet_list, valid,historyPacket):
    # print(packet_list)
    print_dateTime(packet_list[0:7],historyPacket)
    if historyPacket==0:
        print(f"Static field: \t {packet_list[7:13]}")
        print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
        for i in range(13, len(packet_list), EACH_SENSOR_DATA_SIZE):
            print(f"\t         {packet_list[i:(i+EACH_SENSOR_DATA_SIZE)]}")
    else:
        if(valid):
            print(f"Static field: \t {packet_list[6:12]}")
            print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
            for i in range(12, len(packet_list), EACH_SENSOR_DATA_SIZE):
                print(f"\t         {packet_list[i:(i+EACH_SENSOR_DATA_SIZE)]}")
        else:
            print(f"interval period \t {packet_list[-2:]}")



def print_history_output():   
    headerSize = 5
    bodySize = (213 * 1) #(EACH_SENSOR_DATA_SIZE * NUM_OF_SENSORS) #
    x=headerSize
    print(decoded_list[0:x])
    print_header(decoded_list[0:HEADER_SIZE])
    if(decoded_list[2] == 3):
        print(f" invalide packet , contents are {decoded_list}")
    else:
        print(f"Number of packets  {decoded_list[3]}")
        MaxPackets = decoded_list[3]
        currentPacket = 0
        if(decoded_list[2]>0):
            flag = True
        else:
            flag = False
        nextTimeSlotData = decoded_list[4]
        while(flag):
            y=x
            x=x+bodySize
            currentPacket = currentPacket + 1
            # print(f" y value {y}, x value {x}, len {len(decoded_list)}")
            # print_packet(decoded_list[y:x-1])
            if( nextTimeSlotData == 1):
                print("Data present in next time slot \n")
                print_packet(decoded_list[y:x-1],True,1)
                nextTimeSlotData = decoded_list[x-1]
            elif(nextTimeSlotData == 0):
                print("Data not present in next slot\n")
                x=y+9
                print_packet(decoded_list[y:x-1],False,1)
                nextTimeSlotData = decoded_list[x-1]
            # if((x+bodySize) > len(decoded_list)):
            if(currentPacket >= MaxPackets):
                print_footer(decoded_list[-3:])
                flag = False

def print_Alarm():
    print_header(decoded_list[0:HEADER_SIZE])
    index = HEADER_SIZE
    NTDStatus = decoded_list[index]
    index +=1
    ETDAlarm = decoded_list[index]
    index +=1
    NumberOfSensors = decoded_list[index]
    index +=1
    sensornum = 0
    print(f"NTDStaus:\t{NTDStatus} \nAlarm:\t{ETDAlarm} \nNumberOfSensors:\t{NumberOfSensors}")
    sensorAlarm = decoded_list[index:-3]
    # print(f"Maker:{maker} \nModel:{model} \nVersion:{version}")
    for index in range(0, len(sensorAlarm), 2):
        Sensortype = sensorAlarm[index]
        SensorAlarm = sensorAlarm[index+1]
        sensornum=sensornum+1
        print(f" \tsensor {sensornum}, type {Sensortype}, alarm {SensorAlarm}")
    print_footer(decoded_list[-3:])

def print_Maker():
    print_header(decoded_list[0:HEADER_SIZE])
    index = HEADER_SIZE
    maker = decoded_list[index]
    index +=1
    model = decoded_list[index]
    index +=1
    version = decoded_list[index]
    print(f"Maker:\t{maker} \nModel:\t{model} \nVersion:\t{version}")

def print_DayTime():
    print_header(decoded_list[0:HEADER_SIZE])
    print_dateTime(decoded_list[HEADER_SIZE:],0)
    print_footer(decoded_list[-3:])


def print_output():
    print_header(decoded_list[0:HEADER_SIZE])
    print_packet(decoded_list[HEADER_SIZE:-3],True,0)
    print_footer(decoded_list[-3:])


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
    print(" Data received with DLE ")
    print(recevied_data)
    removeDLE()
    print(" \nAfter removing DLE")
    # print(decoded_list)
    decoded_hex_list=[]
    for elem in decoded_list:
        hex_elem = format(int(elem), '02x')
        # hex_elem = hex(elem)
        decoded_hex_list.append(hex_elem)
    print(decoded_hex_list)
    print("\nData sorted as below ")

    input_choice = int(choice)
    # print_output()
    if (input_choice == 1):
        print_output()
    elif(input_choice == 2):
        print_history_output()
    elif(input_choice == 3):
        print_DayTime()
    elif(input_choice == 4):
        print_Maker()
    elif(input_choice == 5):
        print(decoded_list)
        print_Alarm()
    elif(input_choice == 6):
        print(decoded_list)
    print("\n")


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
                print(f"\n Received ETX='{ETX}'. So closing the connection.")
                print("Resonse from server is \n")
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
        

def form_packet(input_string):
        input_list = input_string.split(',')

        hex_list = get_two_byte_hex_list(input_list)
        print(f'hex list: {hex_list}')

        crc = calculate_crc(hex_list)
        crc_hex = format(crc, 'x')

        crc_hex_list = hex_list
        print(f"crc_hex = {crc_hex}")
        # if len(crc_hex) > 2:
        #     crc_hex_list.append(crc_hex[2:])
        #     crc_hex_list.append(crc_hex[:2])
        # else:
        #     crc_hex_list.append(crc_hex)
        crc_hex_list.append(crc_hex)

        hex_list = add_dle(crc_hex_list)
        print(f"{hex_list}")

        joinedList = ''.join(hex_list)
        message_to_send= f'{STX}{joinedList}{ETX}'

         # message_to_send = "02201085435603"  #correct CRC order for LAST period data 
        print(f"messag to send {message_to_send}")
        # decoded_list=[2, 134, 5, 1, 25, 3, 24, 20, 19, 50, 44, 1, 5, 1, 1, 8, 1, 38, 0, 0, 0, 0, 0, 0, 0, 76, 0, 168, 1, 129, 0, 2, 1, 2, 19, 0, 19, 0, 2, 3, 38, 0, 0, 0, 0, 0, 2, 38, 0, 0, 0, 0, 0, 1, 0, 77, 0, 169, 1, 130, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 3, 36, 0, 0, 0, 0, 0, 1, 0, 76, 0, 170, 1, 129, 0, 2, 1, 2, 0, 0, 36, 0, 2, 3, 36, 0, 0, 0, 0, 0, 4, 37, 0, 0, 0, 0, 0, 1, 0, 74, 0, 171, 1, 130, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 5, 38, 0, 0, 0, 0, 0, 0, 0, 75, 0, 172, 1, 131, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 6, 38, 0, 0, 0, 0, 0, 1, 0, 76, 0, 173, 1, 132, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 7, 38, 0, 0, 0, 0, 0, 1, 0, 76, 0, 174, 1, 133, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 8, 38, 0, 0, 0, 0, 0, 1, 0, 75, 0, 175, 1, 134, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 1, 25, 3, 24, 20, 19, 55, 44, 1, 5, 1, 1, 8, 1, 37, 0, 0, 0, 0, 0, 0, 0, 76, 0, 168, 1, 134, 0, 2, 1, 2, 18, 0, 19, 0, 2, 3, 37, 0, 0, 0, 0, 0, 2, 37, 0, 0, 0, 0, 0, 1, 0, 77, 0, 169, 1, 135, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 3, 38, 0, 0, 0, 0, 0, 1, 0, 74, 0, 170, 1, 137, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 4, 38, 0, 0, 0, 0, 0, 1, 0, 75, 0, 171, 1, 138, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 5, 38, 0, 0, 0, 0, 0, 0, 0, 76, 0, 172, 1, 139, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 6, 38, 0, 0, 0, 0, 0, 1, 0, 77, 0, 173, 1, 140, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 7, 37, 0, 0, 0, 0, 0, 1, 0, 74, 0, 173, 1, 139, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 8, 37, 0, 0, 0, 0, 0, 1, 0, 75, 0, 174, 1, 140, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 0, 25, 3, 24, 20, 20, 0, 0, 1, 25, 3, 24, 20, 20, 5, 44, 1, 5, 1, 1, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 1, 25, 3, 24, 20, 20, 9, 44, 1, 5, 1, 1, 8, 1, 1, 0, 0, 0, 0, 0, 0, 0, 50, 0, 164, 1, 0, 0, 2, 1, 2, 1, 0, 0, 0, 2, 3, 1, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 1, 0, 97, 0, 165, 1, 1, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 1, 0, 98, 0, 166, 1, 2, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 1, 0, 99, 0, 167, 1, 3, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 5, 1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 168, 1, 4, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0, 0, 0, 1, 0, 101, 0, 169, 1, 5, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 7, 1, 0, 0, 0, 0, 0, 1, 0, 102, 0, 170, 1, 6, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 8, 1, 0, 0, 0, 0, 0, 1, 0, 103, 0, 171, 1, 7, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 177, 200, 3]
        # for data not present in the response packet only time present
        # decoded_list= [2, 134, 5, 1, 25, 3, 24, 20, 19, 50, 44, 1, 5, 1, 1, 8, 1, 38, 0, 0, 0, 0, 0, 0, 0, 76, 0, 168, 1, 129, 0, 2, 1, 2, 19, 0, 19, 0, 2, 3, 38, 0, 0, 0, 0, 0, 2, 38, 0, 0, 0, 0, 0, 1, 0, 77, 0, 169, 1, 130, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 3, 36, 0, 0, 0, 0, 0, 1, 0, 76, 0, 170, 1, 129, 0, 2, 1, 2, 0, 0, 36, 0, 2, 3, 36, 0, 0, 0, 0, 0, 4, 37, 0, 0, 0, 0, 0, 1, 0, 74, 0, 171, 1, 130, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 5, 38, 0, 0, 0, 0, 0, 0, 0, 75, 0, 172, 1, 131, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 6, 38, 0, 0, 0, 0, 0, 1, 0, 76, 0, 173, 1, 132, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 7, 38, 0, 0, 0, 0, 0, 1, 0, 76, 0, 174, 1, 133, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 8, 38, 0, 0, 0, 0, 0, 1, 0, 75, 0, 175, 1, 134, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 1, 25, 3, 24, 20, 19, 55, 44, 1, 5, 1, 1, 8, 1, 37, 0, 0, 0, 0, 0, 0, 0, 76, 0, 168, 1, 134, 0, 2, 1, 2, 18, 0, 19, 0, 2, 3, 37, 0, 0, 0, 0, 0, 2, 37, 0, 0, 0, 0, 0, 1, 0, 77, 0, 169, 1, 135, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 3, 38, 0, 0, 0, 0, 0, 1, 0, 74, 0, 170, 1, 137, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 4, 38, 0, 0, 0, 0, 0, 1, 0, 75, 0, 171, 1, 138, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 5, 38, 0, 0, 0, 0, 0, 0, 0, 76, 0, 172, 1, 139, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 6, 38, 0, 0, 0, 0, 0, 1, 0, 77, 0, 173, 1, 140, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 7, 37, 0, 0, 0, 0, 0, 1, 0, 74, 0, 173, 1, 139, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 8, 37, 0, 0, 0, 0, 0, 1, 0, 75, 0, 174, 1, 140, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 0, 25, 3, 24, 20, 20, 0, 44, 1, 1, 25, 3, 24, 20, 20, 5, 44, 1, 5, 1, 1, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 1, 25, 3, 24, 20, 20, 9, 44, 1, 5, 1, 1, 8, 1, 1, 0, 0, 0, 0, 0, 0, 0, 50, 0, 164, 1, 0, 0, 2, 1, 2, 1, 0, 0, 0, 2, 3, 1, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 1, 0, 97, 0, 165, 1, 1, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 1, 0, 98, 0, 166, 1, 2, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 1, 0, 99, 0, 167, 1, 3, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 5, 1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 168, 1, 4, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0, 0, 0, 1, 0, 101, 0, 169, 1, 5, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 7, 1, 0, 0, 0, 0, 0, 1, 0, 102, 0, 170, 1, 6, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 8, 1, 0, 0, 0, 0, 0, 1, 0, 103, 0, 171, 1, 7, 0, 2, 1, 2, 0, 0, 1, 0, 2, 3, 1, 0, 0, 0, 0, 0, 164, 120, 3]
        # for data not present for consecutive 5 times
        # decoded_list= [2, 134, 10, 1, 26, 3, 24, 20, 12, 45, 44, 1, 5, 1, 1, 8, 1, 38, 0, 0, 0, 0, 0, 0, 0, 75, 0, 168, 1, 124, 0, 2, 1, 2, 19, 0, 19, 0, 2, 3, 38, 0, 0, 0, 0, 0, 2, 38, 0, 0, 0, 0, 0, 1, 0, 76, 0, 169, 1, 125, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 3, 38, 0, 0, 0, 0, 0, 1, 0, 77, 0, 170, 1, 126, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 4, 37, 0, 0, 0, 0, 0, 1, 0, 75, 0, 171, 1, 129, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 5, 37, 0, 0, 0, 0, 0, 0, 0, 75, 0, 172, 1, 130, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 6, 37, 0, 0, 0, 0, 0, 1, 0, 76, 0, 173, 1, 131, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 7, 37, 0, 0, 0, 0, 0, 1, 0, 77, 0, 174, 1, 132, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 8, 37, 0, 0, 0, 0, 0, 1, 0, 76, 0, 175, 1, 133, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 1, 26, 3, 24, 20, 12, 50, 44, 1, 5, 1, 1, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 1, 26, 3, 24, 20, 12, 50, 44, 1, 5, 1, 1, 8, 1, 32, 0, 0, 0, 0, 0, 0, 0, 77, 0, 168, 1, 124, 0, 2, 1, 2, 16, 0, 16, 0, 2, 3, 32, 0, 0, 0, 0, 0, 2, 32, 0, 0, 0, 0, 0, 1, 0, 76, 0, 169, 1, 125, 0, 2, 1, 2, 0, 0, 32, 0, 2, 3, 32, 0, 0, 0, 0, 0, 3, 32, 0, 0, 0, 0, 0, 1, 0, 77, 0, 170, 1, 126, 0, 2, 1, 2, 0, 0, 32, 0, 2, 3, 32, 0, 0, 0, 0, 0, 4, 32, 0, 0, 0, 0, 0, 1, 0, 78, 0, 171, 1, 127, 0, 2, 1, 2, 0, 0, 32, 0, 2, 3, 32, 0, 0, 0, 0, 0, 5, 31, 0, 0, 0, 0, 0, 0, 0, 78, 0, 171, 1, 124, 0, 2, 1, 2, 0, 0, 31, 0, 2, 3, 31, 0, 0, 0, 0, 0, 6, 31, 0, 0, 0, 0, 0, 1, 0, 75, 0, 172, 1, 125, 0, 2, 1, 2, 0, 0, 31, 0, 2, 3, 31, 0, 0, 0, 0, 0, 7, 31, 0, 0, 0, 0, 0, 1, 0, 76, 0, 173, 1, 126, 0, 2, 1, 2, 0, 0, 31, 0, 2, 3, 31, 0, 0, 0, 0, 0, 8, 31, 0, 0, 0, 0, 0, 1, 0, 77, 0, 174, 1, 127, 0, 2, 1, 2, 0, 0, 31, 0, 2, 3, 31, 0, 0, 0, 0, 0, 1, 26, 3, 24, 20, 12, 57, 44, 1, 5, 1, 1, 8, 1, 17, 0, 0, 0, 0, 0, 0, 0, 74, 0, 167, 1, 64, 0, 2, 1, 2, 9, 0, 8, 0, 2, 3, 17, 0, 0, 0, 0, 0, 2, 16, 0, 0, 0, 0, 0, 1, 0, 77, 0, 169, 1, 63, 0, 2, 1, 2, 0, 0, 16, 0, 2, 3, 16, 0, 0, 0, 0, 0, 3, 16, 0, 0, 0, 0, 0, 1, 0, 78, 0, 170, 1, 64, 0, 2, 1, 2, 0, 0, 16, 0, 2, 3, 16, 0, 0, 0, 0, 0, 4, 17, 0, 0, 0, 0, 0, 1, 0, 79, 0, 171, 1, 68, 0, 2, 1, 2, 0, 0, 17, 0, 2, 3, 17, 0, 0, 0, 0, 0, 5, 17, 0, 0, 0, 0, 0, 0, 0, 77, 0, 172, 1, 69, 0, 2, 1, 2, 0, 0, 17, 0, 2, 3, 17, 0, 0, 0, 0, 0, 6, 17, 0, 0, 0, 0, 0, 1, 0, 77, 0, 173, 1, 70, 0, 2, 1, 2, 0, 0, 17, 0, 2, 3, 17, 0, 0, 0, 0, 0, 7, 17, 0, 0, 0, 0, 0, 1, 0, 78, 0, 174, 1, 71, 0, 2, 1, 2, 0, 0, 17, 0, 2, 3, 17, 0, 0, 0, 0, 0, 8, 17, 0, 0, 0, 0, 0, 1, 0, 79, 0, 175, 1, 72, 0, 2, 1, 2, 0, 0, 17, 0, 2, 3, 17, 0, 0, 0, 0, 0, 1, 26, 3, 24, 20, 13, 0, 44, 1, 5, 1, 1, 8, 1, 38, 0, 0, 0, 0, 0, 0, 0, 74, 0, 168, 1, 130, 0, 2, 1, 2, 19, 0, 19, 0, 2, 3, 38, 0, 0, 0, 0, 0, 2, 38, 0, 0, 0, 0, 0, 1, 0, 75, 0, 169, 1, 131, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 3, 38, 0, 0, 0, 0, 0, 1, 0, 76, 0, 170, 1, 132, 0, 2, 1, 2, 0, 0, 38, 0, 2, 3, 38, 0, 0, 0, 0, 0, 4, 37, 0, 0, 0, 0, 0, 1, 0, 76, 0, 170, 1, 131, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 5, 37, 0, 0, 0, 0, 0, 0, 0, 74, 0, 171, 1, 132, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 6, 37, 0, 0, 0, 0, 0, 1, 0, 75, 0, 172, 1, 133, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 7, 37, 0, 0, 0, 0, 0, 1, 0, 76, 0, 173, 1, 134, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 8, 37, 0, 0, 0, 0, 0, 1, 0, 77, 0, 174, 1, 135, 0, 2, 1, 2, 0, 0, 37, 0, 2, 3, 37, 0, 0, 0, 0, 0, 0, 26, 3, 24, 20, 13, 5, 44, 1, 0, 26, 3, 24, 20, 13, 10, 44, 1, 0, 26, 3, 24, 20, 13, 15, 44, 1, 0, 26, 3, 24, 20, 13, 20, 44, 1, 0, 26, 3, 24, 20, 13, 25, 44, 1, 148, 251, 3]
        # print_history_output()
        return message_to_send



if __name__ == "__main__":
    # server_host = "192.168.99.26"
    # server_port = 9001
    server_host = "62.232.56.36"
    server_port = 4301
    # message_to_send = "02201085564303" // wrong crc order 
    #message_to_send =   "0220108612108318140f1e12108318140f32000074be03"  #outpu from test1.py  
   
    ETX = '03'
    STX = '02'
    CLOSE_ETX = 3
    HEADER_SIZE = 3
    EACH_SENSOR_DATA_SIZE = 25
    NUM_OF_SENSORS = 8
    recevied_data =[]
    decoded_list = []
    AENOR_DLE_DECODE_CHARACTER = 0x7F
    DLE = 0x10
    DLE_list = ['03', '02', '10', '06', '05']

    STR_ADDR = '32'
    INDICATION = '0000'
    
    choice = input(" type number 1 to 6 to send appropriate request:")

    if(int(choice) == 1):
        # message_to_send = "02201085435603"  #correct CRC order for LAST period data 
        message_to_send = "02201085564303"  #correct CRC order for LAST period data 
    elif(int(choice) == 2):
        HISTORY_REQUEST = '06'
        start_time = input("Start date and time comma saperated (dd,mm,yyyy,hh,min)")
        end_time = input("Start date and time comma saperated (dd,mm,yyyy,hh,min)")
        input_string = f'{STR_ADDR},{HISTORY_REQUEST},{start_time},{end_time},{INDICATION}'
        print(f"{input_string}")

        message_to_send = form_packet(input_string)

    elif(int(choice) == 3):
        # message_to_send = "02200aaca703"  #correct CRC order for LAST period data 
        message_to_send = "02200aa7ac03"  #correct CRC order for LAST period data 
    elif(int(choice) == 4):
        # message_to_send = "02200b8db703"  #correct CRC order for LAST period data 
        message_to_send = "02200bb78d03"  #correct CRC order for LAST period data 
    elif(int(choice) == 5):
        # message_to_send = "022009cf9703"  #correct CRC order for LAST period data 
        message_to_send = "02200997cf03"  #correct CRC order for LAST period data 
    elif(int(choice) == 6):
        SET_REQUEST = '03'
        start_time = input("Enter set date&time comma saperated (dd,mm,yyyy,hh,min,sec)")
        input_string = f'{STR_ADDR},{SET_REQUEST},{start_time}'
        print(f"{input_string}")

        message_to_send = form_packet(input_string)

    else:
        print(f"Invalid input")

    if(int(choice) != 7):
        tcp_client(server_host, server_port, message_to_send)
