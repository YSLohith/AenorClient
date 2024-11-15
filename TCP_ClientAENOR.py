import socket
import time
import sys

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
        if len(elem) > 3:
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
    print(f"STX:               {headerList[0]}")
    print(f"Address:           {headerList[1]} , (hex = {hex(headerList[1])})")
    print(f"Response code:     {headerList[2]}, (hex = {hex(headerList[2])})")

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
    elif(type == 1):
        # print(f"Time: \t         {day}.{month}.{yearMSB}{yearLSB}   {hour}:{min}")
        print(f"Time: \t         {day}.{month}.{yearFullForm}   {hour}:{min}")
    elif(type == 2):
        print(f"Time: \t         {day}.{month}.{yearFullForm}   {hour}")
    elif(type == 3):
        print(f"Time: \t         {day}.{month}.{yearFullForm}")

def print_packet(packet_list, valid,historyPacket):
    # print(packet_list)
    print_dateTime(packet_list[0:7],historyPacket)
    if historyPacket==0:
        start = TIME_SIZE_WITH_SEC
        end = TIME_SIZE_WITH_SEC + SIZE_STATIC_FIELD
        print(f"Static field: \t {packet_list[start:end]}")
        print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
        for i in range(end, len(packet_list), EACH_SENSOR_DATA_SIZE):
            print(f"\t         {packet_list[i:(i+EACH_SENSOR_DATA_SIZE)]}")
    elif historyPacket==1:
            start = TIME_SIZE_WITHOUT_SEC
            end = TIME_SIZE_WITHOUT_SEC + SIZE_STATIC_FIELD + 1
            print(f"Static field: \t {packet_list[start:end]}")
            valid_field = packet_list[TIME_SIZE_WITHOUT_SEC+2]
            if(valid_field == 1):
                print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
                for i in range(end, len(packet_list), EACH_SENSOR_DATA_SIZE):
                    print(f"\t         {packet_list[i:(i+EACH_SENSOR_DATA_SIZE)]}")
            else:
                print(f"interval period \t {packet_list[-2:]}")
            # print(f"valid_field = {valid_field}\n")
            # return valid_field    
    elif historyPacket==2:
        start = TIME_SIZE_WITHOUT_MIN_SEC
        end = TIME_SIZE_WITHOUT_MIN_SEC + SIZE_STATIC_FIELD - 1
        print(f"Static field: \t {packet_list[start:end]}")
        print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
        for i in range(end, len(packet_list), EACH_SENSOR_DATA_SIZE):
            print(f"\t         {packet_list[i:(i+EACH_SENSOR_DATA_SIZE)]}")
    elif historyPacket==3:
        start = TIME_SIZE_WITHOUT_HOUR_MIN_SEC
        end = TIME_SIZE_WITHOUT_HOUR_MIN_SEC + SIZE_STATIC_FIELD - 1
        print(f"Static field: \t {packet_list[start:end]}")
        print(" ID , VehicleIntesity, Occupancy, CongeDet, TraficDirection, AvgSpeed, AvgLen, AvgDist, ClassiType")
        for i in range(end, len(packet_list), EACH_SENSOR_DATA_SIZE):
            print(f"\t         {packet_list[i:(i+EACH_SENSOR_DATA_SIZE)]}")



def print_history_output():   
    x=HISTORY_PCK_HEADER_SIZE
    bodySize = (EACH_SENSOR_DATA_SIZE * NUM_OF_SENSORS) + TIME_SIZE_WITHOUT_SEC + SIZE_STATIC_FIELD + 1 # (213 * 1)  # (25 * 8) + 6 + 6 +
    print(decoded_list[0:x])
    print("testing  ")
    print_header(decoded_list[0:HEADER_SIZE])
    if(decoded_list[2] == 3):
        print(f" invalide packet , contents are {decoded_list}")
    else:
        print(f"Number of packets  {decoded_list[3]}")
        MaxPackets = decoded_list[3]
        currentPacket = 0
        if(decoded_list[3]>0):
            flag = True
        else:
            flag = False
        nextTimeSlotData = decoded_list[HISTORY_PCK_HEADER_SIZE+TIME_SIZE_WITHOUT_SEC+2]
        print("\n")
        print(f"next time slot {nextTimeSlotData}")
        while(flag):
            y=x
            x=x+bodySize
            currentPacket = currentPacket + 1
            # print(f" y value {y}, x value {x}, len {len(decoded_list)}")
            # print_packet(decoded_list[y:x-1])
            if( nextTimeSlotData == 1):
                # print("Data present in next time slot \n")
                print_packet(decoded_list[y:x],True,1)
                print("\n")
                if(currentPacket <= MaxPackets - 2):
                    nextTimeSlotData = decoded_list[x+8]
                # print(f"next time slot {nextTimeSlotData}")
            elif(nextTimeSlotData == 4 or nextTimeSlotData == 2):
                # print("Data not present in next slot\n")
                x=y+9
                print_packet(decoded_list[y:x],False,1)
                print("\n")
                if(currentPacket <= MaxPackets - 2):
                    nextTimeSlotData = decoded_list[x+8]
                # print(f"next time slot {nextTimeSlotData}")
                # nextTimeSlotData = decoded_list[x-1]
            # if((x+bodySize) > len(decoded_list)):
            if(currentPacket == MaxPackets):
                print(f"Next packet status {decoded_list[x]}")
                startIndex = x+1
                endIndex = startIndex + TIME_SIZE_WITHOUT_SEC
                print_dateTime(decoded_list[startIndex:endIndex],1)
                startIndex = endIndex
                endIndex = startIndex + 2
                print(f"Static field: \t {decoded_list[startIndex:endIndex]}")
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


def print_HourOutput():
    print_header(decoded_list[0:HEADER_SIZE])
    print_packet(decoded_list[HEADER_SIZE:-3],True,2)
    print_footer(decoded_list[-3:])

def print_DayOutput():
    print_header(decoded_list[0:HEADER_SIZE])
    print_packet(decoded_list[HEADER_SIZE:-3],True,3)
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
    print(decoded_list)
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
    elif(input_choice == 7):
        print_HourOutput()
    elif(input_choice == 8):
        print_DayOutput()
    print("\n")


def tcp_client(host, port, message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.settimeout(30)
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
            try:

                # Receive data from the server
                data = client_socket.recv(1500).hex()
                if not data:
                    print("No more data received, closing connection.")
                    break

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
                # client_socket.close()
                # close_connection()
                break

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Closing the connection.")
        # client_socket.close()
        # close_connection()        

    except Exception as e:
        print(f"Error: {e}")
        # client_socket.close()
        # close_connection()        

    finally:
        client_socket.close()
        close_connection()

        

def form_packet(input_string):
        input_list = input_string.split(DELIMETER)
        print(f"input_list = {input_list}")
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
        # decoded_list= [2, 32, 134, 4, 11, 4, 232, 7, 23, 40, 44, 1, 1, 5, 1, 1, 8, 1, 37, 0, 0, 0, 0, 0, 77, 42, 94, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 2, 38, 0, 0, 0, 1, 0, 74, 42, 94, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 3, 38, 0, 0, 0, 1, 0, 75, 42, 99, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 4, 38, 0, 0, 0, 1, 0, 76, 42, 104, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 5, 38, 0, 0, 0, 0, 0, 77, 42, 109, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 6, 37, 0, 0, 0, 1, 0, 74, 42, 114, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 7, 37, 0, 0, 0, 1, 0, 75, 42, 119, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 8, 37, 0, 0, 0, 1, 0, 76, 42, 124, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 11, 4, 232, 7, 23, 45, 44, 1, 1, 5, 1, 1, 8, 1, 37, 0, 0, 0, 0, 0, 75, 42, 121, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 2, 37, 0, 0, 0, 1, 0, 75, 42, 126, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 3, 37, 0, 0, 0, 1, 0, 76, 42, 131, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 4, 37, 0, 0, 0, 1, 0, 77, 42, 136, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 5, 37, 0, 0, 0, 0, 0, 76, 42, 141, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 6, 38, 0, 0, 0, 1, 0, 75, 42, 145, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 7, 38, 0, 0, 0, 1, 0, 76, 42, 150, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 8, 38, 0, 0, 0, 1, 0, 77, 42, 155, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 11, 4, 232, 7, 23, 50, 44, 1, 1, 5, 1, 1, 8, 1, 38, 0, 0, 0, 0, 0, 74, 42, 158, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 2, 38, 0, 0, 0, 1, 0, 75, 42, 163, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 3, 38, 0, 0, 0, 1, 0, 76, 42, 168, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 4, 38, 0, 0, 0, 1, 0, 77, 42, 173, 2, 1, 2, 38, 0, 0, 0, 2, 3, 38, 0, 0, 0, 0, 0, 5, 37, 0, 0, 0, 0, 0, 74, 42, 168, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 6, 37, 0, 0, 0, 1, 0, 75, 42, 173, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 7, 37, 0, 0, 0, 1, 0, 76, 42, 178, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 8, 37, 0, 0, 0, 1, 0, 77, 42, 183, 2, 1, 2, 37, 0, 0, 0, 2, 3, 37, 0, 0, 0, 0, 0, 1, 11, 4, 232, 7, 23, 55, 44, 1, 211, 233, 3]
        if(TEST_HISTORY_RESPONSE):
            print_history_output()
        else:
            return message_to_send


def setGeneralPeriod():
    localString = ''
    numOfGeneralParam = input(" Enter Number of general params ")
    localString += numOfGeneralParam + DELIMETER
    for i in range(int(numOfGeneralParam)):
        print(" Enter below options \n 1 : for integral period \n 2 : for algo \n 3 for DCDT")
        General_param_type =input()
        General_param_type_choice = int(General_param_type)
        localString += General_param_type + DELIMETER
        if General_param_type_choice in generalParamTypes:
            localString += generalParamTypes[General_param_type_choice]()
        # if i != int(numOfGeneralParam):
        #     localString += DELIMETER

    return localString


def setClassParam():
    {

    }

def setSensorParam():
    {

    }
    
parameterTypes = {
     1: setGeneralPeriod,
     2: setClassParam,
     3: setSensorParam,
 }

def setIntegralPeriod():
    print(" in intergral period ")
    IntegralPeriod = input("enter integral period in seconds (4digits)")
    return IntegralPeriod
    
def setAlgo():
    {

    }

def setDHDP():
    {

    }

generalParamTypes = {
    1: setIntegralPeriod,
    2: setAlgo,
    3: setDHDP,
}


if __name__ == "__main__":
    server_host = "192.168.99.26"
    server_port = 9001
    # server_host = "62.232.56.36"
    # server_port = 4301
    # message_to_send = "02201085564303" // wrong crc order 
    #message_to_send =   "0220108612108318140f1e12108318140f32000074be03"  #outpu from test1.py  
    TEST_HISTORY_RESPONSE = 0
    ETX = '03'
    STX = '02'
    CLOSE_ETX = 3
    HEADER_SIZE = 3
    EACH_SENSOR_DATA_SIZE = 25
    NUM_OF_SENSORS = 8
    TIME_SIZE_WITH_SEC = 7
    TIME_SIZE_WITHOUT_SEC = 6
    TIME_SIZE_WITHOUT_MIN_SEC = 5
    TIME_SIZE_WITHOUT_HOUR_MIN_SEC = 4
    NUM_OF_SENSORS = 8
    SIZE_STATIC_FIELD = 6
    HISTORY_PCK_HEADER_SIZE = 4
    DELIMETER = ','
    recevied_data =[]
    if(TEST_HISTORY_RESPONSE):
        # decoded_list= [2, 32, 134, 5, 12, 4, 232, 7, 12, 0, 44, 1, 3, 12, 4, 232, 7, 12, 5, 44, 1, 3, 12, 4, 232, 7, 12, 10, 44, 1, 3, 12, 4, 232, 7, 12, 15, 44, 1, 1, 5, 1, 1, 8, 1, 1, 0, 0, 0, 0, 0, 50, 42, 0, 2, 1, 2, 1, 0, 0, 0, 2, 3, 1, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 1, 0, 102, 42, 5, 2, 1, 2, 1, 0, 0, 0, 2, 3, 1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 1, 12, 4, 232, 7, 12, 20, 44, 1, 31, 137, 3]
        decoded_list= [2, 32, 134, 2, 12, 4, 232, 7, 16, 20, 44, 1, 2, 2, 12, 4, 232, 7, 16, 25, 44, 1, 86, 92, 3]
    else:
        decoded_list = []
    AENOR_DLE_DECODE_CHARACTER = 0x7F
    DLE = 0x10
    DLE_list = ['03', '02', '10', '06', '05']

    STR_ADDR = '32'
    INDICATION = '0000'

try:
    if len(sys.argv) < 2:
        print("Usage: python script.py <Destination IP>")
        sys.exit(1)

    server_host = sys.argv[1]
    print(f"input IP is {server_host}")

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
        crc_option = input("press 1 to send with correct CRC, \n 0 for wrong CRC  ")
        if(int(crc_option) == 1):
            message_to_send = "02200aa7ac03"  #correct CRC order for LAST period data 
        elif(int(crc_option) == 0):
            message_to_send = "02200aa7ab03"  #wrong CRC to test exeption message
        elif(int(crc_option) == 2):
            message_to_send = "022004466203"  #wrong CRC to test exeption message
    elif(int(choice) == 4):
        # message_to_send = "02200b8db703"  #correct CRC order for request identification 
        message_to_send = "02200bb78d03"  #correct CRC order for request identification 
    elif(int(choice) == 5):
        # message_to_send = "022009cf9703"  #correct CRC order for request status and alarm
        message_to_send = "02200997cf03"  #correct CRC order for request status and alarm
    elif(int(choice) == 6):
        SET_REQUEST = '03'
        start_time = input("Enter set date&time comma saperated (dd,mm,yyyy,hh,min,sec)")
        input_string = f'{STR_ADDR},{SET_REQUEST},{start_time}'
        print(f"{input_string}")

        message_to_send = form_packet(input_string)
    elif(int(choice) == 7):
        SET_REQUEST = '12'
        start_time = input("Enter Start date&time comma saperated (dd,mm,yyyy,hh)")
        input_string = f'{STR_ADDR},{SET_REQUEST},{start_time}'
        print(f"{input_string}")

        message_to_send = form_packet(input_string)
    elif(int(choice) == 8):
        SET_REQUEST = '13'
        start_time = input("Enter Start date&time comma saperated (dd,mm,yyyy)")
        input_string = f'{STR_ADDR},{SET_REQUEST},{start_time}'
        print(f"{input_string}")
        message_to_send = form_packet(input_string)
        # message_to_send = "02200D1204E807D78103" 

    elif(int(choice) == 9):
       message_to_send = "022007760103" 
 
    elif(int(choice) == 10):
        SET_REQUEST = '1'
        # constant_input = input("enter these values as is 3,1,44,1,2,0,3,0,1,1,8,2")
        # constant_input = '3,1,44,1,2,0,3,0,1,1,8,2'
        # constant_input = '3,1,0300,2,0,3,0,1,1,8,2'
        constant_input = '3,1,0180,2,0,3,0,1,1,8,2'
        Lenght_ID = '1'
        Length_threshold = '2,42,0'#input("Enter number of categeries for length, and each threshold ")
        Speed_ID = '2'
        Speed_threshold = '3,60,0,90,0'#input("Enter number of categeries for speed, and each threshold ")
        Num_of_paramter = '3'
        param1_value = '1,255,255,255,255,255,255,1,255,255,255,255,255,255,1,255,255,255,255,255,255,1,255,255,255,255,255,255,1,255,255,255,255,255,255,1,255,255,255,255,255,255,1,255,255,255,255,255,255,1,255,255,255,255,255,255'
        param2_value = '2,255,255,2,255,255,2,255,255,2,255,255,2,255,255,2,255,255,2,255,255,2,255,255'
        param3_value = '3,255,3,255,3,255,3,255,3,255,3,255,3,255,3,255'
        # param1_value = '1,100,100,100,100,100,100,1,100,100,100,100,100,100,1,100,100,100,100,100,100,1,100,100,100,100,100,100,1,100,100,100,100,100,100,1,100,100,100,100,100,100,1,100,100,100,100,100,100,1,100,100,100,100,100,100'
        # param2_value = '2,100,100,2,100,100,2,100,100,2,100,100,2,100,100,2,100,100,2,100,100,2,100,100'
        # param3_value = '3,100,3,100,3,100,3,100,3,100,3,100,3,100,3,100'

        input_string = f'{STR_ADDR},{SET_REQUEST},{constant_input},{Lenght_ID},{Length_threshold},{Speed_ID},{Speed_threshold},{Num_of_paramter},{param1_value},{param2_value},{param3_value}'
        # param3_value = '99,100,2024'
        # input_string = f'{Num_of_paramter},{param3_value}'
        print(f"{input_string}")

        message_to_send = form_packet(input_string)
    
    elif(int(choice) == 11):
        SET_REQUEST = '2'
        param_string = ''
       
        Num_of_paramter = input("Enter number of parameters to set ")
        param_string = Num_of_paramter + DELIMETER
        for i in range(int(Num_of_paramter)):
           General_params_type =  input("Enter parameters type ")
           param_string += General_params_type + DELIMETER
           param_type_choice = int(General_params_type)
           print(f"param_type_choice is {param_type_choice}")
           if param_type_choice in parameterTypes:
               param_string += parameterTypes[param_type_choice]()
           else:
               print("invalid param_type_choice")    

        # Number_of_general_params = '1'
        # Param_type = '1'
        # Interval_period = input('enter interval period in seconds with 4 digits: ')
        # input_string = f'{STR_ADDR},{SET_REQUEST},{Num_of_paramter},{General_params_type},{Number_of_general_params},{Param_type},{Interval_period}'
        input_string = f'{STR_ADDR},{SET_REQUEST},{param_string}'
        print(f" intput string = {input_string}")
        message_to_send = form_packet(input_string)

    elif(int(choice) == 12):
        SET_REQUEST = '8'
        param_string = ''
        General_params_type =  input("Enter parameters type \n 1:General class \n 2:Specific class 3:Sensor class\n")
        if(int(General_params_type) == 2 or int(General_params_type) == 3):
            params_value =  input("Enter sensor type: 1 for DOUBLE DET:  ")
            param_string += General_params_type + DELIMETER + params_value
        elif(int(General_params_type) == 1):
            param_string += General_params_type
        else:
            print(" invalid param type: it is either 1.2 or 3")

        input_string = f'{STR_ADDR},{SET_REQUEST},{param_string}'
        print(f" intput string = {input_string}")
        message_to_send = form_packet(input_string)

    else:
        print(f"Invalid input")
    
    if(TEST_HISTORY_RESPONSE):
        choice_to_compare = 2
    else:
        choice_to_compare = 17
    if(int(choice) != choice_to_compare):
        tcp_client(server_host, server_port, message_to_send)

except KeyboardInterrupt:
    print("\nExiting the program...")
    sys.exit(0)  # Exiting the program with status code 0
