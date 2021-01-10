"""rc a b c d
a left/right
b forward/backward
c up/down
d yaw """

import sensor, image, time, math
from machine import UART
from fpioa_manager import fm
from board import board_info


green_threshold   = (0, 100, -128, -29, 12, 127)
destination = [160,120,25500]
destination_buffer = [50,40,2000]
current = []
side = 7

fm.register (board_info.PIN15, fm.fpioa.UART1_TX)
fm.register (board_info.PIN17, fm.fpioa.UART1_RX)
uart_A = UART (UART.UART1, 9600, 8, None, 1, timeout = 1000, read_buf_len = 4096)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_vflip(0)
sensor.set_hmirror(0)
clock = time.clock()



def process_tags():
    img=sensor.snapshot()
    blobs = img.find_blobs([green_threshold],\
                            area_threshold = 300,\
                            pixel_threshold = 300,\
                            merge = True)


    if blobs:
        for tag in blobs:
            img.draw_rectangle(tag.rect())
            img.draw_cross(tag.cx(), tag.cy())

            current = [tag.cx(), tag.cy(),tag.area()]
            print(current)
            zip_object = zip(destination, current)
            difference = []
            for list1_i, list2_i in zip_object:
                difference.append(list1_i-list2_i)

            print("Diff:",difference)

            factor = 1
            if abs(difference[0]) > destination_buffer[0]:
                if (difference[0] > 0):
                    factor = -1
                if abs(current[2]) > 2000:
                    print("1:rc "+str(int(12*factor*(difference[2]/destination[2])))+" 0 0 0")
                    return "1:rc "+str(int(12*factor*(difference[2]/destination[2])))+" 0 0 0"
                else:
                    print("1:rc 0 0 0 "+str(int(15*factor*(difference[2]/destination[2]))))
                    return "1:rc 0 0 0 "+str(int(15*factor*(difference[2]/destination[2])))

            if abs(difference[1]) > destination_buffer[1]:
                if (difference[1] < 0):
                    factor = -1
                print("1:rc 0 0 "+str(int(15*factor*(difference[2]/destination[2])))+" 0")
                return "1:rc 0 0 "+str(int(15*factor*(difference[2]/destination[2])))+" 0"

            if abs(difference[2]) > destination_buffer[2]:
                if (difference[2] < 0):
                    factor = 0

                print("1:rc 0 "+str(int((17*(difference[2]/destination[2]))*factor))+" 0 0")
                return "1:rc 0 "+str(int((17*(difference[2]/destination[2]))*factor))+" 0 0"

            return "1:rc 0 0 0 0"
    return "0:rc 0 0 0 0"

def run_algo():

    print("replying :)")
    rccommand = process_tags()
    print(rccommand)
    uart_A.write(rccommand)



while(1):
    #uncomment to run this code with esp32
    #if uart_A.any():
        #try:

            #read_data = uart_A.read()
            #read_str = read_data.decode('utf-8')
            #if (read_str == "1"):
                #print("string = ", read_str)
                #run_algo()
        #except  (UnicodeError):
            #pass
    #uncomment to debugging this code while connected to PC       
    run_algo()

uart_A.deinit ()
del uart_A


