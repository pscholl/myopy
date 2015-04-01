Myo.py - read raw data from myo on the cmdline via Bluez
========================================================

 make myo.py executable and run. It is based on DBUS and the experimental
features of BLUEZ. These need to be enabled by running bluetoothd with the -E
flag. If you're Arch linux and run systemd, you can change line 8 
of /usr/lib/systemd/system/bluetooth.service from

    ExecStart=/usr/lib/bluetooth/bluetoothd 

to 

    ExecStart=/usr/lib/bluetooth/bluetoothd -E


After that, turn on you myo and run

    ./myo.py  -i <mac-addr of myo>
    2 7 -13 -6 0 0 2 1
    -8 -3 -5 2 -1 -5 -1 -2
    3 0 -2 -1 -8 0 -3 -2
    10 -5 16 3 -3 -1 -4 -1
    -16 -10 9 3 -1 0 -3 -5
    -2 2 3 -10 3 -3 -2 -1
    -11 -6 -9 7 -6 -1 -3 -5

which will print one EMG sample per line. Or if you are interested in
IMU data you can use

    ./myo.py  -e <mac-addr of myo>
    0.96514892578125 -0.0408935546875 -0.19073486328125 -0.17431640625 0.40478515625 -0.00830078125 0.98876953125 -8.5 1.5 0.3125
    0.96514892578125 -0.0418701171875 -0.1903076171875 -0.17462158203125 0.40185546875 -0.01806640625 0.99169921875 -5.9375 0.625 -0.375
    0.965087890625 -0.04229736328125 -0.1903076171875 -0.1748046875 0.412109375 -0.00634765625 0.99658203125 -3.1875 -0.4375 -0.5
    ...

which will suppress EMG data output. This print a quaternion (w,x,y,z), acceleration (x,y,z in units of g +-16) and gyroscope data (x,y,z in units of deg/s +-2000). You can also print both by not supplying any argument.

To find the mac-addr of your MYO armband use:

    hcitool lescan
    LE Scan ...
    DD:FC:BD:F1:DF:96 Myo

