#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Information based on https://github.com/thalmiclabs/myo-bluetooth/blob/master/myohw.h

import dbus.mainloop.glib; dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
from gi.repository import GObject
from struct import pack, unpack
from time import sleep
import argparse, dbus, sys

VIBS={'no':0, 'short':1, 'medium':2, 'long':3}
cmdline = argparse.ArgumentParser("read data from a Myo Armband")
cmdline.add_argument('--no-imu', '-i', action="store_true", help="do not print IMU data")
cmdline.add_argument('--no-emg', '-e', action="store_true", help="do not print EMG data")
cmdline.add_argument('--vibrate','-v', type=str, default="no", help="vibrate at the start", choices=VIBS.keys())
cmdline.add_argument('--no-disconnect', '-d', action="store_true", help="do not disconnect from Myo at program exit")
cmdline.add_argument('addr', metavar='ADDR', type=str, help="mac-addr of the Myo (use hcitool lescan)")
args = cmdline.parse_args()

class Myo():
    def char(self,service,uid):
        return dbus.Interface(
                self.bus.get_object('org.bluez', '/org/bluez/hci0/dev_%s/service%04x/char%04x'%(self.addr,service,uid)),
                dbus_interface='org.bluez.GattCharacteristic1')

    def __init__(self, addr, imu=None, emg=None, cls=None):
        addr = addr.replace(":","_")
        self.addr = addr
        bus = dbus.SystemBus()
        self.bus = bus
        myo = bus.get_object('org.bluez','/org/bluez/hci0/dev_%s'%addr)

        # Connect to the myo first
        self.dev = dbus.Interface(myo,dbus_interface="org.bluez.Device1")
        try: self.dev.Connect()
        except: pass

        # poll for interface availability
        sys.stderr.write("connecting ")
        while True:
            try: self.fwversion = self.char(0x13,0x16).ReadValue(); sleep(.5); break
            except: sys.stderr.write("."); sys.stderr.flush(); sleep(.5)
        sys.stderr.write("done\n")

        # Connect to the Characteristics
        self.cmd = self.char(0x13,0x18)

        # enable IMU notification
        if imu:
            self.char(0x1a,0x1b).StartNotify()

            # Format for motion data is w,x,y,z, ax,ay,az, gx,gy,gz, i.e. a quaternion, acceleration and gyroscope
            bus.add_signal_receiver(lambda ev,v,z: imu(*[float(x)/scale for (x,scale) in zip(unpack('10h',pack('20B',*v['Value'])),[16384,16384,16384,16384,2048,2048,2048,16,16,16])]),
                    dbus_interface='org.freedesktop.DBus.Properties',
                    path='/org/bluez/hci0/dev_%s/service001a/char001b'%addr)


        # # enable raw EMG notification
        if emg:
            self.char(0x29,0x2a).StartNotify()
            self.char(0x29,0x2d).StartNotify()
            self.char(0x29,0x30).StartNotify()
            self.char(0x29,0x33).StartNotify()

            bus.add_signal_receiver(lambda ev,v,z: emg(unpack('8b',pack('8B',*v["Value"][:8])),unpack('8b',pack('8B',*v["Value"][8:]))),
                    dbus_interface='org.freedesktop.DBus.Properties',
                    path='/org/bluez/hci0/dev_%s/service0029/char002d'%addr)
            bus.add_signal_receiver(lambda ev,v,z: emg(unpack('8b',pack('8B',*v["Value"][:8])),unpack('8b',pack('8B',*v["Value"][8:]))),
                    dbus_interface='org.freedesktop.DBus.Properties',
                    path='/org/bluez/hci0/dev_%s/service0029/char002a'%addr)
            bus.add_signal_receiver(lambda ev,v,z: emg(unpack('8b',pack('8B',*v["Value"][:8])),unpack('8b',pack('8B',*v["Value"][8:]))),
                    dbus_interface='org.freedesktop.DBus.Properties',
                    path='/org/bluez/hci0/dev_%s/service0029/char0030'%addr)
            bus.add_signal_receiver(lambda ev,v,z: emg(unpack('8b',pack('8B',*v["Value"][:8])),unpack('8b',pack('8B',*v["Value"][8:]))),
                    dbus_interface='org.freedesktop.DBus.Properties',
                    path='/org/bluez/hci0/dev_%s/service0029/char0033'%addr)

        # enable raw CLS notification, needs more magic, so disabled!
        #if cls:
        #    dbus.Interface(
        #            bus.get_object('org.bluez', '/org/bluez/hci0/dev_%s/service0021/char0022'%addr),
        #            dbus_interface='org.bluez.GattCharacteristic1').StartNotify()

        #    bus.add_signal_receiver(print,
        #            dbus_interface='org.freedesktop.DBus.Properties',
        #            path='/org/bluez/hci0/dev_%s/service0021/char002222'%addr)


        self.cmd.WriteValue([1,3,
            2 if emg else 0,  # filtered EMG data
            3 if imu else 0,  # motionen events and raw IMU
            1 if cls else 0]) # enable classification

    def vibrate(self, time=1):
        self.cmd.WriteValue([3,1,time])

if __name__=="__main__":
    loop = GObject.MainLoop()

    def emg_print(s1,s2):
        print(" ".join([str(s) for s in s1]))
        print(" ".join([str(s) for s in s2]))
        sys.stdout.flush()

    def fprint(*args):
        print(*args)
        sys.stdout.flush()

    m = Myo(args.addr,
            None if args.no_imu else fprint,
            None if args.no_emg else emg_print)

    m.vibrate(VIBS[args.vibrate])

    if args.no_imu and args.no_emg and args.no_classification:
        sys.exit(0)

    try: loop.run()
    except KeyboardInterrupt:
        if not args.no_disconnect: sys.stderr.write("disconnecting\n"); m.dev.Disconnect()
        sys.exit(0)
