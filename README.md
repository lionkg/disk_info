# disk_info
Module for getting block devices information 

## WARNING: work in progress ##

This is a python module for retriving information on linux blk devices. It is able to detec MegaRaid controllers/arrays with underlying physical devices.

What is implemented
* Bock device detection - diskdrive.py
* MegaRaid controllers detecrtion - raidcontrollers.py
* MegaRaid arrays detection - raidarray.py

TO-DO
* Implemet function for getting dlock device stats and errors
* Implemet classes for Adaptec based raid arrays

linux commands used:
* lsblk from util-linux
* storcli64 Ver 1.21.06
* smartctl from smartmontools package

Tested on Ubuntu 18.04 and python 3.5.2+

### This code is purely infomational and does not make any modifications to the system. ###

P.s.: This is my first more or less 'meaningfull' python project so please be kind ;)
