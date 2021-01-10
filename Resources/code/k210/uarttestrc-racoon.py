"""rc a b c d
a left/right
b forward/backward
c up/down
d yaw """


import sensor,image
import KPU as kpu
from machine import UART
from fpioa_manager import fm

print(kpu.memtest())

classes = ["racoon"]
destination = [112,112,37500]
destination_buffer = [56,56,3000]
current = []
currentlist = []


fm.register (15, fm.fpioa.UART1_TX)
fm.register (17, fm.fpioa.UART1_RX)
uart_A = UART (UART.UART1, 9600, 8, None, 1, timeout = 1000, read_buf_len = 4096)


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.set_hmirror(0)
sensor.run(1)

def mean(a):
    return int(sum(a) / len(a))

def process_target():
    global currentlist
    for x in range(6):
        img = sensor.snapshot()
        a = img.pix_to_ai()
        code = kpu.run_yolo2(task, img)
        if code:
            i = code[0]
            #print(i)
            current= [i.x()+int(i.w()/2),i.y()+int(i.h()/2),i.w()*i.h()]
            currentlist.append(current)
            #print(current)
            #print(currentlist)

    if(len(currentlist)>0):
        average = list(map(mean, zip(*currentlist)))
        print("Mean:",average)
        currentlist = []


        difference = []
        zip_object = zip(destination, average)
        for list1_i, list2_i in zip_object:
            difference.append(list1_i-list2_i)
        print("Diff:",difference)
        factor = 1

#        if abs(difference[0]) > destination_buffer[0]:
#            if (difference[0] > 0):
#                factor = -1
#            if abs(average[2]) > 9000:
#                print("1:rc "+str(int(12*factor*(difference[2]/destination[2])))+" 0 0 0")
#                return "1:rc "+str(int(12*factor*(difference[2]/destination[2])))+" 0 0 0"
#            else:
#            print("1:rc 0 0 0 "+str(int(12*factor*(difference[2]/destination[2]))))
#            return "1:rc 0 0 0 "+str(int(12*factor*(difference[2]/destination[2])))

#        if abs(difference[1]) > destination_buffer[1]:
#            if (difference[1] < 0):
#                factor = -1
#            print("1:rc 0 0 "+str(int(15*factor*(difference[2]/destination[2])))+" 0")
#            return "1:rc 0 0 "+str(int(15*factor*(difference[2]/destination[2])))+" 0"

        if abs(difference[2]) > destination_buffer[2]:
            if (difference[2] < 0):
                factor = 0

            print("1:rc 0 "+str(int((24*(difference[2]/destination[2]))*factor))+" 0 0")
            return "1:rc 0 "+str(int((24*(difference[2]/destination[2]))*factor))+" 0 0"
        print("1:rc 0 0 0 0")
        return "1:rc 0 0 0 0"
    else:
        print("0:rc 0 0 0 0")
        return "0:rc 0 0 0 0"

def run_algo():

    print("replying :)")
    rccommand = process_target()
    print(rccommand)
    uart_A.write(rccommand)


task = kpu.load("/sd/model.kmodel") #change to "/sd/name_of_the_model_file.kmodel" if loading from SD card
print(kpu.memtest())

a = kpu.set_outputs(task, 0, 7,7,30)   #the actual shape needs to match the last layer shape of your model(before Reshape)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task, 0.3, 0.3, 5, anchor) #tweak the second parameter if you're getting too many false positives

while(True):
    #if uart_A.any():
        #try:

            #read_data = uart_A.read()
            #read_str = read_data.decode('utf-8')
            #if (read_str == "1"):
                #print("string = ", read_str)
                #run_algo()
        #except  (UnicodeError):
            #pass
     run_algo()


a = kpu.deinit(task)
