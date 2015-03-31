#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from bluepy import btle

cmdline = argparse.ArgumentParser("read data from a Myo Armband")
cmdline.add_argument('addr', metavar='ADDR', type=str, help="mac-addr of the Myo (use hcitool lescan)")
args = cmdline.parse_args()

class Myo():
    def __init__(self, addr):
        self.perip   = btle.Peripheral(args.addr)
        self.service = self.perip.discoverServices()
        self.control = self.service[btle.UUID("d5060001-a904-deb9-4748-2c7f4a124842")]
        self.imu     = self.service[btle.UUID("d5060002-a904-deb9-4748-2c7f4a124842")]
        self.emgdata = self.service[btle.UUID("d5060005-a904-deb9-4748-2c7f4a124842")]
        self.classifier = self.service[btle.UUID("d5060003-a904-deb9-4748-2c7f4a124842")]

if __name__=="__main__":
    m = Myo(args.addr)
    print (m.control)
