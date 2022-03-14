# -*- coding: utf-8 -*-

'''
Reuben Brewer, Ph.D.
reuben.brewer@gmail.com
www.reubotics.com

Apache 2 License
Software Revision D, 03/13/2022

Verified working on: Python 2.7, 3.8 for Windows 8.1, 10 64-bit and Raspberry Pi Buster (no Mac testing yet).
'''

__author__ = 'reuben.brewer'

import os, sys, platform
import time, datetime
import math, collections
import numpy, struct
import threading
import inspect #To enable 'TellWhichFileWereIn'
import traceback

###############
if sys.version_info[0] < 3:
    from Tkinter import * #Python 2
    import tkFont
    import ttk
else:
    from tkinter import * #Python 3
    import tkinter.font as tkFont #Python 3
    from tkinter import ttk
###############

###############
if sys.version_info[0] < 3:
    import Queue  # Python 2
else:
    import queue as Queue  # Python 3
###############

###############
if sys.version_info[0] < 3:
    from builtins import raw_input as input
else:
    from future.builtins import input as input
############### #"sudo pip3 install future" (Python 3) AND "sudo pip install future" (Python 2)

###############
import platform
if platform.system() == "Windows":
    import ctypes
    winmm = ctypes.WinDLL('winmm')
    winmm.timeBeginPeriod(1) #Set minimum timer resolution to 1ms so that time.sleep(0.001) behaves properly.
###############

##########################################
import serial
from sys import platform as _platform
from serial.tools import list_ports
##########################################

##########################################
'''
ftd2xx

### Windows:
If the required driver is already on your Windows machine, then it will be installed automatically when the U2D2 is first plugged-in (note that this installation will occur separately for EACH separate USB port, and that the latency_timer will need to be set for EACH separate USB port.
However, if you don't see a new USB-Serial device appearing with a new "COM" number in Device Manger after Windows says it's done installing your new device, then you'll need to install the driver separately using Windows_FTDI_USBserial_driver_061020-->CDM21228_Setup.exe

To install the Python module:
pip install ftd2xx==1.0 (this 1.0 is VERY IMPORTANT as the later versions appear to have issues, including when installed from the whl file 'pip install C:\ftd2xx-1.1.2-py2-none-any.whl').

### Raspberry Pi:
To install the Python module:
sudo pip install ftd2xx (perhaps sudo pip install ftd2xx==1.0)

To install the driver:
Download the 1.4.6 ARMv6 hard-float (suits Raspberry Pi) source code from ftdi (http://www.ftdichip.com/Drivers/D2XX.htm) or use the included file.
Install following these instructions (modified from the readme that comes with the driver):

cd build
sudo -s
cp libftd2xx.* /usr/local/lib
chmod 0755 /usr/local/lib/libftd2xx.so.1.4.6
ln -sf /usr/local/lib/libftd2xx.so.1.4.6 /usr/local/lib/libftd2xx.so
exit
THIS LAST STEP ISN’T IN THE READ ME BUT IS CRITICAL: “sudo ldconfig” so that your code can find the new library.
###########################
'''

if sys.version_info[0] < 3:
    import ftd2xx as ftd2xx
else:
    import ftd2xx as ftd2xx #Note that pip3 thinks this module is called "ftd2xx-py3k", but it imports as "ftd2xx"

##########################################

##########################################
#Must install manually from .\DynamixelSDK-3.7.21\python using "sudo python setup.py install".
#Note that "pip show dynamixel_sdk" says it's version 3.6.0, but it's actually 3.7.21.
#Note also that Reuben modified some code in "port_handler.py" before installation.
from dynamixel_sdk import *
##########################################


#http://stackoverflow.com/questions/19087515/subclassing-tkinter-to-create-a-custom-widget
class Dynamixel_Protocol2_Xseries_ReubenPython2and3Class(Frame): #Subclass the Tkinter Frame

    #######################################################################################################################
    ####################################################################################################################### CLASS VARIABLE DECLARATIONS
    angular_units_acceptable_list = ["raw", "dynamixelunits", "rad", "deg", "rev"]
    angular_speed_units_acceptable_list = ["raw", "dynamixelunits", "radpersec", "degpersec", "revpersec", "revpermin"]
    current_units_acceptable_list = ["raw", "dynamixelunits", "milliamps", "amps", "percent"]
    control_type_acceptable_list = ["CurrentControl", "VelocityControl", "PositionControl", "ExtendedPositionControlMultiTurn", "CurrentBasedPositionControl", "PWMcontrol"]
    MotorType_AcceptableDict = dict([("None", dict([("MotorType", -1)])),
                                            ("NONE", dict([("MotorType", -1)])),
                                            ("XM540-W270-R", dict([("MotorType", 0)]))])
    #######################################################################################################################
    #######################################################################################################################
    
    #######################################################################################################################
    def __init__(self, setup_dict): #Subclass the Tkinter Frame

        print("#################### Dynamixel_Protocol2_Xseries_ReubenPython2and3Class __init__ starting. ####################")

        self.EXIT_PROGRAM_FLAG = 0
        self.OBJECT_CREATED_SUCCESSFULLY_FLAG = -1
        self.EnableInternal_MyPrint_Flag = 0

        ##########################################
        if platform.system() == "Linux":

            if "raspberrypi" in platform.uname(): #os.uname() doesn't work in windows
                self.my_platform = "pi"
            else:
                self.my_platform = "linux"

        elif platform.system() == "Windows":
            self.my_platform = "windows"

        elif platform.system() == "Darwin":
            self.my_platform = "mac"

        else:
            self.my_platform = "other"

        print("The OS platform is: " + self.my_platform)
        ##########################################

        ##########################################
        ##########################################
        if "GUIparametersDict" in setup_dict:
            self.GUIparametersDict = setup_dict["GUIparametersDict"]

            ##########################################
            if "USE_GUI_FLAG" in self.GUIparametersDict:
                self.USE_GUI_FLAG = self.PassThrough0and1values_ExitProgramOtherwise("USE_GUI_FLAG", self.GUIparametersDict["USE_GUI_FLAG"])
            else:
                self.USE_GUI_FLAG = 0

            print("USE_GUI_FLAG = " + str(self.USE_GUI_FLAG))
            ##########################################

            ##########################################
            if "root" in self.GUIparametersDict:
                self.root = self.GUIparametersDict["root"]
                self.RootIsOwnedExternallyFlag = 1
            else:
                self.root = None
                self.RootIsOwnedExternallyFlag = 0

            print("RootIsOwnedExternallyFlag = " + str(self.RootIsOwnedExternallyFlag))
            ##########################################

            ##########################################
            if "GUI_RootAfterCallbackInterval_Milliseconds" in self.GUIparametersDict:
                self.GUI_RootAfterCallbackInterval_Milliseconds = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_RootAfterCallbackInterval_Milliseconds", self.GUIparametersDict["GUI_RootAfterCallbackInterval_Milliseconds"], 0.0, 1000.0))
            else:
                self.GUI_RootAfterCallbackInterval_Milliseconds = 30

            print("GUI_RootAfterCallbackInterval_Milliseconds = " + str(self.GUI_RootAfterCallbackInterval_Milliseconds))
            ##########################################

            ##########################################
            if "EnableInternal_MyPrint_Flag" in self.GUIparametersDict:
                self.EnableInternal_MyPrint_Flag = self.PassThrough0and1values_ExitProgramOtherwise("EnableInternal_MyPrint_Flag", self.GUIparametersDict["EnableInternal_MyPrint_Flag"])
            else:
                self.EnableInternal_MyPrint_Flag = 0

            print("EnableInternal_MyPrint_Flag: " + str(self.EnableInternal_MyPrint_Flag))
            ##########################################

            ##########################################
            if "PrintToConsoleFlag" in self.GUIparametersDict:
                self.PrintToConsoleFlag = self.PassThrough0and1values_ExitProgramOtherwise("PrintToConsoleFlag", self.GUIparametersDict["PrintToConsoleFlag"])
            else:
                self.PrintToConsoleFlag = 1

            print("PrintToConsoleFlag: " + str(self.PrintToConsoleFlag))
            ##########################################

            ##########################################
            if "NumberOfPrintLines" in self.GUIparametersDict:
                self.NumberOfPrintLines = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("NumberOfPrintLines", self.GUIparametersDict["NumberOfPrintLines"], 0.0, 50.0))
            else:
                self.NumberOfPrintLines = 10

            print("NumberOfPrintLines = " + str(self.NumberOfPrintLines))
            ##########################################

            ##########################################
            if "UseBorderAroundThisGuiObjectFlag" in self.GUIparametersDict:
                self.UseBorderAroundThisGuiObjectFlag = self.PassThrough0and1values_ExitProgramOtherwise("UseBorderAroundThisGuiObjectFlag", self.GUIparametersDict["UseBorderAroundThisGuiObjectFlag"])
            else:
                self.UseBorderAroundThisGuiObjectFlag = 0

            print("UseBorderAroundThisGuiObjectFlag: " + str(self.UseBorderAroundThisGuiObjectFlag))
            ##########################################

            ##########################################
            if "GUI_ROW" in self.GUIparametersDict:
                self.GUI_ROW = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_ROW", self.GUIparametersDict["GUI_ROW"], 0.0, 1000.0))
            else:
                self.GUI_ROW = 0

            print("GUI_ROW = " + str(self.GUI_ROW))
            ##########################################

            ##########################################
            if "GUI_COLUMN" in self.GUIparametersDict:
                self.GUI_COLUMN = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_COLUMN", self.GUIparametersDict["GUI_COLUMN"], 0.0, 1000.0))
            else:
                self.GUI_COLUMN = 0

            print("GUI_COLUMN = " + str(self.GUI_COLUMN))
            ##########################################

            ##########################################
            if "GUI_PADX" in self.GUIparametersDict:
                self.GUI_PADX = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_PADX", self.GUIparametersDict["GUI_PADX"], 0.0, 1000.0))
            else:
                self.GUI_PADX = 0

            print("GUI_PADX = " + str(self.GUI_PADX))
            ##########################################

            ##########################################
            if "GUI_PADY" in self.GUIparametersDict:
                self.GUI_PADY = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_PADY", self.GUIparametersDict["GUI_PADY"], 0.0, 1000.0))
            else:
                self.GUI_PADY = 0

            print("GUI_PADY = " + str(self.GUI_PADY))
            ##########################################

            ##########################################
            if "GUI_ROWSPAN" in self.GUIparametersDict:
                self.GUI_ROWSPAN = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_ROWSPAN", self.GUIparametersDict["GUI_ROWSPAN"], 0.0, 1000.0))
            else:
                self.GUI_ROWSPAN = 0

            print("GUI_ROWSPAN = " + str(self.GUI_ROWSPAN))
            ##########################################

            ##########################################
            if "GUI_COLUMNSPAN" in self.GUIparametersDict:
                self.GUI_COLUMNSPAN = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_COLUMNSPAN", self.GUIparametersDict["GUI_COLUMNSPAN"], 0.0, 1000.0))
            else:
                self.GUI_COLUMNSPAN = 0

            print("GUI_COLUMNSPAN = " + str(self.GUI_COLUMNSPAN))
            ##########################################

            ##########################################
            if "GUI_STICKY" in self.GUIparametersDict:
                self.GUI_STICKY = str(self.GUIparametersDict["GUI_STICKY"])
            else:
                self.GUI_STICKY = "w"

            print("GUI_STICKY = " + str(self.GUI_STICKY))
            ##########################################

        else:
            self.GUIparametersDict = dict()
            self.USE_GUI_FLAG = 0
            print("No GUIparametersDict present, setting USE_GUI_FLAG = " + str(self.USE_GUI_FLAG))

        print("GUIparametersDict = " + str(self.GUIparametersDict))
        ##########################################
        ##########################################

        ##########################################
        self.PrintToGui_Label_TextInputHistory_List = [" "]*self.NumberOfPrintLines
        self.PrintToGui_Label_TextInput_Str = ""
        self.GUI_ready_to_be_updated_flag = 0
        
        self.TKinter_LightRedColor = '#%02x%02x%02x' % (255, 150, 150)  # RGB
        self.TKinter_LightGreenColor = '#%02x%02x%02x' % (150, 255, 150)  # RGB
        self.TKinter_LightBlueColor = '#%02x%02x%02x' % (150, 150, 255)  # RGB
        self.TKinter_LightYellowColor = '#%02x%02x%02x' % (255, 255, 150)  # RGB
        self.TKinter_DefaultGrayColor = '#%02x%02x%02x' % (240, 240, 240)  # RGB
        ##########################################

        self.NumberOfMotors = len(setup_dict["MotorType_StringList"])
        #print("NumberOfMotors: " + str(self.NumberOfMotors))

        self.device_connected_flag = 0
        self.serialMainThread_still_running_flag = 0

        self.serialObject = serial.Serial()
        self.serial_connected_flag = 0
        self.TimeToWaitBetweenCriticalInstructions = 0.002

        self.PWM_DynamixelUnits_max = [-1] * self.NumberOfMotors
        self.PWM_DynamixelUnits_min = [-1] * self.NumberOfMotors
        self.PWMReceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.PWM_DynamixelUnits = [-1] * self.NumberOfMotors
        self.PWM_DynamixelUnits_TO_BE_SET = [-1] * self.NumberOfMotors
        self.PWM_DynamixelUnits_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.PWM_DynamixelUnits_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors

        self.Current_DynamixelUnits_max = [-1] * self.NumberOfMotors
        self.Current_DynamixelUnits_min = [-1] * self.NumberOfMotors
        self.CurrentReceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.CurrentReceived_Amps = [-1] * self.NumberOfMotors
        self.CurrentReceived_Percent0to1 = [-1] * self.NumberOfMotors
        self.Current_DynamixelUnits = [-1] * self.NumberOfMotors
        self.Current_DynamixelUnits_TO_BE_SET = [-1] * self.NumberOfMotors
        self.Current_DynamixelUnits_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors

        self.Velocity_DynamixelUnits_max = [-1] * self.NumberOfMotors
        self.Velocity_DynamixelUnits_min = [-1] * self.NumberOfMotors
        self.VelocityReceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.Velocity_DynamixelUnits = [-1] * self.NumberOfMotors
        self.Velocity_DynamixelUnits_TO_BE_SET = [-1] * self.NumberOfMotors
        self.Velocity_DynamixelUnits_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors

        self.Position_DynamixelUnits_max = [-1] * self.NumberOfMotors
        self.Position_DynamixelUnits_min = [-1] * self.NumberOfMotors
        self.PositionReceived_DynamixelUnits = [0] * self.NumberOfMotors
        self.PositionReceived_Deg = [0] * self.NumberOfMotors
        self.Position_DynamixelUnits = [0] * self.NumberOfMotors
        self.Position_DynamixelUnits_TO_BE_SET = [0] * self.NumberOfMotors
        self.Position_DynamixelUnits_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.MotionDirectionCommandedByExternalProgram = [-1] * self.NumberOfMotors

        self.MaxPWM_DynamixelUnits_max = [-1] * self.NumberOfMotors
        self.MaxPWM_DynamixelUnits_min = [-1] * self.NumberOfMotors
        self.MaxPWMreceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.MaxPWM_DynamixelUnits = [-1] * self.NumberOfMotors
        self.MaxPWM_DynamixelUnits_TO_BE_SET = [-1] * self.NumberOfMotors
        self.MaxPWM_DynamixelUnits_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.MaxPWM_DynamixelUnits_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors

        self.MinPositionLimit_max = [-1] * self.NumberOfMotors
        self.MinPositionLimit_min = [-1] * self.NumberOfMotors
        self.MinPositionLimitReceived = [-1] * self.NumberOfMotors
        self.MinPositionLimit = [-1] * self.NumberOfMotors
        self.MinPositionLimit_TO_BE_SET = [-1] * self.NumberOfMotors
        self.MinPositionLimit_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.MinPositionLimit_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        
        self.MaxPositionLimit_max = [-1] * self.NumberOfMotors
        self.MaxPositionLimit_min = [-1] * self.NumberOfMotors
        self.MaxPositionLimitReceived = [-1] * self.NumberOfMotors
        self.MaxPositionLimit = [-1] * self.NumberOfMotors
        self.MaxPositionLimit_TO_BE_SET = [-1] * self.NumberOfMotors
        self.MaxPositionLimit_NeedsToBeChangedFlag = [0] * self.NumberOfMotors
        self.MaxPositionLimit_GUI_NeedsToBeChangedFlag = [0] * self.NumberOfMotors

        self.ToggleMinMax_state = [-1] * self.NumberOfMotors
        self.ToggleMinMax_TO_BE_SET = [-1] * self.NumberOfMotors
        self.ToggleMinMax_NeedsToTakePlaceFlag = [-1] * self.NumberOfMotors
        self.ResetSerial_NeedsToTakePlaceFlag = [-1] * self.NumberOfMotors
        self.Reboot_NeedsToTakePlaceFlag = [-1] * self.NumberOfMotors
        self.OperatingModeReceived_int = [-1] * self.NumberOfMotors
        self.OperatingModeReceived_string = ["default"] * self.NumberOfMotors
        self.RealTimeTicksMillisec = [-1] * self.NumberOfMotors
        self.RealTimeTicksMillisec_last = [-1] * self.NumberOfMotors

        self.TorqueReceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.VoltageReceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.TemperatureReceived_DynamixelUnits = [-1] * self.NumberOfMotors
        self.MovingStateReceived_DynamixelUnits = [-1] * self.NumberOfMotors

        self.ModelNumber_Received = [-1] * self.NumberOfMotors
        self.FWversion_Received = [-1] * self.NumberOfMotors
        self.ID_Received = [-1] * self.NumberOfMotors
        self.ReturnDelayTimeMicroSeconds_Received = [-1] * self.NumberOfMotors
        self.TemperatureHighestLimit_Received = [-1] * self.NumberOfMotors
        self.VoltageLowestLimit_Received = [-1] * self.NumberOfMotors
        self.VoltageHighestLimit_Received = [-1] * self.NumberOfMotors

        self.ErrorFlag_BYTE = [-1] * self.NumberOfMotors
        self.ErrorFlag_Overload_Received = [-1] * self.NumberOfMotors
        self.ErrorFlag_ElectricalShock_Received = [-1] * self.NumberOfMotors
        self.ErrorFlag_MotorEncoder_Received = [-1] * self.NumberOfMotors
        self.ErrorFlag_Overheating_Received = [-1] * self.NumberOfMotors
        self.ErrorFlag_InputVoltage_Received = [-1] * self.NumberOfMotors

        self.AskForInfrequentDataReadLoopCounter = [0] * self.NumberOfMotors

        self.EngagedState = [0]*self.NumberOfMotors #TO BE SET LATER. DEFINED HERE TO PREVENT GUI THREAD CREATION ERRORS.
        self.EngagedState_TO_BE_SET = [0]*self.NumberOfMotors
        self.EngagedState_NeedsToBeChangedFlag = [0]*self.NumberOfMotors
        self.EngagedState_GUI_NeedsToBeChangedFlag = [0]*self.NumberOfMotors
        self.StoppedState = [-1]*self.NumberOfMotors

        self.LEDstate = [1]*self.NumberOfMotors #TO BE SET LATER. DEFINED HERE TO PREVENT GUI THREAD CREATION ERRORS.
        self.LEDstate_TO_BE_SET = [1]*self.NumberOfMotors
        self.LEDstate_NeedsToBeChangedFlag = [0]*self.NumberOfMotors
        self.LEDstate_GUI_NeedsToBeChangedFlag = [0]*self.NumberOfMotors

        self.HasMotorEverBeenInitializedFlag = [0]*self.NumberOfMotors

        self.CurrentTime_CalculatedFromMainThread = -11111.0
        self.StartingTime_CalculatedFromMainThread = -11111.0
        self.LastTime_CalculatedFromMainThread = -11111.0
        self.DataStreamingFrequency_CalculatedFromMainThread = -11111.0
        self.DataStreamingDeltaT_CalculatedFromMainThread = -11111.0
        self.LoopCounter_CalculatedFromMainThread = 0

        self.DataStreamingFrequency_RealTimeTicksMillisecFromDynamixel = [-1]*self.NumberOfMotors
        self.DataStreamingDeltaT_RealTimeTicksMillisecFromDynamixel = [-1]*self.NumberOfMotors

        #########################################################
        #########################################################
        
        ##########################################
        if "SerialNumber" in setup_dict:
            self.SerialNumber = setup_dict["SerialNumber"]
        else:
            self.SerialNumber = "-1"
        ##########################################

        ##########################################
        if "NameForU2D2UserProvided" in setup_dict:
            self.NameForU2D2UserProvided = setup_dict["NameForU2D2UserProvided"]
        else:
            self.NameForU2D2UserProvided = "default"
        ##########################################

        ##########################################
        ##########################################
        print("@@@@@@@@@@@@@@@@@@@@@@@@ U2D2 (" + str(self.NameForU2D2UserProvided) + ") SerialNumber = " + str(self.SerialNumber) + " @@@@@@@@@@@@@@@@@@@@@@@@")
        ##########################################
        ##########################################

        ##########################################
        if "SerialBaudRate" in setup_dict:
            self.SerialBaudRate = int(
                self.PassThroughFloatValuesInRange_ExitProgramOtherwise("SerialBaudRate", setup_dict["SerialBaudRate"], 9600, 4500000))

        else:
            self.SerialBaudRate = 4000000

        self.MyPrint_WithoutLogFile("SerialBaudRate: " + str(self.SerialBaudRate))
        ##########################################

        ##########################################
        if "EnableInternal_MyPrint_Flag" in setup_dict:
            self.EnableInternal_MyPrint_Flag = self.PassThrough0and1values_ExitProgramOtherwise("EnableInternal_MyPrint_Flag", setup_dict["EnableInternal_MyPrint_Flag"])
        else:
            self.EnableInternal_MyPrint_Flag = 0

        self.MyPrint_WithoutLogFile("EnableInternal_MyPrint_Flag: " + str(self.EnableInternal_MyPrint_Flag))
        ##########################################

        ##########################################
        if "UseBorderAroundThisGuiObjectFlag" in setup_dict:
            self.UseBorderAroundThisGuiObjectFlag = self.PassThrough0and1values_ExitProgramOtherwise("UseBorderAroundThisGuiObjectFlag", setup_dict["UseBorderAroundThisGuiObjectFlag"])
        else:
            self.UseBorderAroundThisGuiObjectFlag = 0

        self.MyPrint_WithoutLogFile("UseBorderAroundThisGuiObjectFlag: " + str(self.UseBorderAroundThisGuiObjectFlag))
        ##########################################

        ##########################################
        if "GUI_UPDATE_DELAY_MS" in setup_dict:
            self.GUI_UPDATE_DELAY_MS = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_UPDATE_DELAY_MS", setup_dict["GUI_UPDATE_DELAY_MS"], 0.0, 100000))

        else:
            self.GUI_UPDATE_DELAY_MS = 30

        self.MyPrint_WithoutLogFile("GUI_UPDATE_DELAY_MS: " + str(self.GUI_UPDATE_DELAY_MS))
        ##########################################

        ##########################################
        if "MainThread_TimeToSleepEachLoop" in setup_dict:
            self.MainThread_TimeToSleepEachLoop = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("MainThread_TimeToSleepEachLoop", setup_dict["MainThread_TimeToSleepEachLoop"], 0.001, 100000)

        else:
            self.MainThread_TimeToSleepEachLoop = 0.005

        self.MyPrint_WithoutLogFile("MainThread_TimeToSleepEachLoop: " + str(self.MainThread_TimeToSleepEachLoop))
        ##########################################

        ##########################################
        if "ENABLE_GETS" in setup_dict:
            self.ENABLE_GETS = self.PassThrough0and1values_ExitProgramOtherwise("ENABLE_GETS", setup_dict["ENABLE_GETS"])
        else:
            self.ENABLE_GETS = 0

        self.MyPrint_WithoutLogFile("ENABLE_GETS: " + str(self.ENABLE_GETS))
        ##########################################

        ##########################################
        if "ENABLE_SETS" in setup_dict:
            self.ENABLE_SETS = self.PassThrough0and1values_ExitProgramOtherwise("ENABLE_SETS", setup_dict["ENABLE_SETS"])
        else:
            self.ENABLE_SETS = 0

        self.MyPrint_WithoutLogFile("ENABLE_SETS: " + str(self.ENABLE_SETS))
        ##########################################

        ##########################################
        self.MotorType_Int = []
        if "MotorType_StringList" not in setup_dict:
            self.OBJECT_CREATED_SUCCESSFULLY_FLAG = 0
            self.MyPrint_WithoutLogFile("Dynamixel_Protocol2_Xseries_ReubenPython2and3Class ERROR: Must initialize object with 'MotorType_StringList' argument.")
            return

        else:
            self.MotorType_StringList = setup_dict["MotorType_StringList"]

            for index, MotorType_element in enumerate(self.MotorType_StringList):
                if MotorType_element not in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.MotorType_AcceptableDict:
                    self.MyPrint_WithoutLogFile("Dynamixel_Protocol2_Xseries_ReubenPython2and3Class ERROR: MotorType of " + str(MotorType_element) + " is not a supported type.")
                else:
                    motor_type_dict_temp = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.MotorType_AcceptableDict[MotorType_element]
                    self.MotorType_Int.append(motor_type_dict_temp["MotorType"])
        ##########################################

        ##########################################
        self.MotorName_StringList = []
        if "MotorName_StringList" in setup_dict:
            MotorName_StringList_temp = setup_dict["MotorName_StringList"]
            print("########################## " + str(MotorName_StringList_temp) + " ########################## ")

            try:
                for element in MotorName_StringList_temp:
                    self.MotorName_StringList.append(str(element))
            except:
                exceptions = sys.exc_info()[0]
                self.MyPrint_WithoutLogFile("MotorName_StringList coldn't convert to string, Exceptions: %s" % exceptions)
                self.MotorName_StringList = [""] * self.NumberOfMotors
        else:
            self.MotorName_StringList = [""] * self.NumberOfMotors
        ##########################################

        ##########################################
        self.OperatingMode_AcceptableList = ["CurrentControl", "VelocityControl", "PositionControl", "ExtendedPositionControlMultiTurn", "CurrentBasedPositionControl", "PWMcontrol"]
        self.ControlType_AcceptableList = self.OperatingMode_AcceptableList

        self.ControlType_StartingValueList = []
        if "ControlType_StartingValueList" in setup_dict:
            self.ControlType_StartingValueList = setup_dict["ControlType_StartingValueList"]

        else:
            self.ControlType_StartingValueList = ["PositionControl"] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("ControlType_StartingValueList: " + str(self.ControlType_StartingValueList))

        self.ControlType = list(self.ControlType_StartingValueList)
        self.ControlType_TO_BE_SET = list(self.ControlType_StartingValueList)
        self.ControlType_NEEDS_TO_BE_CHANGED_FLAG = [0] * self.NumberOfMotors
        self.ControlType_GUI_NEEDS_TO_BE_CHANGED_FLAG = [0] * self.NumberOfMotors
        self.ControlType_NEEDS_TO_BE_ASKED_FLAG = [1] * self.NumberOfMotors
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        self.Position_DynamixelUnits_StartingValueList = []
        self.Position_Deg_StartingValueList = []
        if "Position_Deg_StartingValueList" in setup_dict:
            temp_list = setup_dict["Position_Deg_StartingValueList"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    item_dynamixelunits = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(item, "deg")["dynamixelunits"]
                    if 1:#item >= 0 and item <= 4095.0:
                        self.Position_Deg_StartingValueList.append(item)
                        self.Position_DynamixelUnits_StartingValueList.append(item_dynamixelunits)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Position_DynamixelUnits_StartingValueList values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Position_Deg_StartingValueList values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Position_Deg_StartingValueList was not valid.")
                return

        else:
            self.Position_Deg_StartingValueList = [0] * self.NumberOfMotors
            self.Position_DynamixelUnits_StartingValueList = [0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Position_Deg_StartingValueList valid: " + str(self.Position_Deg_StartingValueList))
        self.MyPrint_WithoutLogFile("Position_DynamixelUnits_StartingValueList valid: " + str(self.Position_DynamixelUnits_StartingValueList))
        ##########################################

        ##########################################
        self.Position_Deg_max = []
        self.Position_DynamixelUnits_max = []
        if "Position_Deg_max" in setup_dict:
            temp_list = setup_dict["Position_Deg_max"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    item_dynamixelunits = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(item, "deg")["dynamixelunits"]
                    if 1:#item_dynamixelunits >= 0 and item <= 4095.0:
                        self.Position_Deg_max.append(item)
                        self.Position_DynamixelUnits_max.append(item_dynamixelunits)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Position_DynamixelUnits_max values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Position_Deg_max values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Position_Deg_max was not valid.")
                return
        else:
            self.Position_DynamixelUnits_max = [4095.0] * self.NumberOfMotors
            self.Position_Deg_max = [Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(4095.0, "dynamixelunits")["deg"] ] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Position_DynamixelUnits_max valid: " + str(self.Position_DynamixelUnits_max))
        ##########################################

        ##########################################
        self.Position_Deg_min = []
        self.Position_DynamixelUnits_min = []
        if "Position_Deg_min" in setup_dict:
            temp_list = setup_dict["Position_Deg_min"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    item_dynamixelunits = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(item, "deg")["dynamixelunits"]
                    if 1:#item_dynamixelunits >= 0 and item <= 4095.0:
                        self.Position_Deg_min.append(item)
                        self.Position_DynamixelUnits_min.append(item_dynamixelunits)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Position_DynamixelUnits_min values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Position_Deg_min values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Position_Deg_min was not valid.")
                return
        else:
            self.Position_DynamixelUnits_min = [4095.0] * self.NumberOfMotors
            self.Position_Deg_min = [Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(4095.0, "dynamixelunits")["deg"] ] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Position_DynamixelUnits_min valid: " + str(self.Position_DynamixelUnits_min))
        ##########################################
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        self.Velocity_DynamixelUnits_StartingValueList = []
        if "Velocity_DynamixelUnits_StartingValueList" in setup_dict:
            temp_list = setup_dict["Velocity_DynamixelUnits_StartingValueList"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= -1023.0 and item <= 1023.0:
                        self.Velocity_DynamixelUnits_StartingValueList.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Velocity_DynamixelUnits_StartingValueList values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Velocity_DynamixelUnits_StartingValueList values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Velocity_DynamixelUnits_StartingValueList was not valid.")
                return

        else:
            self.Velocity_DynamixelUnits_StartingValueList = [1023.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Velocity_DynamixelUnits_StartingValueList valid: " + str(self.Velocity_DynamixelUnits_StartingValueList))
        ##########################################

        ##########################################
        self.Velocity_DynamixelUnits_max = []
        if "Velocity_DynamixelUnits_max" in setup_dict:
            temp_list = setup_dict["Velocity_DynamixelUnits_max"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= -1023.0 and item <= 1023.0:
                        self.Velocity_DynamixelUnits_max.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Velocity_DynamixelUnits_max values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Velocity_DynamixelUnits_max values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Velocity_DynamixelUnits_max was not valid.")
                return
        else:
            self.Velocity_DynamixelUnits_max = [1023.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Velocity_DynamixelUnits_max valid: " + str(self.Velocity_DynamixelUnits_max))
        ##########################################

        ##########################################
        self.Velocity_DynamixelUnits_min = []
        if "Velocity_DynamixelUnits_min" in setup_dict:
            temp_list = setup_dict["Velocity_DynamixelUnits_min"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= -1023.0 and item <= 1023.0:
                        self.Velocity_DynamixelUnits_min.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Velocity_DynamixelUnits_min values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Velocity_DynamixelUnits_min values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Velocity_DynamixelUnits_min was not valid.")
                return
        else:
            self.Velocity_DynamixelUnits_min = [-1023.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Velocity_DynamixelUnits_min valid: " + str(self.Velocity_DynamixelUnits_min))
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        self.Current_DynamixelUnits_StartingValueList = []
        if "Current_DynamixelUnits_StartingValueList" in setup_dict:
            temp_list = setup_dict["Current_DynamixelUnits_StartingValueList"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= -2047.0 and item <= 2047.0:
                        self.Current_DynamixelUnits_StartingValueList.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Current_DynamixelUnits_StartingValueList values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Current_DynamixelUnits_StartingValueList values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Current_DynamixelUnits_StartingValueList was not valid.")
                return

        else:
            self.Current_DynamixelUnits_StartingValueList = [2047.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Current_DynamixelUnits_StartingValueList valid: " + str(self.Current_DynamixelUnits_StartingValueList))
        ##########################################

        ##########################################
        self.Current_DynamixelUnits_max = []
        self.Current_Percent0to1_max = []
        if "Current_Percent0to1_max" in setup_dict:
            temp_list = setup_dict["Current_Percent0to1_max"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = item
                    item_dynamixel_units = int(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllCurrentUnits(item, "percent")["dynamixelunits"])
                    if item >= 0 and item <= 1:
                        self.Current_Percent0to1_max.append(item)
                        self.Current_DynamixelUnits_max.append(item_dynamixel_units)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Current_Percent0to1_max values must be in the range [0, 1].")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Current_Percent0to1_max values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Current_Percent0to1_max was not valid.")
                return
        else:
            self.Current_Percent0to1_max = [1.0] * self.NumberOfMotors
            self.Current_DynamixelUnits_max = [2047.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Current_Percent0to1_max valid: " + str(self.Current_Percent0to1_max))
        self.MyPrint_WithoutLogFile("Current_DynamixelUnits_max valid: " + str(self.Current_DynamixelUnits_max))
        ##########################################

        ##########################################
        self.Current_DynamixelUnits_min = []
        if "Current_DynamixelUnits_min" in setup_dict:
            temp_list = setup_dict["Current_DynamixelUnits_min"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= -2047.0 and item <= 2047.0:
                        self.Current_DynamixelUnits_min.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: Current_DynamixelUnits_min values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: Current_DynamixelUnits_min values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("Current_DynamixelUnits_min was not valid.")
                return
        else:
            self.Current_DynamixelUnits_min = [-2047.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("Current_DynamixelUnits_min valid: " + str(self.Current_DynamixelUnits_min))
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        self.PWM_DynamixelUnits_StartingValueList = []
        if "PWM_DynamixelUnits_StartingValueList" in setup_dict:
            temp_list = setup_dict["PWM_DynamixelUnits_StartingValueList"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= 0 and item <= 885.0:
                        self.PWM_DynamixelUnits_StartingValueList.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: PWM_DynamixelUnits_StartingValueList values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: PWM_DynamixelUnits_StartingValueList values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("PWM_DynamixelUnits_StartingValueList was not valid.")
                return

        else:
            self.PWM_DynamixelUnits_StartingValueList = [885.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("PWM_DynamixelUnits_StartingValueList valid: " + str(self.PWM_DynamixelUnits_StartingValueList))
        ##########################################

        ##########################################
        self.PWM_DynamixelUnits_max = []
        if "PWM_DynamixelUnits_max" in setup_dict:
            temp_list = setup_dict["PWM_DynamixelUnits_max"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= 0 and item <= 885.0:
                        self.PWM_DynamixelUnits_max.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: PWM_DynamixelUnits_max values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: PWM_DynamixelUnits_max values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("PWM_DynamixelUnits_max was not valid.")
                return
        else:
            self.PWM_DynamixelUnits_max = [885.0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("PWM_DynamixelUnits_max valid: " + str(self.PWM_DynamixelUnits_max))
        ##########################################

        ##########################################
        self.PWM_DynamixelUnits_min = []
        if "PWM_DynamixelUnits_min" in setup_dict:
            temp_list = setup_dict["PWM_DynamixelUnits_min"]

            FailedFlag = 0
            for item in temp_list:
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= 0 and item <= 885.0:
                        self.PWM_DynamixelUnits_min.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: PWM_DynamixelUnits_min values must be integers between 0 and 4095.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: PWM_DynamixelUnits_min values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("PWM_DynamixelUnits_min was not valid.")
                return
        else:
            self.PWM_DynamixelUnits_min = [0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("PWM_DynamixelUnits_min valid: " + str(self.PWM_DynamixelUnits_min))
        ##########################################

        ##########################################
        ##########################################

        ##########################################
        self.MinPositionLimit_StartingValueList = []
        if "MinPositionLimit_StartingValueList" in setup_dict:
            temp_list = setup_dict["MinPositionLimit_StartingValueList"]

            FailedFlag = 0
            for item in temp_list:
                #print(item)
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= 0 and item <= 1023:
                        self.MinPositionLimit_StartingValueList.append(item)
                    else:
                        self.MyPrint_WithoutLogFile(
                            "ERROR: MinPositionLimit_StartingValueList values must be integers between 0 and 1023.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: MinPositionLimit_StartingValueList values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("MinPositionLimit_StartingValueList was not valid.")
                return

        else:
            self.MinPositionLimit_StartingValueList = [0] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("MinPositionLimit_StartingValueList valid: " + str(self.MinPositionLimit_StartingValueList))
        ##########################################

        ##########################################
        self.MaxPositionLimit_StartingValueList = []
        if "MaxPositionLimit_StartingValueList" in setup_dict:
            temp_list = setup_dict["MaxPositionLimit_StartingValueList"]

            FailedFlag = 0
            for item in temp_list:
                #print(item)
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item >= 0 and item <= 1023:
                        self.MaxPositionLimit_StartingValueList.append(item)
                    else:
                        self.MyPrint_WithoutLogFile(
                            "ERROR: MaxPositionLimit_StartingValueList values must be integers between 0 and 1023.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: MaxPositionLimit_StartingValueList values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("MaxPositionLimit_StartingValueList was not valid.")
                return

        else:
            self.MaxPositionLimit_StartingValueList = [1023] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("MaxPositionLimit_StartingValueList valid: " + str(self.MaxPositionLimit_StartingValueList))
        ##########################################

        ##########################################
        self.StartEngagedFlag = []
        if "StartEngagedFlag" in setup_dict:
            temp_list = setup_dict["StartEngagedFlag"]

            FailedFlag = 0
            for item in temp_list:
                #print(item)
                if self.IsArgumentAnumber(item) == 1:
                    item = int(item)
                    if item == 0 or item == 1:
                        self.StartEngagedFlag.append(item)
                    else:
                        self.MyPrint_WithoutLogFile("ERROR: StartEngagedFlag values must be integers between 0 and 1.")
                        FailedFlag = 1
                else:
                    self.MyPrint_WithoutLogFile("ERROR: StartEngagedFlag values must be numbers.")
                    FailedFlag = 1

            if FailedFlag == 1:
                self.MyPrint_WithoutLogFile("StartEngagedFlag was not valid.")
                return

        else:
            self.StartEngagedFlag = [1] * self.NumberOfMotors

        self.MyPrint_WithoutLogFile("StartEngagedFlag valid: " + str(self.StartEngagedFlag))
        ##########################################

        self.Position_DynamixelUnits = list(self.Position_DynamixelUnits_StartingValueList)
        self.Position_DynamixelUnits_TO_BE_SET = list(self.Position_DynamixelUnits_StartingValueList)

        self.Velocity_DynamixelUnits = list(self.Velocity_DynamixelUnits_StartingValueList)
        self.Velocity_DynamixelUnits_TO_BE_SET = list(self.Velocity_DynamixelUnits_StartingValueList)

        self.Current_DynamixelUnits = list(self.Current_DynamixelUnits_StartingValueList)
        self.Current_DynamixelUnits_TO_BE_SET = list(self.Current_DynamixelUnits_StartingValueList)

        self.PWM_DynamixelUnits = list(self.PWM_DynamixelUnits_StartingValueList)
        self.PWM_DynamixelUnits_TO_BE_SET = list(self.PWM_DynamixelUnits_StartingValueList)

        self.MinPositionLimit = list(self.MinPositionLimit_StartingValueList)
        self.MinPositionLimit_TO_BE_SET = list(self.MinPositionLimit_StartingValueList)

        self.MaxPositionLimit = list(self.MaxPositionLimit_StartingValueList)
        self.MaxPositionLimit_TO_BE_SET = list(self.MaxPositionLimit_StartingValueList)

        self.MostRecentDataDict = dict([("ControlType", self.ControlType),
                                        ("Current_DynamixelUnits_TO_BE_SET", self.Current_DynamixelUnits_TO_BE_SET),
                                        ("PWM_DynamixelUnits_TO_BE_SET", self.PWM_DynamixelUnits_TO_BE_SET),
                                        ("Position_DynamixelUnits_TO_BE_SET", self.Position_DynamixelUnits_TO_BE_SET),
                                        ("Velocity_DynamixelUnits_TO_BE_SET", self.Velocity_DynamixelUnits_TO_BE_SET),
                                        ("PositionReceived_DynamixelUnits", self.PositionReceived_DynamixelUnits),
                                        ("PositionReceived_Deg", self.PositionReceived_Deg),
                                        ("VelocityReceived_DynamixelUnits", self.VelocityReceived_DynamixelUnits),
                                        ("TorqueReceived_DynamixelUnits", self.TorqueReceived_DynamixelUnits),
                                        ("VoltageReceived_DynamixelUnits", self.VoltageReceived_DynamixelUnits),
                                        ("TemperatureReceived_DynamixelUnits", self.TemperatureReceived_DynamixelUnits),
                                        ("Time", self.getPreciseSecondsTimeStampString()),
                                        ("DataStreamingFrequency_CalculatedFromMainThread", self.DataStreamingFrequency_CalculatedFromMainThread)])

        #########################################################
        #########################################################
        if _platform == "Windows":
            self.SetAllFTDIdevicesLatencyTimer(1)
            
        self.find_and_assign_serial_port()

        self.portHandler = PortHandler(self.serial_name)
        self.packetHandler = PacketHandler(2.0)

        if self.portHandler.openPort():
            print("Succeeded to open the port")
            self.serial_connected_flag = 1
        else:
            print("Failed to open the port")
            self.serial_connected_flag = 0

        if self.portHandler.setBaudRate(self.SerialBaudRate):
            print("Succeeded to change the baudrate")
            self.serial_connected_flag = 1
        else:
            print("Failed to change the baudrate")
            self.serial_connected_flag = 0

        if self.serial_connected_flag == 1:

            ##########################################
            self.MainThread_ThreadingObject = threading.Thread(target=self.MainThread, args=())
            self.MainThread_ThreadingObject.start()
            ##########################################

            ##########################################
            if self.USE_GUI_FLAG == 1:
                self.StartGUI(self.root)
            ##########################################

            ##########################################
            self.OBJECT_CREATED_SUCCESSFULLY_FLAG = 1
            ##########################################

        else:
            self.MyPrint_WithoutLogFile("Device not connected, cannot start data collection thread.")
            self.OBJECT_CREATED_SUCCESSFULLY_FLAG = 0
            return
    #######################################################################################################################

    #######################################################################################################################
    def __del__(self):
        dummy_var = 0
    #######################################################################################################################


    #######################################################################################################################
    def PassThrough0and1values_ExitProgramOtherwise(self, InputNameString, InputNumber):

        try:
            InputNumber_ConvertedToFloat = float(InputNumber)
        except:
            exceptions = sys.exc_info()[0]
            print("PassThrough0and1values_ExitProgramOtherwise Error. InputNumber must be a float value, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()

        try:
            if InputNumber_ConvertedToFloat == 0.0 or InputNumber_ConvertedToFloat == 1:
                return InputNumber_ConvertedToFloat
            else:
                input("PassThrough0and1values_ExitProgramOtherwise Error. '" +
                          InputNameString +
                          "' must be 0 or 1 (value was " +
                          str(InputNumber_ConvertedToFloat) +
                          "). Press any key (and enter) to exit.")

                sys.exit()
        except:
            exceptions = sys.exc_info()[0]
            print("PassThrough0and1values_ExitProgramOtherwise Error, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()
    #######################################################################################################################

    #######################################################################################################################
    def PassThroughFloatValuesInRange_ExitProgramOtherwise(self, InputNameString, InputNumber, RangeMinValue, RangeMaxValue):
        try:
            InputNumber_ConvertedToFloat = float(InputNumber)
        except:
            exceptions = sys.exc_info()[0]
            print("PassThroughFloatValuesInRange_ExitProgramOtherwise Error. InputNumber must be a float value, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()

        try:
            if InputNumber_ConvertedToFloat >= RangeMinValue and InputNumber_ConvertedToFloat <= RangeMaxValue:
                return InputNumber_ConvertedToFloat
            else:
                input("PassThroughFloatValuesInRange_ExitProgramOtherwise Error. '" +
                          InputNameString +
                          "' must be in the range [" +
                          str(RangeMinValue) +
                          ", " +
                          str(RangeMaxValue) +
                          "] (value was " +
                          str(InputNumber_ConvertedToFloat) + "). Press any key (and enter) to exit.")

                sys.exit()
        except:
            exceptions = sys.exc_info()[0]
            print("PassThroughFloatValuesInRange_ExitProgramOtherwise Error, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()
    #######################################################################################################################

    #######################################################################################################################
    def ComputeTwosComplement(self, IntegerToBeConverted, NumberOfBitsInInteger=16):
        return IntegerToBeConverted & ((2 ** NumberOfBitsInInteger) - 1)
    #######################################################################################################################

    #######################################################################################################################
    def SetAllFTDIdevicesLatencyTimer(self, LatencyTimerToSet = 1):
        FTDI_device_list = ftd2xx.listDevices()
        self.MyPrint_WithoutLogFile("FTDI_device_list: " + str(FTDI_device_list))
        if FTDI_device_list != None:
            index = 0
            for index in range(0, len(FTDI_device_list)):

                    FTDI_serial_number = FTDI_device_list[index]
                    self.MyPrint_WithoutLogFile("FTDI device serial number: " + FTDI_serial_number)
                    try:
                        FTDI_object = ftd2xx.open(index)
                        FTDI_device_info = FTDI_object.getDeviceInfo()
                        self.MyPrint_WithoutLogFile("FTDI_device_info: " + str(FTDI_device_info))
                        FTDI_object.setLatencyTimer(LatencyTimerToSet)
                        time.sleep(0.005)
                        FTDI_object_read_value = FTDI_object.getLatencyTimer()
                        self.MyPrint_WithoutLogFile("FTDI_object.getLatencyTimer() returned: " + str(FTDI_object_read_value))
                        FTDI_object.close()
                    except:
                        self.MyPrint_WithoutLogFile("Could not open FTDI device with serial number " + FTDI_serial_number)
        else:
            self.MyPrint_WithoutLogFile("SetAllFTDIdevicesLatencyTimer ERROR: FTDI_device_list is empty, cannot proceed.")
    #######################################################################################################################

    #######################################################################################################################
    def find_and_assign_serial_port(self):

        ###############################################################
        my_platform = str("default")
        if _platform == "linux" or _platform == "linux2":
            my_platform = "linux"
        elif _platform == "win32":
            my_platform = "windows"
        else:
            my_platform = "other"
        self.MyPrint_WithoutLogFile("The OS platform is: " + my_platform)
        ###############################################################

        ###############################################################


        self.MyPrint_WithoutLogFile("Finding all serial ports...")

        serial_ports_available = serial.tools.list_ports.comports()

        name = []
        description = []
        VID_PID_SERIAL_info = []
        serial_name_temp = str("default")
        serial_found_flag = 0
        self.serial_name = "-1"

        for x in serial_ports_available: #serial_ports_available IS A GENERATOR
            port = x
            self.MyPrint_WithoutLogFile(port)
            name.append(port[0])
            description.append(port[1])
            VID_PID_SERIAL_info.append(port[2])

            for i in range(0, 1):
                serial_number_to_check_against = self.SerialNumber
                if my_platform == "linux":
                    serial_number_to_check_against = serial_number_to_check_against[:-1] #The serial number gets truncated by one digit in linux
                else:
                    serial_number_to_check_against = serial_number_to_check_against

                if port[2].find(serial_number_to_check_against) != -1 and serial_found_flag == 0: #The VID and PID are identical for some of the SSI units and the Juicer serial cables, so we must use the serial numbers
                    serial_name_temp = port[0]
                    serial_number = serial_number_to_check_against
                    self.MyPrint_WithoutLogFile("Found serial port with serial number " + serial_number + " on port " + serial_name_temp)
                    serial_found_flag = 1 #to ensure that we only get one SSI serial device

        ###########################################################################
        if(serial_name_temp != "default"): #Means that it's physically plugged in.
                try: #Will succeed as long as another program hasn't already opened the serial line.
                    self.serial_connected_flag = 1
                    self.serial_name = serial_name_temp
                    self.serialObject = serial.Serial(self.serial_name, self.SerialBaudRate, timeout=0.5)
                    self.MyPrint_WithoutLogFile("Serial is connected and open on " + str(self.serial_name))
                    self.serialObject.close()


                except:
                    self.serial_connected_flag = 0
                    self.MyPrint_WithoutLogFile("ERROR: Serial is physically plugged in but IS IN USE BY ANOTHER PROGRAM (CHECK PUTTY).")
                    time.sleep(5)
        else:
            self.serial_connected_flag = -1
            self.MyPrint_WithoutLogFile("ERROR: Could not find the serial device. IS IT PHYSICALLY PLUGGED IN?")
            time.sleep(5)
        ###########################################################################

        return self.serial_connected_flag
    #######################################################################################################################

    #######################################################################################################################
    def SerialReadSingleByteWithTimeout(self, silenceFlag=0, timeout=-1):

        entry_time = self.getPreciseSecondsTimeStampString()

        line = ''
        while (1):

            try:
                c = ""
                c = self.serialObject.read(1)  # Read a single character

                if c != "":  # IF WE GOT A REAL CHARACTER, RETURN IMMEDIATELY.
                    line = line + c
                    break

            except:
                exceptions = sys.exc_info()[0]
                self.MyPrint_WithoutLogFile("SerialReadLineWithTimeout ERROR: Exceptions: %s" % exceptions)

            if timeout != -1:  # IF THERE IS A TIMEOUT THAT'S SPECIFIED BY THE CALLING FUNCTION
                if self.getPreciseSecondsTimeStampString() - entry_time < timeout:
                    dummy = 0
                else:
                    if silenceFlag == 0:
                        self.MyPrint_WithoutLogFile(
                            "SerialReadSingleByteWithTimeout ERROR: Timed out after " + str(timeout) + " seconds.")
                    break
            else:  # NO TIMEOUT
                break

        if silenceFlag == 0:
            self.MyPrint_WithoutLogFile(line)
        return line
    #######################################################################################################################

    #######################################################################################################################
    def close_serial_port(self):

        if self.serial_connected_flag == 1:
            self.MyPrint_WithoutLogFile("Closed serial connection.")
            self.serialObject.close()
    #######################################################################################################################

    #######################################################################################################################
    def IsArgumentAnumber(self, Input):

        try:
            FloatNumber = float(self.only_numerics(str(Input))) #only_numerics needs the str of the number for it to convert properly
        except:
            return 0

        return 1
    #######################################################################################################################

    #######################################################################################################################
    def IsInputList(self, input, print_result_flag = 0):

        result = isinstance(input, list)

        if print_result_flag == 1:
            self.MyPrint_WithoutLogFile("IsInputList: " + str(result))

        return result
    #######################################################################################################################

    #######################################################################################################################
    def IsListAllNumbers(self, InputList):

        for item in InputList:
            try:
                FloatNumber = float(self.only_numerics(str(item))) #only_numerics needs the str of the number for it to convert properly
            except:
                return 0

        return 1
    #######################################################################################################################

    ########################################################################################################################
    def only_numerics(self, seq):
        seq_numbers_only = ""

        try:
            MinusSignFlag = 0
            for x in range(0, len(seq)):
                if seq[x] == "-":
                    MinusSignFlag = 1
                elif seq[x].isdigit() or seq[x] == ".":
                    seq_numbers_only = seq_numbers_only + seq[x]

            if seq_numbers_only == "0":
                return seq_numbers_only

            seq_numbers_only = seq_numbers_only.lstrip('0')  # Remove leading zeros

            if seq_numbers_only == ".":  # If we lstrip'ed down to just a decimal point
                seq_numbers_only = "0.0"

            if len(seq_numbers_only) > 0:
                if seq_numbers_only[0] == ".":
                    seq_numbers_only = "0" + seq_numbers_only

            if MinusSignFlag == 1:
                seq_numbers_only = "-" + seq_numbers_only

            if seq_numbers_only[-1] == ".":
                seq_numbers_only = seq_numbers_only[:-1]

                # MyPrint_WithoutLogFile("only_numerics: converted " + str(seq) + " to " + seq_numbers_only)
        except:
            exceptions = sys.exc_info()[0]
            self.MyPrint_WithoutLogFile("only_numerics Error, Exceptions: %s" % exceptions)
            return ""

        return seq_numbers_only
    ########################################################################################################################

    #######################################################################################################################
    def TellWhichFileWereIn(self):

        #We used to use this method, but it gave us the root calling file, not the class calling file
        #absolute_file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        #filename = absolute_file_path[absolute_file_path.rfind("\\") + 1:]

        frame = inspect.stack()[1]
        filename = frame[1][frame[1].rfind("\\") + 1:]
        filename = filename.replace(".py","")

        return filename
    #######################################################################################################################

    #######################################################################################################################
    def SetPrintToConsoleFlag(self, value):
        if value == 0 or value == 1:
            self.printToConsoleFlag = value
        else:
            self.MyPrint_WithoutLogFile("SetPrintToConsoleFlag ERROR: This function accepts only 0 or 1.")
    #######################################################################################################################

    #######################################################################################################################
    def getTimeStampString(self):

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('date-%m-%d-%Y---time-%H-%M-%S')

        return st
    #######################################################################################################################

    #######################################################################################################################
    def getPreciseSecondsTimeStampString(self):
        ts = time.time()

        return ts
    #######################################################################################################################

    #######################################################################################################################
    def GetMostRecentDataDict(self):

        return self.MostRecentDataDict
    #######################################################################################################################

    ##########################################################################################################
    ########################################################################################################## dragon
    def SetControlType_FROM_EXTERNAL_PROGRAM(self, MotorIndex, ControlTypeStringExternalProgram):

        if ControlTypeStringExternalProgram not in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.control_type_acceptable_list:
            self.MyPrint_WithoutLogFile("SetControlType_FROM_EXTERNAL_PROGRAM ERROR: ControlTypeStringExternalProgram must be in " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.control_type_acceptable_list))
            return 0

        self.MyPrint_WithoutLogFile("SetControlType_FROM_EXTERNAL_PROGRAM changing ControlType on motor " + str(MotorIndex) + " to a value of " + str(ControlTypeStringExternalProgram))

        self.ControlType_TO_BE_SET[MotorIndex] = ControlTypeStringExternalProgram
        self.ControlType_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] = 1
        self.ControlType_GUI_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] = 1

        return 1
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SetCurrent_FROM_EXTERNAL_PROGRAM(self, MotorIndex, CurrentFromExternalProgram, Units = "None", NumberOfTimesToIssueCommand = 1):
        Units = Units.lower()

        #self.MyPrint_WithoutLogFile("CurrentFromExternalProgram: " + str(CurrentFromExternalProgram))

        if Units not in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.current_units_acceptable_list:
            self.MyPrint_WithoutLogFile("SetCurrent_FROM_EXTERNAL_PROGRAM ERROR: units of " + Units + " is not in the acceptable list of " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_units_acceptable_list))
            return 0

        if NumberOfTimesToIssueCommand < 1:
            self.MyPrint_WithoutLogFile("SetCurrent_FROM_EXTERNAL_PROGRAM ERROR: must set NumberOfTimesToIssueCommand >= 1")
            return 0

        CurrentFromExternalProgram_ConvertedToDynamixelUnits_unlimited = 0
        CurrentFromExternalProgram_ConvertedToDynamixelUnits_limited = 0

        CurrentFromExternalProgram_ConvertedToDynamixelUnits_unlimited = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllCurrentUnits(CurrentFromExternalProgram, Units)["dynamixelunits"]
        CurrentFromExternalProgram_ConvertedToDynamixelUnits_limited = self.limitNumber(self.Current_DynamixelUnits_min[MotorIndex], self.Current_DynamixelUnits_max[MotorIndex], CurrentFromExternalProgram_ConvertedToDynamixelUnits_unlimited)

        self.Current_DynamixelUnits_TO_BE_SET[MotorIndex] = CurrentFromExternalProgram_ConvertedToDynamixelUnits_limited
        self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = NumberOfTimesToIssueCommand
        self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1

        return 1
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SetPosition_FROM_EXTERNAL_PROGRAM(self, MotorIndex, PositionFromExternalProgram, Units = "None"):
        Units = Units.lower()

        if Units not in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_units_acceptable_list:
            self.MyPrint_WithoutLogFile("SetPosition_FROM_EXTERNAL_PROGRAM ERROR: units of " + Units + " is not in the acceptable list of " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_units_acceptable_list))
            return 0

        PositionFromExternalProgram_ConvertedToDynamixelUnits_unlimited = 0
        PositionFromExternalProgram_ConvertedToDynamixelUnits_limited = 0

        PositionFromExternalProgram_ConvertedToDynamixelUnits_unlimited = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(PositionFromExternalProgram, Units)["dynamixelunits"]
        PositionFromExternalProgram_ConvertedToDynamixelUnits_limited = self.limitNumber(self.Position_DynamixelUnits_min[MotorIndex], self.Position_DynamixelUnits_max[MotorIndex], PositionFromExternalProgram_ConvertedToDynamixelUnits_unlimited)

        self.Position_DynamixelUnits_TO_BE_SET[MotorIndex] = PositionFromExternalProgram_ConvertedToDynamixelUnits_limited
        self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
        self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1

        return 1
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SetVelocity_FROM_EXTERNAL_PROGRAM(self, MotorIndex, VelocityFromExternalProgram, Units = "None"):
        Units = Units.upper()

        '''
        if Units not in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_speed_units_acceptable_list:
            self.MyPrint_WithoutLogFile("SetVelocity_FROM_EXTERNAL_PROGRAM ERROR: units of " + Units + " is not in the acceptable list of " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_speed_units_acceptable_list))
            return 0

        VelocityFromExternalProgram_unlimited = 0
        if Units == "NONE":
            VelocityFromExternalProgram_unlimited = VelocityFromExternalProgram

        if Units == "PERCENT":
            VelocityFromExternalProgram = self.limitNumber(0.0, 100.0, VelocityFromExternalProgram) #To limit the input to [0,100]%
            VelocityFromExternalProgram_unlimited = ((self.Velocity_DynamixelUnits_max[MotorIndex] - self.Velocity_DynamixelUnits_min[MotorIndex])/100.0)*VelocityFromExternalProgram + self.Velocity_DynamixelUnits_min[MotorIndex]

        self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex] = self.limitNumber(self.Velocity_DynamixelUnits_min[MotorIndex], self.Velocity_DynamixelUnits_max[MotorIndex], VelocityFromExternalProgram_unlimited)
        self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
        self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1

        return 1
        '''
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SetEngagedState_FROM_EXTERNAL_PROGRAM(self, MotorIndex, EngagedStateExternalProgram):

        if EngagedStateExternalProgram != 0 and EngagedStateExternalProgram != 1:
            self.MyPrint_WithoutLogFile("SetEngagedState_FROM_EXTERNAL_PROGRAM ERROR: EngagedState must be 0 or 1.")
            return 0

        #self.MyPrint_WithoutLogFile("SetEngagedState_FROM_EXTERNAL_PROGRAM changing EngagedState on motor " + str(MotorIndex) + " to a value of " + str(EngagedStateExternalProgram))

        self.EngagedState_TO_BE_SET[MotorIndex] = EngagedStateExternalProgram
        self.EngagedState_NeedsToBeChangedFlag[MotorIndex] = 1
        self.EngagedState_GUI_NeedsToBeChangedFlag[MotorIndex] = 1

        return 1
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ToggleLEDstate_FROM_EXTERNAL_PROGRAM(self, MotorIndex):

        #self.MyPrint_WithoutLogFile("SetLEDstate_FROM_EXTERNAL_PROGRAM changing LEDstate on motor " + str(MotorIndex) + " to a value of " + str(LEDstateExternalProgram))

        if self.LEDstate[MotorIndex] == 0:
            self.SetLEDstate_FROM_EXTERNAL_PROGRAM(MotorIndex, 1)
        else:
            self.SetLEDstate_FROM_EXTERNAL_PROGRAM(MotorIndex, 0)


        return 1
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SetLEDstate_FROM_EXTERNAL_PROGRAM(self, MotorIndex, LEDstateExternalProgram):

        if LEDstateExternalProgram != 0 and LEDstateExternalProgram != 1:
            self.MyPrint_WithoutLogFile("SetLEDstate_FROM_EXTERNAL_PROGRAM ERROR: LEDstate must be 0 or 1.")
            return 0

        #self.MyPrint_WithoutLogFile("SetLEDstate_FROM_EXTERNAL_PROGRAM changing LEDstate on motor " + str(MotorIndex) + " to a value of " + str(LEDstateExternalProgram))

        self.LEDstate_TO_BE_SET[MotorIndex] = LEDstateExternalProgram
        self.LEDstate_NeedsToBeChangedFlag[MotorIndex] = 1
        self.LEDstate_GUI_NeedsToBeChangedFlag[MotorIndex] = 1

        return 1
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def UpdateFrequencyCalculation_CalculatedFromMainThread(self):

        try:

            self.DataStreamingDeltaT_CalculatedFromMainThread = self.CurrentTime_CalculatedFromMainThread - self.LastTime_CalculatedFromMainThread

            ##########################
            if self.DataStreamingDeltaT_CalculatedFromMainThread != 0.0:
                self.DataStreamingFrequency_CalculatedFromMainThread = 1.0/self.DataStreamingDeltaT_CalculatedFromMainThread
            ##########################

            self.LastTime_CalculatedFromMainThread = self.CurrentTime_CalculatedFromMainThread

            self.LoopCounter_CalculatedFromMainThread = self.LoopCounter_CalculatedFromMainThread + 1

        except:
            exceptions = sys.exc_info()[0]
            self.MyPrint_WithoutLogFile("UpdateFrequencyCalculation_CalculatedFromMainThread ERROR, exceptions: %s" % exceptions)
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def UpdateFrequencyCalculation_RealTimeTicksMillisecFromDynamixel(self, MotorIndex):

        try:
            self.DataStreamingDeltaT_RealTimeTicksMillisecFromDynamixel[MotorIndex] = (self.RealTimeTicksMillisec[MotorIndex] - self.RealTimeTicksMillisec_last[MotorIndex])*0.001

            ##########################
            if self.DataStreamingDeltaT_RealTimeTicksMillisecFromDynamixel[MotorIndex] != 0.0:
                self.DataStreamingFrequency_RealTimeTicksMillisecFromDynamixel[MotorIndex] = 1.0/self.DataStreamingDeltaT_RealTimeTicksMillisecFromDynamixel[MotorIndex]
            ##########################

            self.RealTimeTicksMillisec_last[MotorIndex] = self.RealTimeTicksMillisec[MotorIndex]

        except:
            exceptions = sys.exc_info()[0]
            self.MyPrint_WithoutLogFile("UpdateFrequencyCalculation_RealTimeTicksMillisecDynamixel ERROR, exceptions: %s" % exceptions)
            #traceback.print_exc()
    ##########################################################################################################
    ##########################################################################################################

    #######################################################################################################################
    def ConvertOperatingModeStringToInt(self, OperatingModeString):

        if OperatingModeString == "CurrentControl":
            OperatingModeInt = 0
        elif OperatingModeString == "VelocityControl":
            OperatingModeInt = 1
        elif OperatingModeString == "PositionControl":
            OperatingModeInt = 3
        elif OperatingModeString == "ExtendedPositionControlMultiTurn":
            OperatingModeInt = 4
        elif OperatingModeString == "CurrentBasedPositionControl":
            OperatingModeInt = 5
        elif OperatingModeString == "PWMcontrol":
            OperatingModeInt = 16
        else:
            OperatingModeInt = -1
            #self.MyPrint_WithoutLogFile("ConvertOperatingModeStringToInt ERROR: OperatingModeString '" + OperatingModeString + "' is invalid.")

        return OperatingModeInt
    #######################################################################################################################

    #######################################################################################################################
    def ConvertOperatingModeIntToString(self, OperatingModeInt):

        if OperatingModeInt == 0:
            OperatingModeString = "CurrentControl"
        elif OperatingModeInt == 1:
            OperatingModeString = "VelocityControl"
        elif OperatingModeInt == 3:
            OperatingModeString = "PositionControl"
        elif OperatingModeInt == 4:
            OperatingModeString = "ExtendedPositionControlMultiTurn"
        elif OperatingModeInt == 5:
            OperatingModeString = "CurrentBasedPositionControl"
        elif OperatingModeInt == 16:
            OperatingModeString = "PWMcontrol"
        else:
            OperatingModeString = "invalid"
            #self.MyPrint_WithoutLogFile("ConvertOperatingModeIntToString ERROR: OperatingModeInt '" + str(OperatingModeInt) + "' is invalid.")

        return OperatingModeString
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetOperatingMode(self, MotorID, OperatingModeString, print_bytes_for_debugging = 0):

        ############################################################
        ############################################################ FOR SOME REASON, SendInstructionPacket_SetOperatingMode ONLY WORKS IF WE FIRST REBOOT THE MOTOR
        self.SendInstructionPacket_Reboot(MotorID)
        time.sleep(0.10) #Have to wait a long time after the REBOOT for this to work
        ############################################################
        ############################################################

        OperatingModeInt = self.ConvertOperatingModeStringToInt(OperatingModeString)

        print("OperatingModeString: " + OperatingModeString)
        print("OperatingModeInt: " + str(OperatingModeInt))

        ADDR_PRO_OPERATINGMODE = 11

        dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_OPERATINGMODE, OperatingModeInt)
        if dxl_comm_result != COMM_SUCCESS:
            self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
            self.ControlType[MotorID] = OperatingModeString
            self.MyPrint_WithoutLogFile("@@@@@@@@@@@@@@@@@@@@ SendInstructionPacket_SetOperatingMode set operating mode to " + self.ControlType[MotorID] + " on motor " + str(MotorID) + " @@@@@@@@@@@@@@@@@@@@")

            if OperatingModeString == "CurrentControl":
                self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1
            elif OperatingModeString == "VelocityControl":
                self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1
            elif OperatingModeString == "PositionControl":
                self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1
            elif OperatingModeString == "ExtendedPositionControlMultiTurn":
                self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1
            elif OperatingModeString == "CurrentBasedPositionControl":
                self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1
                self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1
            elif OperatingModeString == "PWMcontrol":
                self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorID] = 1

            self.EngagedState_TO_BE_SET[MotorID] = 1  # From page 9 of motor manual: "After setting the operating mode (11) to speed control mode, change the Torque Enable (64) to '1'."
            self.EngagedState_NeedsToBeChangedFlag[MotorID] = 1

        return 1
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetLED(self, MotorID, LEDstate, print_bytes_for_debugging = 0):

        ADDR_PRO_LED = 65

        dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_LED, LEDstate)
        if dxl_comm_result != COMM_SUCCESS:
            self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        self.LEDstate[MotorID] = LEDstate
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetLEDalarmSettings(self, MotorID, LEDalarmSettingsByte, print_bytes_for_debugging = 0):
        dummy = 0

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetID(self, MotorID, IDToSet, print_bytes_for_debugging = 0):

        ############################################
        ############################################
        #In order to change the ID in the EEPROM Area, Torque Enable(64) has to be cleared to "0" in advance.
        EngagedState_temp = self.EngagedState[MotorID]
        self.SendInstructionPacket_SetTorqueEnable(MotorID, 0) #In order to change the ID in the EEPROM Area, Torque Enable(64) has to be cleared to "0" in advance.
        time.sleep(0.002)
        ############################################
        ############################################

        ADDR_PRO_ID = 7

        dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_ID, IDToSet)
        if dxl_comm_result != COMM_SUCCESS:
            self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
        time.sleep(0.002)

        ############################################
        ############################################
        self.SendInstructionPacket_SetTorqueEnable(MotorID, EngagedState_temp)
        time.sleep(0.002)
        ############################################
        ############################################

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetBaudRate(self, MotorID, BaudRateToSet, print_bytes_for_debugging = 0):

        ADDR_PRO_BAUD_RATE = 8

        dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_BAUD_RATE, 6)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetTorqueEnable(self, MotorID, TorqueEnableState, print_bytes_for_debugging = 0):

        ADDR_PRO_TORQUE_ENABLE = 64

        dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_TORQUE_ENABLE, TorqueEnableState)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
            self.EngagedState[MotorID] = TorqueEnableState

        #self.MyPrint_WithoutLogFile("SendInstructionPacket_SetTorqueEnable fired!")
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def ResetSerial(self, print_bytes_for_debugging = 0):

        self.portHandler.clearPort()
        self.portHandler.closePort()
        time.sleep(0.025)
        self.portHandler.openPort()

        for MotorIndex in range(0, self.NumberOfMotors):
            self.SendInstructionPacket_SetStatusReturnLevel(MotorIndex, 1)  # 0: Do not respond to any instructions, 1: Respond only to READ_DATA instructions, 2: Respond to all instructions
            time.sleep(self.TimeToWaitBetweenCriticalInstructions)

        self.MyPrint_WithoutLogFile("########## ResetSerial! ##########")
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_Reboot(self, MotorID, print_bytes_for_debugging = 0):

        dxl_comm_result = self.packetHandler.reboot(self.portHandler, MotorID)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        self.MyPrint_WithoutLogFile("REBOOTED MOTOR " + str(MotorID))
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_ReturnDelayTime(self, MotorID, ReturnDelayTime, print_bytes_for_debugging = 0):

        ReturnDelayTime_limited = int(self.limitNumber(0, 254, ReturnDelayTime))

        ADDR_PRO_RETURN_DELAY_TIME = 9

        dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_RETURN_DELAY_TIME, ReturnDelayTime_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetStatusReturnLevel(self, MotorID, StatusReturnLevel, print_bytes_for_debugging = 0):

        # 0: Do not respond to any instructions
        # 1: Respond only to READ_DATA instructions
        # 2: Respond to all instructions

        if StatusReturnLevel == 0 or StatusReturnLevel == 1 or StatusReturnLevel == 2:

            ADDR_PRO_STATUS_RETURN_LEVEL = 68

            dxl_comm_result = self.packetHandler.write1ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_STATUS_RETURN_LEVEL, int(StatusReturnLevel))
            if dxl_comm_result != COMM_SUCCESS:
                dummy_var = 0
                #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            else:
                dummy = 0
        else:
            self.MyPrint_WithoutLogFile("SendInstructionPacket_SetStatusReturnLevel ERROR: StatusReturnLevel must be 0, 1, or 2.")
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetPosition(self, MotorID, Position, print_bytes_for_debugging = 0):

        ADDR_PRO_GOAL_POSITION = 116

        Position_limited = int(self.limitNumber(self.Position_DynamixelUnits_min[MotorID], self.Position_DynamixelUnits_max[MotorID], Position))

        #if Position_limited < 0:
        #    Position_limited = self.ComputeTwosComplement(Position_limited) #NOT NEEDED

        dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_GOAL_POSITION, Position_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        self.Position_DynamixelUnits[MotorID] = Position_limited
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetGoalCurrent_ForCurrentAndCurrentBasedPositionControl(self, MotorID, Current, print_bytes_for_debugging = 0):

        ADDR_PRO_GOAL_Current = 102

        Current_limited = int(self.limitNumber(-2047.0, 2047.0, Current))

        if Current_limited < 0:
            Current_limited_TwosComplement = self.ComputeTwosComplement(Current_limited, 16) #2 bytes = 16bits
            dxl_comm_result = self.packetHandler.write2ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_GOAL_Current, Current_limited_TwosComplement)
        else:
            dxl_comm_result = self.packetHandler.write2ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_GOAL_Current, Current_limited)

        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
            self.Current_DynamixelUnits[MotorID] = Current_limited
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetCurrentLimit(self, MotorID, CurrentLimit, print_bytes_for_debugging = 0):

        ########### IT SEEMS LIKE THIS FUNCTION LIKES TO DECREASE THE CURRENT LIMIT BUT NEVER INCREASE IT

        ####################################################
        EngagedState_temp = self.EngagedState[MotorID]
        self.SendInstructionPacket_SetTorqueEnable(MotorID, 0) #DYNAMIXEL LIMITS CAN ONLY BE CHANGED WITH TORQUE DISABLED
        ####################################################

        ####################################################
        CurrentLimit_limited = int(self.limitNumber(0.0, 2047.0, CurrentLimit))

        ADDR_PRO_CURRENT_LIMIT = 38

        dxl_comm_result = self.packetHandler.write2ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_CURRENT_LIMIT, CurrentLimit_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        #self.Current_DynamixelUnits_max[MotorID] = CurrentLimit_limited
        ####################################################

        ####################################################
        self.SendInstructionPacket_SetTorqueEnable(MotorID, EngagedState_temp) #Must set the EngagedState back to what it was before we changed this limit
        ####################################################

        #self.MyPrint_WithoutLogFile("SendInstructionPacket_SetCurrentLimit EVENT FIRED!")
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetGoalVelocity_ForVelocityModeOnly(self, MotorID, Velocity, print_bytes_for_debugging = 0):

        ADDR_PRO_GOAL_VELOCITY = 104

        Velocity_limited = int(self.limitNumber(-1023.0, 1023.0, Velocity))

        if Velocity_limited < 0:
            Velocity_limited_TwosComplement = self.ComputeTwosComplement(Velocity_limited, 32) #4 bytes = 32bits
            #print("negative: " + str('{0:016b}'.format(Velocity_limited_TwosComplement)))

            dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_GOAL_VELOCITY, Velocity_limited_TwosComplement)
        else:
            #print('{0:016b}'.format(Velocity_limited))
            dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_GOAL_VELOCITY, Velocity_limited)

        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
            #self.MyPrint_WithoutLogFile("SendInstructionPacket_SetGoalVelocity_ForVelocityModeOnly fired!")
            self.Velocity_DynamixelUnits[MotorID] = Velocity_limited
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetMinPositionLimit_PositionModeOnly(self, MotorID, MinPositionLimit, print_bytes_for_debugging = 0):

        # $$$$$$$$$$$$$ These values are not used in Extended Position Control Mode and Current-based Position Control Mode.
        if self.ControlType == "PositionControl":
            ####################################################
            EngagedState_temp = self.EngagedState[MotorID]
            self.SendInstructionPacket_SetTorqueEnable(MotorID, 0) #DYNAMIXEL LIMITS CAN ONLY BE CHANGED WITH TORQUE DISABLED
            ####################################################

            ####################################################
            MinPositionLimit_limited = int(self.limitNumber(0.0, 4095.0, MinPositionLimit))

            ADDR_PRO_MIN_POSITION_LIMIT = 52

            dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_MIN_POSITION_LIMIT, MinPositionLimit_limited)
            if dxl_comm_result != COMM_SUCCESS:
                dummy_var = 0
                #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            else:
                dummy = 0
            ####################################################

            ####################################################
            self.SendInstructionPacket_SetTorqueEnable(MotorID, EngagedState_temp) #Must set the EngagedState back to what it was before we changed this limit
            ####################################################

        else:
            self.MyPrint_WithoutLogFile("SendInstructionPacket_SetMinPositionLimit_PositionModeOnly ERROR, function can only be called in 'PositionMode' (single-turn).")
        
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetMaxPositionLimit_PositionModeOnly(self, MotorID, MaxPositionLimit, print_bytes_for_debugging=0):

        #$$$$$$$$$$$$$ These values are not used in Extended Position Control Mode and Current-based Position Control Mode.
        if self.ControlType == "PositionControl":
            ####################################################
            EngagedState_temp = self.EngagedState[MotorID]
            self.SendInstructionPacket_SetTorqueEnable(MotorID, 0)  # DYNAMIXEL LIMITS CAN ONLY BE CHANGED WITH TORQUE DISABLED
            ####################################################

            ####################################################
            MaxPositionLimit_limited = int(self.limitNumber(0.0, 4095.0, MaxPositionLimit))

            ADDR_PRO_Max_POSITION_LIMIT = 48

            dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_Max_POSITION_LIMIT, MaxPositionLimit_limited)
            if dxl_comm_result != COMM_SUCCESS:
                dummy_var = 0
                #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            else:
                dummy = 0
            ####################################################

            ####################################################
            self.SendInstructionPacket_SetTorqueEnable(MotorID, EngagedState_temp)  # Must set the EngagedState back to what it was before we changed this limit
            ####################################################

        else:
            self.MyPrint_WithoutLogFile("SendInstructionPacket_SetMinPositionLimit_PositionModeOnly ERROR, function can only be called in 'PositionMode' (single-turn).")

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetMaxVelocity(self, MotorID, MaxVelocity, print_bytes_for_debugging = 0):
        ####################################################
        EngagedState_temp = self.EngagedState[MotorID]
        self.SendInstructionPacket_SetTorqueEnable(MotorID, 0) #DYNAMIXEL LIMITS CAN ONLY BE CHANGED WITH TORQUE DISABLED
        ####################################################

        ####################################################
        Velocity_DynamixelUnits_max_limited = int(self.limitNumber(0.0, 1023.0, MaxVelocity))

        ADDR_PRO_MAX_VELOCITY_LIMIT = 44

        dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_MAX_VELOCITY_LIMIT, Velocity_DynamixelUnits_max_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("SendInstructionPacket_SetMaxVelocity %s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        self.Velocity_DynamixelUnits_max[MotorID] = Velocity_DynamixelUnits_max_limited
        ####################################################

        ####################################################
        self.SendInstructionPacket_SetTorqueEnable(MotorID, EngagedState_temp) #Must set the EngagedState back to what it was before we changed this limit
        ####################################################
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetProfileVelocity_ForAllModesExceptCurrentAndVelocity(self, MotorID, ProfileVelocity, print_bytes_for_debugging = 0):
        '''
        Described on page 9 of motor manual
        The Maximum velocity of Profile can be set with this value.
        Profile Velocity(112) can be used in all control modes except Torque Control Mode and Velocity Control Mode.
        Profile Velocity(112) cannot exceed Velocity Limit(44).
        Velocity Control Mode only uses Profile Acceleration(108) instead of Profile Velocity(112).
        '''

        ProfileVelocity_limited = int(self.limitNumber(0.0, 1023.0, ProfileVelocity))

        ADDR_PRO_PROFILE_VELOCITY_LIMIT = 112

        dxl_comm_result = self.packetHandler.write4ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_PROFILE_VELOCITY_LIMIT, ProfileVelocity_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("SendInstructionPacket_SetProfileVelocity_ForAllModesExceptCurrentAndVelocity %s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetMaxPWM(self, MotorID, MaxPWM, print_bytes_for_debugging = 0):
        ####################################################
        EngagedState_temp = self.EngagedState[MotorID]
        self.SendInstructionPacket_SetTorqueEnable(MotorID, 0) #DYNAMIXEL LIMITS CAN ONLY BE CHANGED WITH TORQUE DISABLED
        ####################################################

        MaxPWM_limited = int(self.limitNumber(0.0, 885.0, MaxPWM))

        ADDR_PRO_MAX_PWM_LIMIT = 36

        dxl_comm_result = self.packetHandler.write2ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_MAX_PWM_LIMIT, MaxPWM_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        self.MaxPWM_DynamixelUnits[MotorID] = MaxPWM_limited

        ####################################################
        self.SendInstructionPacket_SetTorqueEnable(MotorID, EngagedState_temp) #Must set the EngagedState back to what it was before we changed this limit
        ####################################################
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def SendInstructionPacket_SetPWM(self, MotorID, GoalPWM, print_bytes_for_debugging = 0):

        GoalPWM_limited = int(self.limitNumber(0.0, 885.0, GoalPWM))

        ADDR_PRO_GOAL_PWM = 100

        dxl_comm_result = self.packetHandler.write2ByteTxOnly(self.portHandler, MotorID, ADDR_PRO_GOAL_PWM, GoalPWM_limited)
        if dxl_comm_result != COMM_SUCCESS:
            dummy_var = 0
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        else:
            dummy = 0

        self.PWM_DynamixelUnits[MotorID] = GoalPWM_limited
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def PingMotor(self, MotorID, print_bytes_for_debugging = 0):

        dummy = 0

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def ReadVariable(self, MotorID, VariableName, print_bytes_for_debugging = 0):

        PortRegister = -1
        ReadLength = -1
        dxl_data = -1
        dxl_comm_result = -1
        dxl_error = -1
        Data_Value = -1111111111

        ##########################################################
        if VariableName == "Baud":
            PortRegister = 8
            ReadLength = 1
        elif VariableName == "OperatingMode":
            PortRegister = 11
            ReadLength = 1
        elif VariableName == "TemperatureLimit":
            PortRegister = 31
            ReadLength = 1
        elif VariableName == "MaxVoltageLimit":
            PortRegister = 32
            ReadLength = 2
        elif VariableName == "MinVoltageLimit":
            PortRegister = 34
            ReadLength = 2
        elif VariableName == "PWMlimit":
            PortRegister = 36
            ReadLength = 2
        elif VariableName == "CurrentLimit":
            PortRegister = 38
            ReadLength = 2
        elif VariableName == "AccelerationLimit":
            PortRegister = 40
            ReadLength = 4
        elif VariableName == "VelocityLimit":
            PortRegister = 44
            ReadLength = 4
        elif VariableName == "HardwareErrorStatus":
            PortRegister = 70
            ReadLength = 1
        elif VariableName == "RealtimeTick":
            PortRegister = 120
            ReadLength = 2
        elif VariableName == "Moving":
            PortRegister = 122
            ReadLength = 1
        elif VariableName == "MovingStatus":
            PortRegister = 123
            ReadLength = 1
        elif VariableName == "PresentPWM":
            PortRegister = 124
            ReadLength = 2
        elif VariableName == "PresentCurrent":
            PortRegister = 126
            ReadLength = 2
        elif VariableName == "PresentVelocity":
            PortRegister = 128
            ReadLength = 4
        elif VariableName == "PresentPosition":
            PortRegister = 132
            ReadLength = 4
        elif VariableName == "PresentInputVoltage":
            PortRegister = 144
            ReadLength = 2
        elif VariableName == "PresentTemperature":
            PortRegister = 146
            ReadLength = 1 #Should be 1 according to the datasheet, but 2 works and I confirmed here: https://github.com/ROBOTIS-GIT/DynamixelSDK/issues/152
        else:
            self.MyPrint_WithoutLogFile("$$$$$$$$$$$$$$$$$$$$$$$$$ ReadVariable ERROR: Variable name '" + VariableName + " is no valid! $$$$$$$$$$$$$$$$$$$$$$$$$")
            return -1111111111
        ##########################################################

        ##########################################################
        if ReadLength == 1:
            try:
                dxl_data, dxl_comm_result, dxl_error = self.packetHandler.read1ByteTxRx(self.portHandler, MotorID, PortRegister)
            except:
                pass
            
        elif ReadLength == 2:
            try:
                dxl_data, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, MotorID, PortRegister)
            except:
                pass

        elif ReadLength == 4:
            try:
                dxl_data, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, MotorID, PortRegister)
            except:
                pass
        ##########################################################

        ##########################################################
        if dxl_comm_result != COMM_SUCCESS:
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            self.portHandler.clearPort()
            return -1111111111
        elif dxl_error != 0:
            #self.MyPrint_WithoutLogFile("%s" % self.packetHandler.getRxPacketError(dxl_error))
            self.portHandler.clearPort()
            return -1111111111
        ##########################################################

        ##########################################################
        if VariableName == "PresentInputVoltage" or VariableName == "MaxVoltageLimit" or VariableName == "MinVoltageLimit":
            Data_Value = dxl_data
            #if dxl_data >= 95 and dxl_data <= 160:
            #    Data_Value = dxl_data*0.1
            #else:
            #    return -1111111111

        elif VariableName == "PresentTemperature" or VariableName == "TemperatureLimit":
            Data_Value = dxl_data
            #if dxl_data >= 0 and dxl_data <= 100:
            #    Data_Value = dxl_data*1.0
            #else:
            #    return -1111111111

        elif VariableName == "HardwareErrorStatus":
            Data_Value = dxl_data

            self.ErrorFlag_BYTE[MotorID] = Data_Value
            # Bit 7 --> 0 (self.ErrorFlag_BYTE[MotorID] & 0b10000000)
            # Bit 6 --> 0 (self.ErrorFlag_BYTE[MotorID] & 0b01000000)
            self.ErrorFlag_Overload_Received[MotorID] = (self.ErrorFlag_BYTE[MotorID] & 0b00100000)  # Bit 5 --> Instruction Error. Set to 1 if an undefined instruction is sent or an action instruction is sent without a Reg_Write instruction.
            self.ErrorFlag_ElectricalShock_Received[MotorID] = (self.ErrorFlag_BYTE[MotorID] & 0b00010000)  # Bit 4 --> Overload Error. Set to 1 if the specified maximum torque can't control the applied load.
            self.ErrorFlag_MotorEncoder_Received[MotorID] = (self.ErrorFlag_BYTE[MotorID] & 0b00001000)  # Bit 3 --> Range Error. Set to 1 if the instruction sent is out of the defined range.
            self.ErrorFlag_Overheating_Received[MotorID] = (self.ErrorFlag_BYTE[MotorID] & 0b00000100)  # Bit 2 --> Overheating Error. Set to 1 if the internal temperature of the Dynamixel unit is above the operating temperature range as defined in the control table.
            # Bit 1 --> 0
            self.ErrorFlag_InputVoltage_Received[MotorID] = (self.ErrorFlag_BYTE[MotorID] & 0b00000001)  # Bit 0 --> Input Voltage Error. Set to 1 if the voltage is out of the operating voltage range as defined in the control table.

        else:
            Data_Value = dxl_data
        ##########################################################

        ##########################################################
        if print_bytes_for_debugging == 1:
            self.MyPrint_WithoutLogFile("ReadVariable, " + VariableName + " on PortRegister " + str(PortRegister) + ": " + str(Data_Value))
        ##########################################################

        #self.portHandler.clearPort()
        return Data_Value
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    @staticmethod
    def ConvertBetweenAllAngularUnits(commanded_value, commanded_units):

        commanded_units = commanded_units.lower()

        commanded_value_raw = -1111111111
        commanded_value_dynamixelunits = -1111111111
        commanded_value_rad = -1111111111
        commanded_value_deg = -1111111111
        commanded_value_rev = -1111111111

        ######################################
        if commanded_units in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_units_acceptable_list:
            if commanded_units == "raw" or commanded_units == "dynamixelunits":

                commanded_value_raw = commanded_value
                commanded_value_dynamixelunits = commanded_value

                commanded_value_deg = commanded_value_dynamixelunits * 0.088 #0.088deg/dynamixelunit
                commanded_value_rev = commanded_value_deg / 360.0
                commanded_value_rad = commanded_value_rev * (2.0 * math.pi)

            elif commanded_units == "rad":

                commanded_value_rad = commanded_value

                commanded_value_rev = commanded_value_rad / (2.0 * math.pi)
                commanded_value_deg = 360.0 * commanded_value_rev
                commanded_value_dynamixelunits = commanded_value_deg / 0.088 #0.088deg/dynamixelunit
                commanded_value_raw = commanded_value_dynamixelunits

            elif commanded_units == "deg":

                commanded_value_deg = commanded_value

                commanded_value_dynamixelunits = commanded_value_deg / 0.088 #0.088deg/dynamixelunit
                commanded_value_raw = commanded_value_dynamixelunits
                commanded_value_rev = commanded_value_deg / 360.0
                commanded_value_rad = commanded_value_rev * (2.0 * math.pi)

            elif commanded_units == "rev":

                commanded_value_rev = commanded_value

                commanded_value_deg = 360.0 * commanded_value_rev
                commanded_value_dynamixelunits = commanded_value_deg / 0.088 #0.088deg/dynamixelunit
                commanded_value_raw = commanded_value_dynamixelunits
                commanded_value_rad = commanded_value_rev * (2.0 * math.pi)
            ######################################

            results_dict = dict([("raw", commanded_value_raw),
                                ("dynamixelunits", commanded_value_dynamixelunits),
                                ("deg", commanded_value_deg),
                                ("rad", commanded_value_rad),
                                ("rev", commanded_value_rev)])

            return results_dict

        else:
            print("Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits ERROR: The units '" + commanded_units + "' are not compatible but are limited to " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_units_acceptable_list))
            return dict()
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    @staticmethod
    def ConvertBetweenAllAngularSpeedUnits(commanded_value, commanded_units):

        commanded_units = commanded_units.lower()

        commanded_value_raw = -1111111111
        commanded_value_dynamixelunits = -1111111111
        commanded_value_deg_per_sec = -1111111111
        commanded_value_rev_per_sec = -1111111111
        commanded_value_rev_per_min = -1111111111
        commanded_value_rad_per_sec = -1111111111

        ######################################
        if commanded_units in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_speed_units_acceptable_list:
            if commanded_units == "raw" or commanded_units == "dynamixelunits":

                commanded_value_raw = commanded_value
                commanded_value_dynamixelunits = commanded_value

                commanded_value_rev_per_min = commanded_value_dynamixelunits * 0.229 #0.229RPM/dynamixelunit of speed
                commanded_value_rev_per_sec = commanded_value_rev_per_min / 60.0
                commanded_value_deg_per_sec = commanded_value_rev_per_sec * 360.0
                commanded_value_rad_per_sec = commanded_value_rev_per_sec * (2.0 * math.pi)

            elif commanded_units == "radpersec":

                commanded_value_rad_per_sec = commanded_value

                commanded_value_rev_per_sec = commanded_value_rad_per_sec / (2.0 * math.pi)
                commanded_value_rev_per_min = commanded_value_rad_per_sec * 60.0
                commanded_value_deg_per_sec = 360.0 * commanded_value_rev_per_sec
                commanded_value_dynamixelunits = commanded_value_rev_per_min / 0.229 #0.229RPM/dynamixelunit of speed
                commanded_value_raw = commanded_value_dynamixelunits

            elif commanded_units == "degpersec":

                commanded_value_deg_per_sec = commanded_value

                commanded_value_rev_per_sec = commanded_value_deg_per_sec / 360.0
                commanded_value_rev_per_min = commanded_value_rad_per_sec * 60.0
                commanded_value_rad_per_sec = commanded_value_rev_per_sec * (2.0 * math.pi)
                commanded_value_dynamixelunits = commanded_value_rev_per_min / 0.229 #0.229RPM/dynamixelunit of speed
                commanded_value_raw = commanded_value_dynamixelunits

            elif commanded_units == "revpersec":

                commanded_value_rev_per_sec = commanded_value

                commanded_value_rev_per_min = commanded_value_rad_per_sec * 60.0
                commanded_value_deg_per_sec = 360.0 * commanded_value_rev_per_sec
                commanded_value_rad_per_sec = commanded_value_rev_per_sec * (2.0 * math.pi)
                commanded_value_dynamixelunits = commanded_value_rev_per_min / 0.229 #0.229RPM/dynamixelunit of speed
                commanded_value_raw = commanded_value_dynamixelunits

            elif commanded_units == "revpermin":

                commanded_value_rev_per_min = commanded_value

                commanded_value_rev_per_sec = commanded_value / 60.0
                commanded_value_deg_per_sec = 360.0 * commanded_value_rev_per_sec
                commanded_value_rad_per_sec = commanded_value_rev_per_sec * (2.0 * math.pi)
                commanded_value_dynamixelunits = commanded_value_rev_per_min / 0.229 #0.229RPM/dynamixelunit of speed
                commanded_value_raw = commanded_value_dynamixelunits
            ######################################

            results_dict = dict([("raw", commanded_value_raw),
                                        ("dynamixelunits", commanded_value_dynamixelunits),
                                        ("degPerSec", commanded_value_deg_per_sec),
                                        ("radPerSec", commanded_value_rad_per_sec),
                                        ("revPerSec", commanded_value_rev_per_sec),
                                        ("revPerMin", commanded_value_rev_per_min)])

            return results_dict

        else:
            print("ConvertBetweenAllAngularSpeedUnits ERROR: The units '" + commanded_units + "' are not compatible but are limited to " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.angular_speed_units_acceptable_list))
            return dict()
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    @staticmethod
    def ConvertBetweenAllCurrentUnits(commanded_value, commanded_units):

        commanded_units = commanded_units.lower()

        commanded_value_raw = -1111111111
        commanded_value_dynamixelunits = -1111111111
        commanded_value_milliamps = -1111111111
        commanded_value_amps = -1111111111
        commanded_value_percent = -1111111111

        ######################################
        if commanded_units in Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.current_units_acceptable_list:
            if commanded_units == "raw" or commanded_units == "dynamixelunits":

                commanded_value_raw = commanded_value
                commanded_value_dynamixelunits = commanded_value

                commanded_value_milliamps = commanded_value_dynamixelunits * 2.69 #2.69mA/dynamixelunit
                commanded_value_amps = commanded_value_milliamps / 1000.0
                commanded_value_percent = commanded_value_dynamixelunits / 2047.0

            elif commanded_units == "milliamps":

                commanded_value_milliamps = commanded_value

                commanded_value_amps = commanded_value_milliamps / 1000.0
                commanded_value_dynamixelunits = commanded_value_milliamps / 2.69 #2.69mA/dynamixelunit
                commanded_value_raw = commanded_value_dynamixelunits
                commanded_value_percent = commanded_value_dynamixelunits / 2047.0

            elif commanded_units == "amps":

                commanded_value_amps = commanded_value

                commanded_value_milliamps = commanded_value_amps * 1000.0
                commanded_value_dynamixelunits = commanded_value_milliamps / 2.69 #2.69mA/dynamixelunit
                commanded_value_raw = commanded_value_dynamixelunits
                commanded_value_percent = commanded_value_dynamixelunits / 2047.0

            elif commanded_units == "percent":

                if commanded_value < -1.0 or commanded_value > 1.0:
                    print("ConvertBetweenAllCurrentUnits ERROR: The value '" + str(commanded_value) + "% must be in the range [0,1]")
                    return dict()

                commanded_value_percent = commanded_value

                commanded_value_dynamixelunits = commanded_value_percent*2047.0
                commanded_value_raw = commanded_value_dynamixelunits
                commanded_value_milliamps = commanded_value_dynamixelunits * 2.69 #2.69mA/dynamixelunit
                commanded_value_amps = commanded_value_milliamps / 1000.0
            ######################################

            results_dict = dict([("raw", commanded_value_raw),
                                        ("dynamixelunits", commanded_value_dynamixelunits),
                                        ("milliamps", commanded_value_milliamps),
                                        ("amps", commanded_value_amps),
                                        ("percent", commanded_value_percent)])

            return results_dict

        else:
            print("ConvertBetweenAllCurrentUnits ERROR: The units '" + commanded_units + "' are not compatible but are limited to " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.current_units_acceptable_list))
            return dict()
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def InitializeMotor(self, MotorIndex):

        self.SendInstructionPacket_SetCurrentLimit(MotorIndex, self.Current_DynamixelUnits_max[MotorIndex], 0)
        time.sleep(self.TimeToWaitBetweenCriticalInstructions)
        self.SendInstructionPacket_SetMaxVelocity(MotorIndex, self.Velocity_DynamixelUnits_max[MotorIndex], 0)
        time.sleep(self.TimeToWaitBetweenCriticalInstructions)
        self.SendInstructionPacket_SetProfileVelocity_ForAllModesExceptCurrentAndVelocity(MotorIndex, self.Velocity_DynamixelUnits_max[MotorIndex], 0)
        time.sleep(self.TimeToWaitBetweenCriticalInstructions)
        self.SendInstructionPacket_SetMaxPWM(MotorIndex, self.PWM_DynamixelUnits_max[MotorIndex], 0)
        time.sleep(self.TimeToWaitBetweenCriticalInstructions)
        self.SendInstructionPacket_ReturnDelayTime(MotorIndex, 2)
        time.sleep(self.TimeToWaitBetweenCriticalInstructions)
        self.SendInstructionPacket_SetStatusReturnLevel(MotorIndex, 1) #0: Do not respond to any instructions, 1: Respond only to READ_DATA instructions, 2: Respond to all instructions
        time.sleep(self.TimeToWaitBetweenCriticalInstructions)


        if self.HasMotorEverBeenInitializedFlag[MotorIndex] == 0:
            if self.StartEngagedFlag[MotorIndex] == 1:
                self.SetEngagedState_FROM_EXTERNAL_PROGRAM(MotorIndex, 1)
                #self.SendInstructionPacket_SetTorqueEnable(MotorIndex, 1)
                #time.sleep(self.TimeToWaitBetweenCriticalInstructions)
            else:
                self.SetEngagedState_FROM_EXTERNAL_PROGRAM(MotorIndex, 0)
                #self.SendInstructionPacket_SetTorqueEnable(MotorIndex, 0)
                #time.sleep(self.TimeToWaitBetweenCriticalInstructions)
        else:
            self.SetEngagedState_FROM_EXTERNAL_PROGRAM(MotorIndex, 1)
            #self.SendInstructionPacket_SetTorqueEnable(MotorIndex, self.EngagedState[MotorIndex])
            #time.sleep(self.TimeToWaitBetweenCriticalInstructions)

        '''
        ################################################
        for i in range(0, 2):
            time.sleep(self.TimeToWaitBetweenCriticalInstructions)
            self.OperatingModeReceived_int[MotorIndex] = self.ReadVariable(MotorIndex, "OperatingMode", 0)
            self.OperatingModeReceived_string[MotorIndex] = self.ConvertOperatingModeIntToString(self.OperatingModeReceived_int[MotorIndex])
            self.MyPrint_WithoutLogFile("InitializeMotor, " + str(self.OperatingModeReceived_int[MotorIndex]) + " | " + self.OperatingModeReceived_string[MotorIndex] + " | " + self.ControlType_StartingValueList[MotorIndex])
            time.sleep(self.TimeToWaitBetweenCriticalInstructions)

        #if self.OperatingModeReceived_string[MotorIndex] != self.ControlType_StartingValueList[MotorIndex]:
        #    self.ControlType_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] = 1
        ################################################
        '''

        ################################################ Will tell the main loop how to update the motor
        if self.ControlType[MotorIndex] == "CurrentControl":
            self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        if self.ControlType[MotorIndex] == "VelocityControl":
            self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        if self.ControlType[MotorIndex] == "PositionControl" or self.ControlType[MotorIndex] == "ExtendedPositionControlMultiTurn" or self.ControlType[MotorIndex] == "CurrentBasedPositionControl":
            self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
            self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        if self.ControlType[MotorIndex] == "PWMcontrol":
            self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
        ################################################

        self.HasMotorEverBeenInitializedFlag[MotorIndex] = 1

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def InitializeAllMotors(self):

        for MotorIndex in range(0, self.NumberOfMotors):
            self.InitializeMotor(MotorIndex)

    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    def MainThread(self): #unicorn

        self.MyPrint_WithoutLogFile("Started the MainThread thread for Dynamixel_Protocol2_Xseries_ReubenPython2and3Class object.")
        self.serialMainThread_still_running_flag = 1

        self.InitializeAllMotors()

        self.StartingTime_CalculatedFromMainThread = self.getPreciseSecondsTimeStampString()

        #############################################################################################################################################
        #############################################################################################################################################
        #############################################################################################################################################
        while self.EXIT_PROGRAM_FLAG == 0:

            ##############################################################################################
            ##############################################################################################
            self.CurrentTime_CalculatedFromMainThread = self.getPreciseSecondsTimeStampString() - self.StartingTime_CalculatedFromMainThread
            ##############################################################################################
            ##############################################################################################

            ##############################################################################################  Start GETs
            ##############################################################################################
            if self.ENABLE_GETS == 1:
                try:

                    ##############################################################################################
                    for MotorIndex in range(0, self.NumberOfMotors):

                        self.AskForInfrequentDataReadLoopCounter[MotorIndex] = self.AskForInfrequentDataReadLoopCounter[MotorIndex] + 1

                        #########################################
                        #'''
                        if self.ControlType_NEEDS_TO_BE_ASKED_FLAG[MotorIndex] == 1:
                            self.OperatingModeReceived_int[MotorIndex] = self.ReadVariable(MotorIndex, "OperatingMode", 0)
                            self.OperatingModeReceived_string[MotorIndex] = self.ConvertOperatingModeIntToString(self.OperatingModeReceived_int[MotorIndex])
                            self.MyPrint_WithoutLogFile("self.OperatingModeReceived_string, motor: " + str(MotorIndex) + ": " + self.OperatingModeReceived_string[MotorIndex])
                            self.ControlType_NEEDS_TO_BE_ASKED_FLAG[MotorIndex] = 0
                            #time.sleep(0.002) #COMMENTED OUT 02/05/2020
                        #'''
                        #########################################

                        #########################################
                        '''
                        self.ReadVariable(MotorIndex, "HardwareErrorStatus", 0)
                        if self.ErrorFlag_BYTE[MotorIndex] != 0:
                            dummy_var = 0
                            self.MyPrint_WithoutLogFile("%%%%%%%%%%%%% ERROR CODE " + str(self.ErrorFlag_BYTE[MotorIndex]) + " on motor " + str(MotorIndex))
                            #self.SendInstructionPacket_Reboot(MotorIndex)
                        time.sleep(0.002)
                        '''
                        #########################################

                        #########################################
                        PositionReceived_DynamixelUnits_temp = self.ReadVariable(MotorIndex, "PresentPosition", 0)
                        if PositionReceived_DynamixelUnits_temp != -1111111111:

                            self.PositionReceived_DynamixelUnits[MotorIndex] = PositionReceived_DynamixelUnits_temp
                            self.PositionReceived_Deg[MotorIndex] = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(self.PositionReceived_DynamixelUnits[MotorIndex], "DynamixelUnits")["deg"]
                            self.PositionReceived_Deg[MotorIndex] = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllAngularUnits(self.PositionReceived_DynamixelUnits[MotorIndex], "DynamixelUnits")["deg"]

                        #self.portHandler.clearPort()
                        #self.portHandler.closePort()
                        #self.portHandler.openPort()
                        #time.sleep(0.002) #COMMENTED OUT 02/05/2020


                        '''
                        CurrentReceived_DynamixelUnits_temp = self.ReadVariable(MotorIndex, "PresentCurrent", 0)
                        if CurrentReceived_DynamixelUnits_temp != -1111111111 and CurrentReceived_DynamixelUnits_temp >= 0 and CurrentReceived_DynamixelUnits_temp <= 2047.0:
                            self.CurrentReceived_DynamixelUnits[MotorIndex] = CurrentReceived_DynamixelUnits_temp
                            self.CurrentReceived_Amps[MotorIndex] = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllCurrentUnits(self.CurrentReceived_DynamixelUnits[MotorIndex], "dynamixelunits")["amps"]
                            self.CurrentReceived_Percent0to1[MotorIndex] = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.ConvertBetweenAllCurrentUnits(self.CurrentReceived_DynamixelUnits[MotorIndex], "dynamixelunits")["percent"]
                        time.sleep(0.002)
                        '''
                        #########################################


                        #########################################
                        '''
                        if self.AskForInfrequentDataReadLoopCounter[MotorIndex] == 1:
                            pass
                            #self.VoltageReceived_DynamixelUnits[MotorIndex] = self.ReadVariable(MotorIndex, "PresentInputVoltage", 1)
                            #time.sleep(0.002)
                        elif self.AskForInfrequentDataReadLoopCounter[MotorIndex] == 2:
                            pass
                            #self.TemperatureReceived_DynamixelUnits[MotorIndex] = self.ReadVariable(MotorIndex, "PresentTemperature", 1)
                            #time.sleep(0.002)
                        elif self.AskForInfrequentDataReadLoopCounter[MotorIndex] == 3:
                            self.OperatingModeReceived_int[MotorIndex] = self.ReadVariable(MotorIndex, "OperatingMode", 0)
                            self.OperatingModeReceived_string[MotorIndex] = self.ConvertOperatingModeIntToString(self.OperatingModeReceived_int[MotorIndex])
                            time.sleep(0.002)
                        elif self.AskForInfrequentDataReadLoopCounter[MotorIndex] == 201: #201
                            self.AskForInfrequentDataReadLoopCounter[MotorIndex] = 0
                        '''
                        #########################################


                        #print(self.ReadVariable(MotorIndex, "CurrentLimit", 0))
                        #self.RealTimeTicksMillisec[MotorIndex] = self.ReadVariable(MotorIndex, "RealtimeTick", 0)
                        #self.UpdateFrequencyCalculation_RealTimeTicksMillisecFromDynamixel(MotorIndex)
                        #self.PWMReceived_DynamixelUnits[MotorIndex] = self.ReadVariable(MotorIndex, "PresentPWM", 0)
                        #self.VelocityReceived_DynamixelUnits[MotorIndex] = self.ReadVariable(MotorIndex, "PresentVelocity", 0)
                        # self.MovingStateReceived_DynamixelUnits[MotorIndex] = self.ReadVariable(MotorIndex, "MovingState")
                        #self.ReadVariable(MotorIndex, "Baud", 1)
                    ##############################################################################################

                    '''
                    self.MostRecentDataDict = dict([("ControlType", self.ControlType),
                                                     ("Current_DynamixelUnits_TO_BE_SET", self.Current_DynamixelUnits_TO_BE_SET),
                                                     ("PWM_DynamixelUnits_TO_BE_SET", self.PWM_DynamixelUnits_TO_BE_SET),
                                                     ("Position_DynamixelUnits_TO_BE_SET", self.Position_DynamixelUnits_TO_BE_SET),
                                                     ("Velocity_DynamixelUnits_TO_BE_SET", self.Velocity_DynamixelUnits_TO_BE_SET),
                                                     ("PositionReceived_DynamixelUnits", self.PositionReceived_DynamixelUnits),
                                                     ("PositionReceived_Deg", self.PositionReceived_Deg),
                                                     ("VelocityReceived_DynamixelUnits", self.VelocityReceived_DynamixelUnits),
                                                     ("TorqueReceived_DynamixelUnits", self.TorqueReceived_DynamixelUnits),
                                                     ("VoltageReceived_DynamixelUnits", self.VoltageReceived_DynamixelUnits),
                                                     ("TemperatureReceived_DynamixelUnits", self.TemperatureReceived_DynamixelUnits),
                                                     ("Time", self.CurrentTime_CalculatedFromMainThread),
                                                     ("DataStreamingFrequency_CalculatedFromMainThread", self.DataStreamingFrequency_CalculatedFromMainThread)])
                    '''
                    self.MostRecentDataDict["PositionReceived_DynamixelUnits"] = self.PositionReceived_DynamixelUnits
                    self.MostRecentDataDict["PositionReceived_Deg"] = self.PositionReceived_Deg
                    self.MostRecentDataDict["VelocityReceived_DynamixelUnits"] = self.VelocityReceived_DynamixelUnits
                    self.MostRecentDataDict["TorqueReceived_DynamixelUnits"] = self.TorqueReceived_DynamixelUnits
                    self.MostRecentDataDict["VoltageReceived_DynamixelUnits"] = self.VoltageReceived_DynamixelUnits
                    self.MostRecentDataDict["TemperatureReceived_DynamixelUnits"] = self.TemperatureReceived_DynamixelUnits
                    self.MostRecentDataDict["Time"] = self.CurrentTime_CalculatedFromMainThread
                    self.MostRecentDataDict["DataStreamingFrequency_CalculatedFromMainThread"] = self.DataStreamingFrequency_CalculatedFromMainThread

                except:
                    exceptions = sys.exc_info()[0]
                    self.MyPrint_WithoutLogFile("MainThread GETS, exceptions: %s" % exceptions)
                    traceback.print_exc()
            ##############################################################################################
            ############################################################################################## End GETs

            ############################################################################################## StartSETs
            ##############################################################################################
            if self.ENABLE_SETS == 1:
                try:

                    ###############################################
                    self.MostRecentDataDict["ControlType"] = self.ControlType
                    self.MostRecentDataDict["Current_DynamixelUnits_TO_BE_SET"] = self.Current_DynamixelUnits_TO_BE_SET
                    self.MostRecentDataDict["PWM_DynamixelUnits_TO_BE_SET"] = self.PWM_DynamixelUnits_TO_BE_SET
                    self.MostRecentDataDict["Position_DynamixelUnits_TO_BE_SET"] = self.Position_DynamixelUnits_TO_BE_SET
                    self.MostRecentDataDict["Velocity_DynamixelUnits_TO_BE_SET"] = self.Velocity_DynamixelUnits_TO_BE_SET
                    ###############################################

                    for MotorIndex in range(0, self.NumberOfMotors):

                        #########################################################
                        if self.Reboot_NeedsToTakePlaceFlag[MotorIndex] == 1:
                            self.SendInstructionPacket_Reboot(MotorIndex)
                            time.sleep(0.25) #FIGURE OUT HOW LOW THIS CAN GO

                            self.InitializeMotor(MotorIndex)

                            self.ResetSerial()

                            self.Reboot_NeedsToTakePlaceFlag[MotorIndex] = 0
                        #########################################################

                        #########################################################
                        if self.ResetSerial_NeedsToTakePlaceFlag[MotorIndex] == 1:
                            self.ResetSerial()
                            self.ResetSerial_NeedsToTakePlaceFlag[MotorIndex] = 0
                        #########################################################

                        #'''
                        #########################################################
                        if self.ControlType_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] == 1:
                            self.SendInstructionPacket_SetOperatingMode(MotorIndex, self.ControlType_TO_BE_SET[MotorIndex])
                            self.ControlType_NEEDS_TO_BE_ASKED_FLAG[MotorIndex] = 1

                            time.sleep(0.030)

                            self.SendInstructionPacket_SetCurrentLimit(MotorIndex, self.Current_DynamixelUnits_max[MotorIndex], 0)

                            #time.sleep(0.001)
                            self.ControlType_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] = 0
                        #########################################################
                        #'''

                        #########################################################
                        if self.ToggleMinMax_NeedsToTakePlaceFlag[MotorIndex] == 1:

                            self.MyPrint_WithoutLogFile("Position_DynamixelUnits_min valid: " + str(self.Position_DynamixelUnits_min))
                            self.MyPrint_WithoutLogFile("Position_DynamixelUnits_StartingValueList valid: " + str(self.Position_DynamixelUnits_StartingValueList))
                            self.MyPrint_WithoutLogFile("Position_DynamixelUnits_max valid: " + str(self.Position_DynamixelUnits_max))
                            
                            if self.ToggleMinMax_TO_BE_SET[MotorIndex] == -1:
                                
                                if self.ControlType[MotorIndex] == "CurrentControl":
                                    self.Current_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Current_DynamixelUnits_min[MotorIndex]
                                    self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "VelocityControl":
                                    self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Velocity_DynamixelUnits_min[MotorIndex]
                                    self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "PositionControl" or self.ControlType[MotorIndex] == "ExtendedPositionControlMultiTurn" or self.ControlType[MotorIndex] == "CurrentBasedPositionControl":
                                    self.Position_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Position_DynamixelUnits_min[MotorIndex]
                                    print(self.Position_DynamixelUnits_TO_BE_SET[MotorIndex])
                                    self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "PWMcontrol":
                                    self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex] = self.PWM_DynamixelUnits_min[MotorIndex]
                                    self.PWM_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

                            elif self.ToggleMinMax_TO_BE_SET[MotorIndex] == 0:

                                if self.ControlType[MotorIndex] == "CurrentControl":
                                    self.Current_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Current_DynamixelUnits_StartingValueList[MotorIndex]
                                    self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "VelocityControl":
                                    self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Velocity_DynamixelUnits_StartingValueList[MotorIndex]
                                    self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "PositionControl" or self.ControlType[MotorIndex] == "ExtendedPositionControlMultiTurn" or self.ControlType[MotorIndex] == "CurrentBasedPositionControl":
                                    self.Position_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Position_DynamixelUnits_StartingValueList[MotorIndex]
                                    print(self.Position_DynamixelUnits_TO_BE_SET[MotorIndex])
                                    self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "PWMcontrol":
                                    self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex] = self.PWM_DynamixelUnits_StartingValueList[MotorIndex]
                                    self.PWM_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

                            elif self.ToggleMinMax_TO_BE_SET[MotorIndex] == 1:
                            
                                if self.ControlType[MotorIndex] == "CurrentControl":
                                    self.Current_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Current_DynamixelUnits_max[MotorIndex]
                                    self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "VelocityControl":
                                    self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Velocity_DynamixelUnits_max[MotorIndex]
                                    self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "PositionControl" or self.ControlType[MotorIndex] == "ExtendedPositionControlMultiTurn" or self.ControlType[MotorIndex] == "CurrentBasedPositionControl":
                                    self.Position_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Position_DynamixelUnits_max[MotorIndex]
                                    print(self.Position_DynamixelUnits_TO_BE_SET[MotorIndex])
                                    self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                                elif self.ControlType[MotorIndex] == "PWMcontrol":
                                    self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex] = self.PWM_DynamixelUnits_max[MotorIndex]
                                    self.PWM_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 1
                                    self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1
                            
                            self.ToggleMinMax_state[MotorIndex] = self.ToggleMinMax_TO_BE_SET[MotorIndex]
                            self.ToggleMinMax_NeedsToTakePlaceFlag[MotorIndex] = 0
                        #########################################################

                        ###############################################
                        if self.MinPositionLimit_NeedsToBeChangedFlag[MotorIndex] == 1:
                            #self.SendInstructionPacket_SetCWandMaxPositionLimits(MotorIndex, self.MinPositionLimit_TO_BE_SET[MotorIndex], self.MaxPositionLimit_TO_BE_SET[MotorIndex])
                            #time.sleep(0.001)
                            self.MinPositionLimit_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                        ###############################################
                        if self.MaxPositionLimit_NeedsToBeChangedFlag[MotorIndex] == 1:
                            #self.SendInstructionPacket_SetCWandMaxPositionLimits(MotorIndex, self.MinPositionLimit_TO_BE_SET[MotorIndex], self.MaxPositionLimit_TO_BE_SET[MotorIndex])
                            #time.sleep(0.001)
                            self.MaxPositionLimit_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                        ###############################################
                        if self.EngagedState_NeedsToBeChangedFlag[MotorIndex] == 1:
                            self.SendInstructionPacket_SetTorqueEnable(MotorIndex, self.EngagedState_TO_BE_SET[MotorIndex])
                            #time.sleep(0.001)
                            self.EngagedState_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                        ###############################################
                        if self.LEDstate_NeedsToBeChangedFlag[MotorIndex] == 1:
                            self.SendInstructionPacket_SetLED(MotorIndex, self.LEDstate_TO_BE_SET[MotorIndex])
                            #time.sleep(0.001)
                            self.LEDstate_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                        ###############################################
                        if self.MaxPWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] == 1:
                            self.SendInstructionPacket_SetMaxPWM(MotorIndex, self.MaxPWM_DynamixelUnits_TO_BE_SET[MotorIndex])
                            #time.sleep(0.001)
                            self.MaxPWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                        ###############################################
                        if self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] > 0:

                            if self.ControlType[MotorIndex] == "CurrentControl":
                                Current_limited = self.limitNumber(self.Current_DynamixelUnits_min[MotorIndex], self.Current_DynamixelUnits_max[MotorIndex], self.Current_DynamixelUnits_TO_BE_SET[MotorIndex])
                                self.SendInstructionPacket_SetGoalCurrent_ForCurrentAndCurrentBasedPositionControl(MotorIndex, Current_limited, 0)
                            else:
                                Current_limited = self.limitNumber(10, self.Current_DynamixelUnits_max[MotorIndex], self.Current_DynamixelUnits_TO_BE_SET[MotorIndex])
                                self.SendInstructionPacket_SetCurrentLimit(MotorIndex, Current_limited, 0)

                            if self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] >= 1:
                                self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] - 1
                                #self.MyPrint_WithoutLogFile("self.Current_DynamixelUnits_NeedsToBeChangedFlag[" + str(MotorIndex) + "]: " + str(self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex]))
                            #time.sleep(0.001)
                        ###############################################

                        ###############################################
                        if self.ControlType[MotorIndex] == "VelocityControl":
                            if self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] == 1:
                                Velocity_limited = self.limitNumber(self.Velocity_DynamixelUnits_min[MotorIndex], self.Velocity_DynamixelUnits_max[MotorIndex], self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex])
                                self.SendInstructionPacket_SetGoalVelocity_ForVelocityModeOnly(MotorIndex, Velocity_limited, 0)
                                # time.sleep(0.001)
                                self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                        ###############################################
                        if self.ControlType[MotorIndex] == "PositionControl" or self.ControlType[MotorIndex] == "ExtendedPositionControlMultiTurn" or self.ControlType[MotorIndex] == "CurrentBasedPositionControl":
                            ###############################################
                            if self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex]:
                                Position_limited = self.limitNumber(self.Position_DynamixelUnits_min[MotorIndex], self.Position_DynamixelUnits_max[MotorIndex], self.Position_DynamixelUnits_TO_BE_SET[MotorIndex])
                                self.SendInstructionPacket_SetPosition(MotorIndex, Position_limited, 0)
                                #time.sleep(0.001)
                                self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 0
                            ###############################################

                            ###############################################
                            if self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] == 1:
                                Velocity_limited = self.limitNumber(self.Velocity_DynamixelUnits_min[MotorIndex], self.Velocity_DynamixelUnits_max[MotorIndex], self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex])
                                self.SendInstructionPacket_SetProfileVelocity_ForAllModesExceptCurrentAndVelocity(MotorIndex, Velocity_limited, 0)
                                # time.sleep(0.001)
                                self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 0
                            ###############################################
                        ###############################################

                        ###############################################
                        if self.ControlType[MotorIndex] == "PWMcontrol":
                            if self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex]:
                                PWM_limited = self.limitNumber(self.PWM_DynamixelUnits_min[MotorIndex], self.PWM_DynamixelUnits_max[MotorIndex], self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex])
                                self.SendInstructionPacket_SetPWM(MotorIndex, PWM_limited, 0)
                                #time.sleep(0.001)
                                self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 0
                        ###############################################

                except:
                    exceptions = sys.exc_info()[0]
                    self.MyPrint_WithoutLogFile("MainThread SETS, exceptions: %s" % exceptions)
                    traceback.print_exc()
            ##############################################################################################
            ##############################################################################################  End SETs

            time.sleep(self.MainThread_TimeToSleepEachLoop)
            self.UpdateFrequencyCalculation_CalculatedFromMainThread()
            #############################################################################################################################################
            #############################################################################################################################################
            #############################################################################################################################################

        self.MyPrint_WithoutLogFile("Finished the MainThread for Dynamixel_Protocol2_Xseries_ReubenPython2and3Class object.")
        self.serialMainThread_still_running_flag = 0

        return 0
    #######################################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ExitProgram_Callback(self):

        print("Exiting all threads for MQTTreubenPython2and3Class object")

        self.EXIT_PROGRAM_FLAG = 1

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def StartGUI(self, GuiParent=None):

        GUI_Thread_ThreadingObject = threading.Thread(target=self.GUI_Thread, args=(GuiParent,))
        GUI_Thread_ThreadingObject.setDaemon(True) #Should mean that the GUI thread is destroyed automatically when the main thread is destroyed.
        GUI_Thread_ThreadingObject.start()
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def GUI_Thread(self, parent=None):

        print("Starting the GUI_Thread for MyPrintClassPython3exp2 object.")

        ########################
        if parent == None:  #This class object owns root and must handle it properly
            self.root = Tk()
            self.parent = self.root

            ################################################### SET THE DEFAULT FONT FOR ALL WIDGETS CREATED AFTTER/BELOW THIS CALL
            default_font = tkFont.nametofont("TkDefaultFont")
            default_font.configure(size=8)
            self.root.option_add("*Font", default_font)
            ###################################################

        else:
            self.root = parent
            self.parent = parent
        ########################

        ########################
        self.myFrame = Frame(self.root)

        if self.UseBorderAroundThisGuiObjectFlag == 1:
            self.myFrame["borderwidth"] = 2
            self.myFrame["relief"] = "ridge"

        self.myFrame.grid(row = self.GUI_ROW,
                          column = self.GUI_COLUMN,
                          padx = self.GUI_PADX,
                          pady = self.GUI_PADY,
                          rowspan = self.GUI_ROWSPAN,
                          columnspan= self.GUI_COLUMNSPAN,
                          sticky = self.GUI_STICKY)
        ########################

        ##############################################################################################################
        ##############################################################################################################
        #######################################################
        self.SmallGUIobjectsFrame = Frame(self.myFrame)
        self.SmallGUIobjectsFrame["borderwidth"] = 2
        self.SmallGUIobjectsFrame["relief"] = "ridge"
        #self.SmallGUIobjectsFrame.grid(row=0, column=0, padx=1, pady=1, columnspan=20, rowspan=1)
        #######################################################

        ##############################################################################################################
        ##############################################################################################################

        #################################################
        self.device_info_label = Label(self.myFrame, text="Device Info", width=50)
        self.device_info_label.grid(row=0, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
        #################################################

        #################################################
        self.data_label = Label(self.myFrame, text="data_label", width=50)
        self.data_label.grid(row=0, column=3, padx=1, pady=1, columnspan=1, rowspan=1)
        #################################################

        #################################################
        self.error_label = Label(self.myFrame, text="error_label", width=50)
        self.error_label.grid(row=0, column=4, padx=1, pady=1, columnspan=5, rowspan=1)
        #################################################

        #################################################
        self.DisengageAllMotorsButton = Button(self.myFrame, text="Disengage All Motors", state="normal", bg = "red", width=20,command=lambda i=1: self.DisengageAllMotorsButtonResponse())
        self.DisengageAllMotorsButton.grid(row=2, column=0, padx=1, pady=1, columnspan=2, rowspan=1)
        #################################################

        #################################################
        self.EngageAllMotorsButton = Button(self.myFrame, text="Engage All Motors", state="normal", bg = "green", width=20,command=lambda i=1: self.EngageAllMotorsButtonResponse())
        self.EngageAllMotorsButton.grid(row=2, column=2, padx=1, pady=1, columnspan=2, rowspan=1)
        #################################################

        #################################################
        self.printToGui_label = Label(self.myFrame, text="printToGui_label", width=75)
        if self.EnableInternal_MyPrint_Flag == 1:
            self.printToGui_label.grid(row=0, column=10, padx=1, pady=1, columnspan=30, rowspan=1)
        #################################################

        #################################################
        #################################################
        #################################################
        self.Position_DynamixelUnits_ScaleLabel = []
        self.Position_DynamixelUnits_ScaleValue = []
        self.Position_DynamixelUnits_Scale = []

        self.Velocity_DynamixelUnits_ScaleLabel = []
        self.Velocity_DynamixelUnits_ScaleValue = []
        self.Velocity_DynamixelUnits_Scale = []

        self.Current_DynamixelUnits_ScaleLabel = []
        self.Current_DynamixelUnits_ScaleValue = []
        self.Current_DynamixelUnits_Scale = []

        self.PWM_DynamixelUnits_ScaleLabel = []
        self.PWM_DynamixelUnits_ScaleValue = []
        self.PWM_DynamixelUnits_Scale = []

        self.MinPositionLimit_label = []
        self.MinPositionLimit_StringVar = []
        self.MinPositionLimit_Entry = []

        self.MaxPositionLimit_label = []
        self.MaxPositionLimit_StringVar = []
        self.MaxPositionLimit_Entry = []

        self.MaxPWM_DynamixelUnits_label = []
        self.MaxPWM_DynamixelUnits_StringVar = []
        self.MaxPWM_DynamixelUnits_Entry = []

        self.EngagedState_Checkbutton = []
        self.EngagedState_Checkbutton_Value = []

        self.LEDstate_Checkbutton = []
        self.LEDstate_Checkbutton_Value = []

        self.ToggleMinMax_Button = []
        self.ResetSerial_Button = []
        self.Reboot_Button = []

        self.ControlTypeRadiobutton_SelectionVar = []
        self.ControlTypeRadiobutton_CurrentControl = []
        self.ControlTypeRadiobutton_VelocityControl = []
        self.ControlTypeRadiobutton_PositionControl = []
        self.ControlTypeRadiobutton_ExtendedPositionControlMultiTurn = []
        self.ControlTypeRadiobutton_CurrentBasedPositionControl = []
        self.ControlTypeRadiobutton_PWMcontrol = []

        self.TkinterScaleWidth = 10
        self.TkinterScaleLength = 200

        for MotorIndex in range(0, self.NumberOfMotors):
            #################################################
            self.Position_DynamixelUnits_ScaleLabel.append(Label(self.myFrame, text="Pos M" + str(MotorIndex) + "\n" + self.MotorName_StringList[MotorIndex], width=self.TkinterScaleWidth))
            self.Position_DynamixelUnits_ScaleLabel[MotorIndex].grid(row=3 + MotorIndex*2, column=0, padx=1, pady=1, columnspan=1, rowspan=1)

            self.Position_DynamixelUnits_ScaleValue.append(DoubleVar())
            self.Position_DynamixelUnits_Scale.append(Scale(self.myFrame, \
                                            from_=self.Position_DynamixelUnits_min[MotorIndex],\
                                            to=self.Position_DynamixelUnits_max[MotorIndex],\
                                            #tickinterval=(self.Position_DynamixelUnits_max[MotorIndex] - self.Position_DynamixelUnits_min[MotorIndex]) / 2.0,\
                                            orient=HORIZONTAL,\
                                            borderwidth=2,\
                                            showvalue=1,\
                                            width=self.TkinterScaleWidth,\
                                            length=self.TkinterScaleLength,\
                                            resolution=1,\
                                            variable=self.Position_DynamixelUnits_ScaleValue[MotorIndex]))
            self.Position_DynamixelUnits_Scale[MotorIndex].bind('<Button-1>', lambda event, name=MotorIndex: self.Position_DynamixelUnits_ScaleResponse(event, name))
            self.Position_DynamixelUnits_Scale[MotorIndex].bind('<B1-Motion>', lambda event, name=MotorIndex: self.Position_DynamixelUnits_ScaleResponse(event, name))
            self.Position_DynamixelUnits_Scale[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.Position_DynamixelUnits_ScaleResponse(event, name))
            self.Position_DynamixelUnits_Scale[MotorIndex].set(self.Position_DynamixelUnits_StartingValueList[MotorIndex])
            self.Position_DynamixelUnits_Scale[MotorIndex].grid(row=3 + MotorIndex*2, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
            #################################################

            #################################################
            self.Velocity_DynamixelUnits_ScaleLabel.append(Label(self.myFrame, text="Vel M" + str(MotorIndex) + "\n" + self.MotorName_StringList[MotorIndex], width=self.TkinterScaleWidth))
            self.Velocity_DynamixelUnits_ScaleLabel[MotorIndex].grid(row=3 + MotorIndex*2, column=2, padx=1, pady=1, columnspan=1, rowspan=1)

            self.Velocity_DynamixelUnits_ScaleValue.append(DoubleVar())
            self.Velocity_DynamixelUnits_Scale.append(Scale(self.myFrame,\
                                                        from_=self.Velocity_DynamixelUnits_min[MotorIndex],\
                                                        to=self.Velocity_DynamixelUnits_max[MotorIndex],\
                                                        #tickinterval=(self.Velocity_DynamixelUnits_max[MotorIndex] - self.Velocity_DynamixelUnits_min[MotorIndex]) / 2.0,\
                                                        orient=HORIZONTAL,\
                                                        showvalue=1,\
                                                        width=self.TkinterScaleWidth,\
                                                        length=self.TkinterScaleLength,\
                                                        resolution=1,\
                                                        variable=self.Velocity_DynamixelUnits_ScaleValue[MotorIndex]))
            self.Velocity_DynamixelUnits_Scale[MotorIndex].bind('<Button-1>', lambda event, name=MotorIndex: self.Velocity_DynamixelUnits_ScaleResponse(event, name))
            self.Velocity_DynamixelUnits_Scale[MotorIndex].bind('<B1-Motion>', lambda event, name=MotorIndex: self.Velocity_DynamixelUnits_ScaleResponse(event, name))
            self.Velocity_DynamixelUnits_Scale[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.Velocity_DynamixelUnits_ScaleResponse(event, name))
            self.Velocity_DynamixelUnits_Scale[MotorIndex].set(self.Velocity_DynamixelUnits_StartingValueList[MotorIndex])
            self.Velocity_DynamixelUnits_Scale[MotorIndex].grid(row=3 + MotorIndex*2, column=3, padx=1, pady=1, columnspan=1, rowspan=1)
            #################################################

            #################################################
            self.Current_DynamixelUnits_ScaleLabel.append(Label(self.myFrame, text="Cur M" + str(MotorIndex) + "\n" + self.MotorName_StringList[MotorIndex], width=self.TkinterScaleWidth))
            self.Current_DynamixelUnits_ScaleLabel[MotorIndex].grid(row=4 + MotorIndex*2, column=0, padx=1, pady=1, columnspan=1, rowspan=1)

            self.Current_DynamixelUnits_ScaleValue.append(DoubleVar())
            self.Current_DynamixelUnits_Scale.append(Scale(self.myFrame, \
                                            from_=self.Current_DynamixelUnits_min[MotorIndex],\
                                            to=self.Current_DynamixelUnits_max[MotorIndex],\
                                            #tickinterval=(self.Current_DynamixelUnits_max[MotorIndex] - self.Current_DynamixelUnits_min[MotorIndex]) / 2.0,\
                                            orient=HORIZONTAL,\
                                            borderwidth=2,\
                                            showvalue=1,\
                                            width=self.TkinterScaleWidth,\
                                            length=self.TkinterScaleLength,\
                                            resolution=1,\
                                            variable=self.Current_DynamixelUnits_ScaleValue[MotorIndex]))
            self.Current_DynamixelUnits_Scale[MotorIndex].bind('<Button-1>', lambda event, name=MotorIndex: self.Current_DynamixelUnits_ScaleResponse(event, name))
            self.Current_DynamixelUnits_Scale[MotorIndex].bind('<B1-Motion>', lambda event, name=MotorIndex: self.Current_DynamixelUnits_ScaleResponse(event, name))
            self.Current_DynamixelUnits_Scale[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.Current_DynamixelUnits_ScaleResponse(event, name))
            self.Current_DynamixelUnits_Scale[MotorIndex].set(self.Current_DynamixelUnits_StartingValueList[MotorIndex])
            self.Current_DynamixelUnits_Scale[MotorIndex].grid(row=4 + MotorIndex*2, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
            #################################################
            
            #################################################
            self.PWM_DynamixelUnits_ScaleLabel.append(Label(self.myFrame, text="PWM M" + str(MotorIndex) + "\n" + self.MotorName_StringList[MotorIndex], width=self.TkinterScaleWidth))
            self.PWM_DynamixelUnits_ScaleLabel[MotorIndex].grid(row=4 + MotorIndex*2, column=2, padx=1, pady=1, columnspan=1, rowspan=1)

            self.PWM_DynamixelUnits_ScaleValue.append(DoubleVar())
            self.PWM_DynamixelUnits_Scale.append(Scale(self.myFrame, \
                                            from_=self.PWM_DynamixelUnits_min[MotorIndex],\
                                            to=self.PWM_DynamixelUnits_max[MotorIndex],\
                                            #tickinterval=(self.PWM_DynamixelUnits_max[MotorIndex] - self.PWM_DynamixelUnits_min[MotorIndex]) / 2.0,\
                                            orient=HORIZONTAL,\
                                            borderwidth=2,\
                                            showvalue=1,\
                                            width=self.TkinterScaleWidth,\
                                            length=self.TkinterScaleLength,\
                                            resolution=1,\
                                            variable=self.PWM_DynamixelUnits_ScaleValue[MotorIndex]))
            self.PWM_DynamixelUnits_Scale[MotorIndex].bind('<Button-1>', lambda event, name=MotorIndex: self.PWM_DynamixelUnits_ScaleResponse(event, name))
            self.PWM_DynamixelUnits_Scale[MotorIndex].bind('<B1-Motion>', lambda event, name=MotorIndex: self.PWM_DynamixelUnits_ScaleResponse(event, name))
            self.PWM_DynamixelUnits_Scale[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.PWM_DynamixelUnits_ScaleResponse(event, name))
            self.PWM_DynamixelUnits_Scale[MotorIndex].set(self.PWM_DynamixelUnits_StartingValueList[MotorIndex])
            self.PWM_DynamixelUnits_Scale[MotorIndex].grid(row=4 + MotorIndex*2, column=3, padx=1, pady=1, columnspan=1, rowspan=1)
            #################################################

            self.ENTRY_WIDTH = 5
            self.ENTRY_LABEL_WIDTH = 10

            '''
            #######################################################
            #######################################################
            self.MinPositionLimit_label.append(Label(self.myFrame, text="MinPositionLimit", width=self.ENTRY_LABEL_WIDTH))
            self.MinPositionLimit_label[MotorIndex].grid(row=3 + MotorIndex*2, column=4, padx=1, pady=1, columnspan=1, rowspan=1)

            self.MinPositionLimit_StringVar.append(StringVar())
            self.MinPositionLimit_StringVar[MotorIndex].set(self.MinPositionLimit_StartingValueList[MotorIndex])
            self.MinPositionLimit_Entry.append(Entry(self.myFrame, width=self.ENTRY_WIDTH, state="normal", textvariable=self.MinPositionLimit_StringVar[MotorIndex]))
            self.MinPositionLimit_Entry[MotorIndex].grid(row=3 + MotorIndex*2, column=5, padx=1, pady=1, columnspan=1, rowspan=1)
            self.MinPositionLimit_Entry[MotorIndex].bind('<Return>', lambda name=MotorIndex: self.MinPositionLimit_Entry_Response(name))
            #######################################################
            #######################################################

            #######################################################
            #######################################################
            self.MaxPositionLimit_label.append(Label(self.myFrame, text="MaxPositionLimit", width=self.ENTRY_LABEL_WIDTH))
            self.MaxPositionLimit_label[MotorIndex].grid(row=3 + MotorIndex*2, column=6, padx=1, pady=1, columnspan=1, rowspan=1)

            self.MaxPositionLimit_StringVar.append(StringVar())
            self.MaxPositionLimit_StringVar[MotorIndex].set(self.MaxPositionLimit_StartingValueList[MotorIndex])
            self.MaxPositionLimit_Entry.append(Entry(self.myFrame, width=self.ENTRY_WIDTH, state="normal", textvariable=self.MaxPositionLimit_StringVar[MotorIndex]))
            self.MaxPositionLimit_Entry[MotorIndex].grid(row=3 + MotorIndex*2, column=7, padx=1, pady=1, columnspan=1, rowspan=1)
            self.MaxPositionLimit_Entry[MotorIndex].bind('<Return>', lambda name=MotorIndex: self.MaxPositionLimit_Entry_Response(name))
            #######################################################
            #######################################################
            '''

            '''
            #######################################################
            #######################################################
            self.MaxPWM_DynamixelUnits_label.append(Label(self.myFrame, text="MaxPWM", width=self.ENTRY_LABEL_WIDTH))
            self.MaxPWM_DynamixelUnits_label[MotorIndex].grid(row=3 + MotorIndex*2, column=8, padx=1, pady=1, columnspan=1, rowspan=1)

            self.MaxPWM_DynamixelUnits_StringVar.append(StringVar())
            self.MaxPWM_DynamixelUnits_StringVar[MotorIndex].set(self.PWM_DynamixelUnits_max[MotorIndex])
            self.MaxPWM_DynamixelUnits_Entry.append(Entry(self.myFrame, width=self.ENTRY_WIDTH, state="normal", textvariable=self.MaxPWM_DynamixelUnits_StringVar[MotorIndex]))
            self.MaxPWM_DynamixelUnits_Entry[MotorIndex].grid(row=3 + MotorIndex*2, column=9, padx=1, pady=1, columnspan=1, rowspan=1)
            self.MaxPWM_DynamixelUnits_Entry[MotorIndex].bind('<Return>', lambda event, name=MotorIndex: self.MaxPWM_DynamixelUnits_Entry_Response(event, name))
            #######################################################
            #######################################################
            '''

            ###########################################################
            self.ToggleMinMax_Button.append(Button(self.myFrame,
                                            width=15,
                                            text='ToggleMinMax M' + str(MotorIndex),
                                            state="normal"))
            self.ToggleMinMax_Button[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.ToggleMinMax_ButtonResponse(event, name))
            self.ToggleMinMax_Button[MotorIndex].grid(row=3 + MotorIndex*2, column=5, padx=1, pady=1, columnspan=1, rowspan=1)
            ###########################################################

            ###########################################################
            self.ResetSerial_Button.append(Button(self.myFrame,
                                            width=15,
                                            text='ResetSerial M' + str(MotorIndex),
                                            state="normal"))
            self.ResetSerial_Button[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.ResetSerial_ButtonResponse(event, name))
            self.ResetSerial_Button[MotorIndex].grid(row=3 + MotorIndex*2, column=6, padx=1, pady=1, columnspan=1, rowspan=1)
            ###########################################################

            ###########################################################
            self.Reboot_Button.append(Button(self.myFrame,
                                            width=15,
                                            text='Reboot M' + str(MotorIndex),
                                            state="normal"))
            self.Reboot_Button[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.Reboot_ButtonResponse(event, name))
            self.Reboot_Button[MotorIndex].grid(row=3 + MotorIndex*2, column=7, padx=1, pady=1, columnspan=1, rowspan=1)
            ###########################################################

            ###########################################################
            self.EngagedState_Checkbutton_Value.append(DoubleVar())

            if self.EngagedState[MotorIndex] == 1:
                self.EngagedState_Checkbutton_Value[MotorIndex].set(1)
            else:
                self.EngagedState_Checkbutton_Value[MotorIndex].set(0)

            self.EngagedState_Checkbutton.append(Checkbutton(self.myFrame,
                                                            width=15,
                                                            text='Engage M' + str(MotorIndex),
                                                            state="normal",
                                                            variable=self.EngagedState_Checkbutton_Value[MotorIndex]))
            self.EngagedState_Checkbutton[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.EngagedState_CheckbuttonResponse(event, name))
            self.EngagedState_Checkbutton[MotorIndex].grid(row=3 + MotorIndex*2, column=8, padx=1, pady=1, columnspan=1, rowspan=1)
            ###########################################################

            ###########################################################
            self.LEDstate_Checkbutton_Value.append(DoubleVar())
            self.LEDstate_Checkbutton_Value[MotorIndex].set(0)
            self.LEDstate_Checkbutton.append(Checkbutton(self.myFrame,
                                                            width=15,
                                                            text='LED M' + str(MotorIndex),
                                                            state="normal",
                                                            variable=self.LEDstate_Checkbutton_Value[MotorIndex]))
            self.LEDstate_Checkbutton[MotorIndex].bind('<ButtonRelease-1>', lambda event, name=MotorIndex: self.LEDstate_CheckbuttonResponse(event, name))
            self.LEDstate_Checkbutton[MotorIndex].grid(row=3 + MotorIndex*2, column=9, padx=1, pady=1, columnspan=1, rowspan=1)
            ###########################################################

            ###########################################################
            self.ControlTypeRadiobutton_SelectionVar.append(StringVar())
            ###########################################################

            ###########################################################
            self.ControlTypeRadiobutton_CurrentControl.append(Radiobutton(self.myFrame,
                                                          text="CurrentControl",
                                                          state="normal",
                                                          width=15,
                                                          anchor="w",
                                                          variable=self.ControlTypeRadiobutton_SelectionVar[MotorIndex],
                                                          value="CurrentControl",
                                                          command=lambda name=MotorIndex: self.ControlTypeRadiobutton_Response(name)))
            self.ControlTypeRadiobutton_CurrentControl[MotorIndex].grid(row=4 + MotorIndex*2, column=5, padx=1, pady=1, columnspan=1, rowspan=1)
            if self.ControlType_StartingValueList[MotorIndex] == "CurrentControl":
                self.ControlTypeRadiobutton_CurrentControl[MotorIndex].select()
                #self.ControlTypeRadiobutton_CurrentControl[MotorIndex].invoke()
            ###########################################################

            ###########################################################
            self.ControlTypeRadiobutton_VelocityControl.append(Radiobutton(self.myFrame,
                                                          text="VelocityControl",
                                                          state="normal",
                                                          width=15,
                                                          anchor="w",
                                                          variable=self.ControlTypeRadiobutton_SelectionVar[MotorIndex],
                                                          value="VelocityControl",
                                                          command=lambda name=MotorIndex: self.ControlTypeRadiobutton_Response(name)))
            self.ControlTypeRadiobutton_VelocityControl[MotorIndex].grid(row=4 + MotorIndex*2, column=6, padx=1, pady=1, columnspan=1, rowspan=1)
            if self.ControlType_StartingValueList[MotorIndex] == "VelocityControl":
                self.ControlTypeRadiobutton_VelocityControl[MotorIndex].select()
                #self.ControlTypeRadiobutton_VelocityControl[MotorIndex].invoke()
            ###########################################################
            
            ###########################################################
            self.ControlTypeRadiobutton_PositionControl.append(Radiobutton(self.myFrame,
                                                          text="PositionControl",
                                                          state="normal",
                                                          width=15,
                                                          anchor="w",
                                                          variable=self.ControlTypeRadiobutton_SelectionVar[MotorIndex],
                                                          value="PositionControl",
                                                          command=lambda name=MotorIndex: self.ControlTypeRadiobutton_Response(name)))
            self.ControlTypeRadiobutton_PositionControl[MotorIndex].grid(row=4 + MotorIndex*2, column=7, padx=1, pady=1, columnspan=1, rowspan=1)
            if self.ControlType_StartingValueList[MotorIndex] == "PositionControl":
                self.ControlTypeRadiobutton_PositionControl[MotorIndex].select()
                #self.ControlTypeRadiobutton_PositionControl[MotorIndex].invoke()
            ###########################################################
            
            ###########################################################
            self.ControlTypeRadiobutton_ExtendedPositionControlMultiTurn.append(Radiobutton(self.myFrame,
                                                          text="ExtendedPositionControlMultiTurn",
                                                          state="normal",
                                                          width=15,
                                                          anchor="w",
                                                          variable=self.ControlTypeRadiobutton_SelectionVar[MotorIndex],
                                                          value="ExtendedPositionControlMultiTurn",
                                                          command=lambda name=MotorIndex: self.ControlTypeRadiobutton_Response(name)))
            self.ControlTypeRadiobutton_ExtendedPositionControlMultiTurn[MotorIndex].grid(row=4 + MotorIndex*2, column=8, padx=1, pady=1, columnspan=1, rowspan=1)
            if self.ControlType_StartingValueList[MotorIndex] == "ExtendedPositionControlMultiTurn":
                self.ControlTypeRadiobutton_ExtendedPositionControlMultiTurn[MotorIndex].select()
                #self.ControlTypeRadiobutton_ExtendedPositionControlMultiTurn[MotorIndex].invoke()
            ###########################################################
            
            ###########################################################
            self.ControlTypeRadiobutton_CurrentBasedPositionControl.append(Radiobutton(self.myFrame,
                                                          text="CurrentBasedPositionControl",
                                                          state="normal",
                                                          width=15,
                                                          anchor="w",
                                                          variable=self.ControlTypeRadiobutton_SelectionVar[MotorIndex],
                                                          value="CurrentBasedPositionControl",
                                                          command=lambda name=MotorIndex: self.ControlTypeRadiobutton_Response(name)))
            self.ControlTypeRadiobutton_CurrentBasedPositionControl[MotorIndex].grid(row=4 + MotorIndex*2, column=9, padx=1, pady=1, columnspan=1, rowspan=1)
            if self.ControlType_StartingValueList[MotorIndex] == "CurrentBasedPositionControl":
                self.ControlTypeRadiobutton_CurrentBasedPositionControl[MotorIndex].select()
                #self.ControlTypeRadiobutton_CurrentBasedPositionControl[MotorIndex].invoke()
            ###########################################################
            
            ###########################################################
            self.ControlTypeRadiobutton_PWMcontrol.append(Radiobutton(self.myFrame,
                                                          text="PWMcontrol",
                                                          state="normal",
                                                          width=15,
                                                          anchor="w",
                                                          variable=self.ControlTypeRadiobutton_SelectionVar[MotorIndex],
                                                          value="PWMcontrol",
                                                          command=lambda name=MotorIndex: self.ControlTypeRadiobutton_Response(name)))
            self.ControlTypeRadiobutton_PWMcontrol[MotorIndex].grid(row=4 + MotorIndex*2, column=10, padx=1, pady=1, columnspan=1, rowspan=1)
            if self.ControlType_StartingValueList[MotorIndex] == "PWMcontrol":
                self.ControlTypeRadiobutton_PWMcontrol[MotorIndex].select()
                #self.ControlTypeRadiobutton_PWMcontrol[MotorIndex].invoke()
            ###########################################################

        #################################################
        #################################################
        #################################################

        ########################
        self.PrintToGui_Label = Label(self.myFrame, text="PrintToGui_Label", width=75)
        if self.EnableInternal_MyPrint_Flag == 1:
            self.PrintToGui_Label.grid(row=0, column=2, padx=1, pady=1, columnspan=1, rowspan=10)
        ########################

        ########################
        if self.RootIsOwnedExternallyFlag == 0: #This class object owns root and must handle it properly
            self.root.protocol("WM_DELETE_WINDOW", self.ExitProgram_Callback)

            self.root.after(self.GUI_RootAfterCallbackInterval_Milliseconds, self.GUI_update_clock)
            self.GUI_ready_to_be_updated_flag = 1
            self.root.mainloop()
        else:
            self.GUI_ready_to_be_updated_flag = 1
        ########################

        ########################
        if self.RootIsOwnedExternallyFlag == 0: #This class object owns root and must handle it properly
            self.root.quit()  # Stop the GUI thread, MUST BE CALLED FROM GUI_Thread
            self.root.destroy()  # Close down the GUI thread, MUST BE CALLED FROM GUI_Thread
        ########################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    def ControlTypeRadiobutton_Response(self, name):

        MotorNumber = int(name)

        self.ControlType_TO_BE_SET[MotorNumber] = self.ControlTypeRadiobutton_SelectionVar[MotorNumber].get()
        self.ControlType_NEEDS_TO_BE_CHANGED_FLAG[MotorNumber] = 1
        self.MyPrint_WithoutLogFile("Motor " + str(MotorNumber) + " ControlType set to: " + self.ControlType_TO_BE_SET[MotorNumber])
    ##########################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def ToggleMinMax_ButtonResponse(self, event = None, name = "default"):

        MotorNumber = int(name)

        if self.ToggleMinMax_state[MotorNumber] == -1:
            self.ToggleMinMax_TO_BE_SET[MotorNumber] = 0
        elif self.ToggleMinMax_state[MotorNumber] == 0:
            self.ToggleMinMax_TO_BE_SET[MotorNumber] = 1
        elif self.ToggleMinMax_state[MotorNumber] == 1:
            self.ToggleMinMax_TO_BE_SET[MotorNumber] = -1
            
        self.ToggleMinMax_NeedsToTakePlaceFlag[MotorNumber] = 1

        self.MyPrint_WithoutLogFile("ToggleMinMax_ButtonResponse event fired for motor: " + str(MotorNumber) + ", state = " + str(self.ToggleMinMax_TO_BE_SET[MotorNumber]))
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def ResetSerial_ButtonResponse(self, event = None, name = "default"):

        MotorNumber = int(name)

        self.ResetSerial_NeedsToTakePlaceFlag[MotorNumber] = 1

        self.MyPrint_WithoutLogFile("Reboot Button event fired for motor : " + str(MotorNumber))
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def Reboot_ButtonResponse(self, event = None, name = "default"):

        MotorNumber = int(name)

        self.Reboot_NeedsToTakePlaceFlag[MotorNumber] = 1

        self.MyPrint_WithoutLogFile("Reboot Button event fired for motor : " + str(MotorNumber))
    #######################################################################################################################
    #######################################################################################################################

    '''
    #######################################################################################################################
    #######################################################################################################################
    def MinPositionLimit_Entry_Response(self, event = None, name = "default"):

        MotorNumber = int(name)
        MinPositionLimit_temp = float(self.MinPositionLimit_StringVar[MotorNumber].get())
        self.MinPositionLimit[MotorNumber] = self.limitTextEntryInput(0.0, 1023.0, MinPositionLimit_temp, self.MinPositionLimit_StringVar[MotorNumber])

        self.MinPositionLimit_TO_BE_SET[MotorNumber] = self.MinPositionLimit[MotorNumber]

        self.MinPositionLimit_NeedsToBeChangedFlag[MotorNumber] = 1

        self.MyPrint_WithoutLogFile("New MinPositionLimit: " + str(self.MinPositionLimit[MotorNumber]))
    #######################################################################################################################
    #######################################################################################################################

    #######################################################################################################################
    #######################################################################################################################
    def MaxPositionLimit_Entry_Response(self, event = None, name = "default"):

        MotorNumber = int(name)
        MaxPositionLimit_temp = float(self.MaxPositionLimit_StringVar[MotorNumber].get())
        self.MaxPositionLimit[MotorNumber] = self.limitTextEntryInput(0.0, 1023.0, MaxPositionLimit_temp, self.MaxPositionLimit_StringVar[MotorNumber])

        self.MaxPositionLimit_TO_BE_SET[MotorNumber] = self.MaxPositionLimit[MotorNumber]

        self.MaxPositionLimit_NeedsToBeChangedFlag[MotorNumber] = 1

        self.MyPrint_WithoutLogFile("New MaxPositionLimit: " + str(self.MaxPositionLimit[MotorNumber]))
    #######################################################################################################################
    #######################################################################################################################
    '''

    '''
    #######################################################################################################################
    #######################################################################################################################
    def MaxPWM_DynamixelUnits_Entry_Response(self, event = None, name = "default"):

        MotorNumber = int(name)
        MaxPWM_DynamixelUnits_temp = float(self.MaxPWM_DynamixelUnits_StringVar[MotorNumber].get())
        self.MaxPWM_DynamixelUnits[MotorNumber] = self.limitTextEntryInput(0.0, 885.0, MaxPWM_DynamixelUnits_temp, self.MaxPWM_DynamixelUnits_StringVar[MotorNumber])

        self.MaxPWM_DynamixelUnits_TO_BE_SET[MotorNumber] = self.MaxPWM_DynamixelUnits[MotorNumber]

        self.MaxPWM_DynamixelUnits_NeedsToBeChangedFlag[MotorNumber] = 1

        self.MyPrint_WithoutLogFile("New MaxPWM_DynamixelUnits: " + str(self.MaxPWM_DynamixelUnits[MotorNumber]))
    #######################################################################################################################
    #######################################################################################################################
    '''

    ##########################################################################################################
    ##########################################################################################################
    def GUI_update_clock(self):

        #######################################################
        #######################################################
        #######################################################
        if self.USE_GUI_FLAG == 1 and self.EXIT_PROGRAM_FLAG == 0:

            #######################################################
            #######################################################
            if self.GUI_ready_to_be_updated_flag == 1:

                #######################################################
                self.device_info_label["text"] = "NameForU2D2UserProvided: " + str(self.NameForU2D2UserProvided) + \
                                        "\nModelNumber: " + str(self.ModelNumber_Received) + \
                                        "\nFWversion: " + str(self.FWversion_Received) + \
                                        "\nID: " + str(self.ID_Received) + \
                                        "\nReturnDelayTimeMicroSeconds: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.ReturnDelayTimeMicroSeconds_Received) + \
                                        "\nTemperatureHighestLimit_Received: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.TemperatureHighestLimit_Received) + \
                                        "\nVoltageLowestLimit: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.VoltageLowestLimit_Received) + \
                                        "\nVoltageHighesttLimit: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.VoltageLowestLimit_Received)
                #######################################################

                #######################################################
                self.data_label["text"] = "ControlType: " + str(self.ControlType) + \
                                        "\nOperatingModeReceived_int: " + str(self.OperatingModeReceived_int) + \
                                        "\nOperatingModeReceived_string: " + str(self.OperatingModeReceived_string) + \
                                        "\nPWM: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.PWMReceived_DynamixelUnits) + \
                                        "\nCurrent DU: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.CurrentReceived_DynamixelUnits) + \
                                        "\nCurrent Amps: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.CurrentReceived_Amps) + \
                                        "\nCurrent %: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.CurrentReceived_Percent0to1) + \
                                        "\nVelocity: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.VelocityReceived_DynamixelUnits) + \
                                        "\nPos: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.PositionReceived_DynamixelUnits) + \
                                        "\nPosDeg: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.PositionReceived_Deg) + \
                                        "\nVoltage: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.VoltageReceived_DynamixelUnits) + \
                                        "\nTemperature: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.TemperatureReceived_DynamixelUnits) + \
                                        "\nCWangleLimit: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.MinPositionLimitReceived) + \
                                        "\nCCWangleLimit: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.MaxPositionLimitReceived) + \
                                        "\nEngaged: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.EngagedState) + \
                                        "\nLEDstate: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.LEDstate) + \
                                        "\nRealTimeTicksMillisec: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.RealTimeTicksMillisec) + \
                                        "\nData Frequency RealTimeTicksMillisec: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.DataStreamingFrequency_RealTimeTicksMillisecFromDynamixel) + \
                                        "\n" +\
                                        "\nData Frequency Python Calculated: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.DataStreamingFrequency_CalculatedFromMainThread) +\
                                        "\nTime: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.CurrentTime_CalculatedFromMainThread)
            #######################################################

                #######################################################
                self.error_label["text"] = "ErrorFlag_BYTE: " + str(self.ErrorFlag_BYTE) + \
                                        "\nErrorFlag_Overload_Received: " + str(self.ErrorFlag_Overload_Received) + \
                                        "\nErrorFlag_ElectricalShock_Received: " + str(self.ErrorFlag_ElectricalShock_Received) + \
                                        "\nErrorFlag_MotorEncoder_Received: " + str(self.ErrorFlag_MotorEncoder_Received) + \
                                        "\nErrorFlag_Overheating_Received: " + str(self.ErrorFlag_Overheating_Received) + \
                                        "\nErrorFlag_InputVoltage_Received: " + str(self.ErrorFlag_InputVoltage_Received)

                #######################################################

                #######################################################
                #######################################################
                for MotorIndex in range(0, self.NumberOfMotors):

                    #########################################################
                    if self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] == 1:
                        self.Position_DynamixelUnits_Scale[MotorIndex].set(self.Position_DynamixelUnits_TO_BE_SET[MotorIndex])
                        self.Position_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 0
                    #########################################################

                    #########################################################
                    if self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] == 1:
                        self.Velocity_DynamixelUnits_Scale[MotorIndex].set(self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex])
                        self.Velocity_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 0
                    #########################################################

                    #########################################################
                    if self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] == 1:
                        self.Current_DynamixelUnits_Scale[MotorIndex].set(self.Current_DynamixelUnits_TO_BE_SET[MotorIndex])
                        self.Current_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 0
                    #########################################################
                    
                    #########################################################
                    if self.PWM_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] == 1:
                        self.PWM_DynamixelUnits_Scale[MotorIndex].set(self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex])
                        self.PWM_DynamixelUnits_GUI_NeedsToBeChangedFlag[MotorIndex] = 0
                    #########################################################

                    #########################################################
                    if self.ControlType_GUI_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] == 1:

                        if self.ControlType_TO_BE_SET[MotorIndex] == "CurrentControl":
                            self.ControlTypeRadiobutton_CurrentControl[MotorIndex].select()

                        elif self.ControlType_TO_BE_SET[MotorIndex] == "VelocityControl":
                            self.ControlTypeRadiobutton_VelocityControl[MotorIndex].select()

                        elif self.ControlType_TO_BE_SET[MotorIndex] == "PositionControl":
                            self.ControlTypeRadiobutton_PositionControl[MotorIndex].select()

                        elif self.ControlType_TO_BE_SET[MotorIndex] == "ExtendedPositionControlMultiTurnControl":
                            self.ControlTypeRadiobutton_ExtendedPositionControlMultiTurn[MotorIndex].select()

                        elif self.ControlType_TO_BE_SET[MotorIndex] == "CurrentBasedPositionControl":
                            self.ControlTypeRadiobutton_CurrentBasedPositionControl[MotorIndex].select()

                        elif self.ControlType_TO_BE_SET[MotorIndex] == "PWMcontrol":
                            self.ControlTypeRadiobutton_PWMcontrol[MotorIndex].select()

                        self.ControlType_GUI_NEEDS_TO_BE_CHANGED_FLAG[MotorIndex] = 0
                    #########################################################

                    #########################################################
                    if self.EngagedState_GUI_NeedsToBeChangedFlag[MotorIndex] == 1:

                        if self.EngagedState_TO_BE_SET[MotorIndex] == 1: #This actually changes how the widget looks
                            self.EngagedState_Checkbutton[MotorIndex].select()
                        elif self.EngagedState_TO_BE_SET[MotorIndex] == 0:
                            self.EngagedState_Checkbutton[MotorIndex].deselect()

                        self.EngagedState_GUI_NeedsToBeChangedFlag[MotorIndex] = 0
                    #########################################################

                    #########################################################
                    if self.LEDstate_GUI_NeedsToBeChangedFlag[MotorIndex] == 1:

                        if self.LEDstate_TO_BE_SET[MotorIndex] == 1: #This actually changes how the widget looks
                            self.LEDstate_Checkbutton[MotorIndex].select()
                        elif self.LEDstate_TO_BE_SET[MotorIndex] == 0:
                            self.LEDstate_Checkbutton[MotorIndex].deselect()

                        self.LEDstate_GUI_NeedsToBeChangedFlag[MotorIndex] = 0
                    #########################################################

                    #########################################################
                    if self.EngagedState[MotorIndex] == 1:
                        self.Position_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightGreenColor
                        self.Velocity_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightGreenColor
                        self.Current_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightGreenColor
                        self.PWM_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightGreenColor
                    else:
                        self.Position_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightRedColor
                        self.Velocity_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightRedColor
                        self.Current_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightRedColor
                        self.PWM_DynamixelUnits_Scale[MotorIndex]["troughcolor"] = self.TKinter_LightRedColor
                    #########################################################

                #######################################################
                #######################################################

                #######################################################
                #######################################################
                self.PrintToGui_Label.config(text = self.PrintToGui_Label_TextInput_Str)
                #######################################################
                #######################################################

            #######################################################
            #######################################################
            if self.RootIsOwnedExternallyFlag == 0:  # This class object owns root and must handle it properly
                self.root.after(self.GUI_RootAfterCallbackInterval_Milliseconds, self.GUI_update_clock)
            #######################################################
            #######################################################

        #######################################################
        #######################################################
        #######################################################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self, input, number_of_leading_numbers=4, number_of_decimal_places=3):
        #print("ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput input: " + str(input))

        if type(input) == "str":
            return "-1111111111"

        IsListFlag = self.IsInputList(input)

        if IsListFlag == 0:
            float_number_list = [input]
        else:
            float_number_list = list(input)

        float_number_list_as_strings = []
        for element in float_number_list:
            try:
                element = float(element)
                prefix_string = "{:." + str(number_of_decimal_places) + "f}"
                element_as_string = prefix_string.format(element)
                float_number_list_as_strings.append(element_as_string)
            except:
                print(self.TellWhichFileWereIn() + ": ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput ERROR: " + str(element) + " cannot be turned into a float")
                return "-1111111111"

        StringToReturn = ""
        if IsListFlag == 0:
            StringToReturn = float_number_list_as_strings[0].zfill(number_of_leading_numbers + number_of_decimal_places + 1 + 1)  # +1 for sign, +1 for decimal place
        else:
            StringToReturn = "["
            for index, StringElement in enumerate(float_number_list_as_strings):
                if float_number_list[index] >= 0:
                    StringElement = "+" + StringElement  # So that our strings always have either + or - signs to maintain the same string length

                StringElement = StringElement.zfill(number_of_leading_numbers + number_of_decimal_places + 1 + 1)  # +1 for sign, +1 for decimal place

                if index != len(float_number_list_as_strings) - 1:
                    StringToReturn = StringToReturn + StringElement + ", "
                else:
                    StringToReturn = StringToReturn + StringElement + "]"

        return StringToReturn
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def MyPrint_WithoutLogFile(self, input_string):

        input_string = str(input_string)

        if input_string != "":

            #input_string = input_string.replace("\n", "").replace("\r", "")

            ################################ Write to console
            # Some people said that print crashed for pyinstaller-built-applications and that sys.stdout.write fixed this.
            # http://stackoverflow.com/questions/13429924/pyinstaller-packaged-application-works-fine-in-console-mode-crashes-in-window-m
            if self.PrintToConsoleFlag == 1:
                sys.stdout.write(input_string + "\n")
            ################################

            ################################ Write to GUI
            self.PrintToGui_Label_TextInputHistory_List.append(self.PrintToGui_Label_TextInputHistory_List.pop(0)) #Shift the list
            self.PrintToGui_Label_TextInputHistory_List[-1] = str(input_string) #Add the latest value

            self.PrintToGui_Label_TextInput_Str = ""
            for Counter, Line in enumerate(self.PrintToGui_Label_TextInputHistory_List):
                self.PrintToGui_Label_TextInput_Str = self.PrintToGui_Label_TextInput_Str + Line

                if Counter < len(self.PrintToGui_Label_TextInputHistory_List) - 1:
                    self.PrintToGui_Label_TextInput_Str = self.PrintToGui_Label_TextInput_Str + "\n"
            ################################

    ##########################################################################################################
    ##########################################################################################################

    #######################################################################################################################
    def limitNumber(self, min_val, max_val, test_val):

        if test_val > max_val:
            test_val = max_val

        elif test_val < min_val:
            test_val = min_val

        else:
            dummy_var = 0

        return test_val
    #######################################################################################################################

    #######################################################################################################################
    def limitTextEntryInput(self, min_val, max_val, test_val, TextEntryObject):

        test_val = float(test_val)  # MUST HAVE THIS LINE TO CATCH STRINGS PASSED INTO THE FUNCTION

        if test_val > max_val:
            test_val = max_val
        elif test_val < min_val:
            test_val = min_val
        else:
            test_val = test_val

        if TextEntryObject != "":
            if isinstance(TextEntryObject, list) == 1:  # Check if the input 'TextEntryObject' is a list or not
                TextEntryObject[0].set(str(test_val))  # Reset the text, overwriting the bad value that was entered.
            else:
                TextEntryObject.set(str(test_val))  # Reset the text, overwriting the bad value that was entered.

        return test_val
    #######################################################################################################################

    #######################################################################################################################
    def Position_DynamixelUnits_ScaleResponse(self, event, name):

        MotorIndex = name
        self.Position_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Position_DynamixelUnits_ScaleValue[MotorIndex].get()
        self.Position_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        #self.MyPrint_WithoutLogFile("ScaleResponse: Position set to: " + str(self.Position_DynamixelUnits_TO_BE_SET[MotorIndex]) + " on motor " + str(MotorIndex))
    #######################################################################################################################

    #######################################################################################################################
    def Velocity_DynamixelUnits_ScaleResponse(self, event, name):

        MotorIndex = name
        self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Velocity_DynamixelUnits_ScaleValue[MotorIndex].get()
        self.Velocity_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        #self.MyPrint_WithoutLogFile("ScaleResponse: Velocity set to: " + str(self.Velocity_DynamixelUnits_TO_BE_SET[MotorIndex]) + " on motor " + str(MotorIndex))
    #######################################################################################################################

    #######################################################################################################################
    def Current_DynamixelUnits_ScaleResponse(self, event, name):

        MotorIndex = name
        self.Current_DynamixelUnits_TO_BE_SET[MotorIndex] = self.Current_DynamixelUnits_ScaleValue[MotorIndex].get()
        self.Current_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        #self.MyPrint_WithoutLogFile("ScaleResponse: Current set to: " + str(self.Current_DynamixelUnits_TO_BE_SET[MotorIndex]) + " on motor " + str(MotorIndex))
    #######################################################################################################################
    
    #######################################################################################################################
    def PWM_DynamixelUnits_ScaleResponse(self, event, name):

        MotorIndex = name
        self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex] = self.PWM_DynamixelUnits_ScaleValue[MotorIndex].get()
        self.PWM_DynamixelUnits_NeedsToBeChangedFlag[MotorIndex] = 1

        #self.MyPrint_WithoutLogFile("ScaleResponse: PWM set to: " + str(self.PWM_DynamixelUnits_TO_BE_SET[MotorIndex]) + " on motor " + str(MotorIndex))
    #######################################################################################################################

    #######################################################################################################################
    def EngagedState_CheckbuttonResponse(self, event, name):

        MotorIndex = name
        temp_value = self.EngagedState_Checkbutton_Value[MotorIndex].get()

        if temp_value == 0:
            self.EngagedState_TO_BE_SET[MotorIndex] = 1 ########## This reversal is needed for the variable state to match the checked state, but we don't know why
        elif temp_value == 1:
            self.EngagedState_TO_BE_SET[MotorIndex] = 0

        self.EngagedState_NeedsToBeChangedFlag[MotorIndex] = 1
        self.MyPrint_WithoutLogFile("EngagedState_CheckbuttonResponse: EngagedState changed to " + str(self.EngagedState_TO_BE_SET[MotorIndex]) + " on motor " + str(MotorIndex))
    #######################################################################################################################

    #######################################################################################################################
    def LEDstate_CheckbuttonResponse(self, event, name):

        MotorIndex = name
        temp_value = self.LEDstate_Checkbutton_Value[MotorIndex].get()

        if temp_value == 0:
            self.LEDstate_TO_BE_SET[MotorIndex] = 1 ########## This reversal is needed for the variable state to match the checked state, but we don't know why
        elif temp_value == 1:
            self.LEDstate_TO_BE_SET[MotorIndex] = 0

        self.LEDstate_NeedsToBeChangedFlag[MotorIndex] = 1
        #self.MyPrint_WithoutLogFile("LEDstate_CheckbuttonResponse: LEDstate changed to " + str(self.LEDstate_TO_BE_SET[MotorIndex]) + " on motor " + str(MotorIndex))
    #######################################################################################################################

    #######################################################################################################################
    def DisengageAllMotorsButtonResponse(self):

        for MotorIndex in range(0, len(self.EngagedState_TO_BE_SET)):
            if self.MotorType_StringList[MotorIndex] != "None":
                #print("DisengageAllMotorsButtonResponse MotorIndex: " + str(MotorIndex))
                self.EngagedState_TO_BE_SET[MotorIndex] = 0
                self.EngagedState_NeedsToBeChangedFlag[MotorIndex] = 1

        self.MyPrint_WithoutLogFile("DisengageAllMotorsButtonResponse")
    #######################################################################################################################

    #######################################################################################################################
    def EngageAllMotorsButtonResponse(self):

        for MotorIndex in range(0, len(self.EngagedState_TO_BE_SET)):
            if self.MotorType_StringList[MotorIndex]  != "None":
                #print("EngageAllMotorsButtonResponse MotorIndex: " + str(MotorIndex))
                self.EngagedState_TO_BE_SET[MotorIndex] = 1
                self.EngagedState_NeedsToBeChangedFlag[MotorIndex] = 1

        self.MyPrint_WithoutLogFile("EngageAllMotorsButtonResponse")
    #######################################################################################################################