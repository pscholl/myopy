#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Information based on https://github.com/thalmiclabs/myo-bluetooth/blob/master/myohw.h

import argparse, struct
from bluepy import btle
from time import sleep

cmdline = argparse.ArgumentParser("read data from a Myo Armband")
cmdline.add_argument('addr', metavar='ADDR', type=str, help="mac-addr of the Myo (use hcitool lescan)")
args = cmdline.parse_args()

class Myo(btle.DefaultDelegate):
    def __init__(self, addr, imu=None, emg=None, cls=None):
        btle.DefaultDelegate.__init__(self)

        self.perip   = btle.Peripheral(args.addr)
        self.service = self.perip.discoverServices()
        self.control = self.service[btle.UUID("d5060001-a904-deb9-4748-2c7f4a124842")]

        self.imu = self.service[btle.UUID("d5060002-a904-deb9-4748-2c7f4a124842")]
        self.emg = self.service[btle.UUID("d5060005-a904-deb9-4748-2c7f4a124842")]
        self.cls = self.service[btle.UUID("d5060003-a904-deb9-4748-2c7f4a124842")]

        self.info = self.control.getCharacteristics("d5060101-a904-deb9-4748-2c7f4a124842")[0]
        self.vers = self.control.getCharacteristics("d5060201-a904-deb9-4748-2c7f4a124842")[0]
        self.cmd  = self.control.getCharacteristics("d5060401-a904-deb9-4748-2c7f4a124842")[0]
        self.imudata = self.imu.getCharacteristics("d5060402-a904-deb9-4748-2c7f4a124842")[0]
        self.emgdata = self.emg.getCharacteristics("d5060105-a904-deb9-4748-2c7f4a124842")[0]

        self.imucb = imu
        self.embcb = emg
        self.clscb = cls

        print(self.info.read())
        print(self.vers.read())
        print(self.imudata.valHandle)
        self.perip.writeCharacteristic(self.imudata.valHandle+1, b'\x03\00', False)

        # subscribe
        self.cmd.write(struct.pack("BBBBB",
            1, # set_mode cmd
            3, # payload size
            2 if imu else 0, # send all IMU data, see myohw_imu_mode_t
            2 if emg else 0, # send filtered EMG, see myohw_emg_mode_t
            1 if cls else 0, # classifier mode on or off
        ))

        self.perip.setDelegate(self)

    def vibrate(self, time=1):
        if time < 0 or time > 3:
            raise ("must be in range [0,3]")
        #self.cmd.write(struct.pack('BBB',3,1,time),True)
        self.perip.writeCharacteristic(self.cmd.valHandle,b'\x03\x00\x01')

    def vibrate2(self, duration=100,strange=128):
        pass

    def handleNotification(self,ch,data):
        print(ch)
        print(data)


if __name__=="__main__":
    m = Myo(args.addr, True)
    m.vibrate(2)

    while True:
        if m.perip.waitForNotifications(1.0):
            continue

        print (m.imudata.read())

        sleep(.1)
