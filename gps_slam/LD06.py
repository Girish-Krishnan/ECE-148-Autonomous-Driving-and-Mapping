# Class for LD06 lidar

import serial
from CalcLidarData import CalcLidarData
import time

class LD06:

    def __init__(self, port, baudrate, timeout, bytesize, parity, stopbits) -> None:
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, bytesize=bytesize, parity=parity, stopbits=stopbits)

        self.tmpString = ""
        self.lines = list()
        self.angles = list()
        self.distances = list()
    
    def get_lidar_data(self):

        i = 0

        loopFlag = True
        flag2c = False

        if(i % 40 == 39):
            self.angles.clear()
            self.distances.clear()
            i = 0
            

        while loopFlag:
            b = self.ser.read()
            tmpInt = int.from_bytes(b, 'big')
            
            if (tmpInt == 0x54):
                self.tmpString +=  b.hex()+" "
                flag2c = True
                continue
            
            elif(tmpInt == 0x2c and flag2c):
                self.tmpString += b.hex()

                if(not len(self.tmpString[0:-5].replace(' ','')) == 90 ):
                    self.tmpString = ""
                    loopFlag = False
                    flag2c = False
                    continue

                lidarData = CalcLidarData(self.tmpString[0:-5])
                self.angles.extend(lidarData.Angle_i)
                self.distances.extend(lidarData.Distance_i)
                    
                self.tmpString = ""
                loopFlag = False
            else:
                self.tmpString += b.hex()+" "
            
            flag2c = False
        
        i +=1

        return self.angles, self.distances

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    lidar = LD06('/dev/tty.usbserial-0001', 230400, 5.0, 8, 'N', 1)
    while True:
        print(lidar.get_lidar_data())
        time.sleep(2)