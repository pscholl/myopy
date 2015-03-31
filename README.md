Myo.py - read raw data from myo on the cmdline
==============================================

 make myopy executable and have bluepy (https://github.com/IanHarvey/bluepy)
installed. For example if bluepy is not installed systemwide but in one
directory up, you can do:

    PYTHONPATH=../bluepy ./myo.py <addr>

 To find the address of your Myo, wiggle it and run

    hcitool -i hci0 lescan
