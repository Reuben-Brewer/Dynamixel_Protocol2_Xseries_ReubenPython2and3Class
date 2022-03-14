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

from Dynamixel_Protocol2_Xseries_ReubenPython2and3Class import *
from MyPrint_ReubenPython2and3Class import *

import os, sys, platform
import time, datetime
import threading
import collections

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
    from builtins import raw_input as input
else:
    from future.builtins import input as input #"sudo pip3 install future" (Python 3) AND "sudo pip install future" (Python 2)
###############

###############
import platform
if platform.system() == "Windows":
    import ctypes
    winmm = ctypes.WinDLL('winmm')
    winmm.timeBeginPeriod(1) #Set minimum timer resolution to 1ms so that time.sleep(0.001) behaves properly.
###############

##########################################################################################################
##########################################################################################################
def getPreciseSecondsTimeStampString():
    ts = time.time()

    return ts
##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def TestButtonResponse():
    global MyPrint_ReubenPython2and3ClassObject
    global USE_MYPRINT_FLAG

    if USE_MYPRINT_FLAG == 1:
        MyPrint_ReubenPython2and3ClassObject.my_print("Test Button was Pressed!")
    else:
        print("Test Button was Pressed!")
##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def GUI_update_clock():
    global root
    global EXIT_PROGRAM_FLAG
    global GUI_RootAfterCallbackInterval_Milliseconds
    global USE_GUI_FLAG

    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject
    global DYNAMIXEL_X_OPEN_FLAG
    global SHOW_IN_GUI_DYNAMIXEL_X_FLAG

    global MyPrint_ReubenPython2and3ClassObject
    global MYPRINT_OPEN_FLAG
    global SHOW_IN_GUI_MYPRINT_FLAG

    if USE_GUI_FLAG == 1:
        if EXIT_PROGRAM_FLAG == 0:
            #########################################################
            #########################################################

            #########################################################
            if DYNAMIXEL_X_OPEN_FLAG == 1 and SHOW_IN_GUI_DYNAMIXEL_X_FLAG == 1:
                Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.GUI_update_clock()
            #########################################################

            #########################################################
            if MYPRINT_OPEN_FLAG == 1 and SHOW_IN_GUI_MYPRINT_FLAG == 1:
                MyPrint_ReubenPython2and3ClassObject.GUI_update_clock()
            #########################################################

            root.after(GUI_RootAfterCallbackInterval_Milliseconds, GUI_update_clock)
            #########################################################
            #########################################################

##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def ExitProgram_Callback():
    global EXIT_PROGRAM_FLAG

    print("ExitProgram_Callback event fired!")

    EXIT_PROGRAM_FLAG = 1
##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def GUI_Thread():
    global root
    global GUI_RootAfterCallbackInterval_Milliseconds

    ################################################# KEY GUI LINE
    #################################################
    root = Tk()
    #################################################
    #################################################

    #################################################
    TestButton = Button(root, text='Test Button', state="normal", width=20, command=lambda i=1: TestButtonResponse())
    TestButton.grid(row=0, column=0, padx=5, pady=1)
    #################################################

    #################################################
    root.protocol("WM_DELETE_WINDOW", ExitProgram_Callback)  # Set the callback function for when the window's closed.
    root.after(GUI_RootAfterCallbackInterval_Milliseconds, GUI_update_clock)
    root.mainloop()
    #################################################

    #################################################
    root.quit() #Stop the GUI thread, MUST BE CALLED FROM GUI_Thread
    root.destroy() #Close down the GUI thread, MUST BE CALLED FROM GUI_Thread
    #################################################

##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
if __name__ == '__main__':

    #################################################
    #################################################
    global my_platform

    if platform.system() == "Linux":

        if "raspberrypi" in platform.uname():  # os.uname() doesn't work in windows
            my_platform = "pi"
        else:
            my_platform = "linux"

    elif platform.system() == "Windows":
        my_platform = "windows"

    elif platform.system() == "Darwin":
        my_platform = "mac"

    else:
        my_platform = "other"

    print("The OS platform is: " + my_platform)
    #################################################
    #################################################

    #################################################
    #################################################
    global USE_GUI_FLAG
    USE_GUI_FLAG = 1

    global USE_DYNAMIXEL_X_FLAG
    USE_DYNAMIXEL_X_FLAG = 1
    
    global USE_MYPRINT_FLAG
    USE_MYPRINT_FLAG = 1
    
    global USE_DYNAMIXEL_POSITION_CONTROL_FLAG
    USE_DYNAMIXEL_POSITION_CONTROL_FLAG = 1 #SET TO 0 FOR VELOCITY CONTROL

    global USE_DYNAMIXEL_SINUSOIDAL_INPUT_FLAG
    USE_DYNAMIXEL_SINUSOIDAL_INPUT_FLAG = 1
    #################################################
    #################################################

    #################################################
    #################################################
    global SHOW_IN_GUI_DYNAMIXEL_X_FLAG
    SHOW_IN_GUI_DYNAMIXEL_X_FLAG = 1
    
    global SHOW_IN_GUI_MYPRINT_FLAG
    SHOW_IN_GUI_MYPRINT_FLAG = 1
    #################################################
    #################################################

    #################################################
    #################################################
    global GUI_ROW_DYNAMIXEL_X
    global GUI_COLUMN_DYNAMIXEL_X
    global GUI_PADX_DYNAMIXEL_X
    global GUI_PADY_DYNAMIXEL_X
    global GUI_ROWSPAN_DYNAMIXEL_X
    global GUI_COLUMNSPAN_DYNAMIXEL_X
    GUI_ROW_DYNAMIXEL_X = 0

    GUI_COLUMN_DYNAMIXEL_X = 0
    GUI_PADX_DYNAMIXEL_X = 1
    GUI_PADY_DYNAMIXEL_X = 10
    GUI_ROWSPAN_DYNAMIXEL_X = 1
    GUI_COLUMNSPAN_DYNAMIXEL_X = 1
    
    global GUI_ROW_MYPRINT
    global GUI_COLUMN_MYPRINT
    global GUI_PADX_MYPRINT
    global GUI_PADY_MYPRINT
    global GUI_ROWSPAN_MYPRINT
    global GUI_COLUMNSPAN_MYPRINT
    GUI_ROW_MYPRINT = 1

    GUI_COLUMN_MYPRINT = 0
    GUI_PADX_MYPRINT = 1
    GUI_PADY_MYPRINT = 10
    GUI_ROWSPAN_MYPRINT = 1
    GUI_COLUMNSPAN_MYPRINT = 1
    #################################################
    #################################################

    #################################################
    #################################################
    global EXIT_PROGRAM_FLAG
    EXIT_PROGRAM_FLAG = 0

    global CurrentTime_MainLoopThread
    CurrentTime_MainLoopThread = -11111.0

    global StartingTime_MainLoopThread
    StartingTime_MainLoopThread = -11111.0

    global SINUSOIDAL_MOTION_INPUT_ROMtestTimeToPeakAngle
    SINUSOIDAL_MOTION_INPUT_ROMtestTimeToPeakAngle = 2.0

    global SINUSOIDAL_MOTION_INPUT_MinValue_PositionControl
    SINUSOIDAL_MOTION_INPUT_MinValue_PositionControl = 0.0

    global SINUSOIDAL_MOTION_INPUT_MaxValue_PositionControl
    SINUSOIDAL_MOTION_INPUT_MaxValue_PositionControl = 90.0

    global SINUSOIDAL_MOTION_INPUT_MinValue_VelocityControl
    SINUSOIDAL_MOTION_INPUT_MinValue_VelocityControl = -1.0

    global SINUSOIDAL_MOTION_INPUT_MaxValue_VelocityControl
    SINUSOIDAL_MOTION_INPUT_MaxValue_VelocityControl = 1.0

    global root

    global GUI_RootAfterCallbackInterval_Milliseconds
    GUI_RootAfterCallbackInterval_Milliseconds = 30
    #################################################
    #################################################

    #################################################
    #################################################
    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject

    global DYNAMIXEL_X_OPEN_FLAG
    DYNAMIXEL_X_OPEN_FLAG = -1

    global DynamixelList_TestChannelsList
    DynamixelList_TestChannelsList = [0] #Set this list to whichever motor ID's you want to test.

    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict

    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageCounter
    Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageCounter =  -11111.0

    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageTimeSeconds
    Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageTimeSeconds = -11111.0

    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageTopic
    Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageTopic = ""

    global Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageData
    Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageData = ""
    #################################################
    #################################################

    #################################################
    #################################################
    global MyPrint_ReubenPython2and3ClassObject

    global MYPRINT_OPEN_FLAG
    MYPRINT_OPEN_FLAG = -1
    #################################################
    #################################################

    #################################################  KEY GUI LINE
    #################################################
    if USE_GUI_FLAG == 1:
        print("Starting GUI thread...")
        GUI_Thread_ThreadingObject = threading.Thread(target=GUI_Thread)
        GUI_Thread_ThreadingObject.setDaemon(True) #Should mean that the GUI thread is destroyed automatically when the main thread is destroyed.
        GUI_Thread_ThreadingObject.start()
        time.sleep(0.5)  #Allow enough time for 'root' to be created that we can then pass it into other classes.
    else:
        root = None
    #################################################
    #################################################

    #################################################
    #################################################
    global DYNAMIXEL_X_GUIparametersDict
    DYNAMIXEL_X_GUIparametersDict = dict([("USE_GUI_FLAG", USE_GUI_FLAG and SHOW_IN_GUI_DYNAMIXEL_X_FLAG),
                                    ("root", root),
                                    ("EnableInternal_MyPrint_Flag", 1),
                                    ("NumberOfPrintLines", 10),
                                    ("UseBorderAroundThisGuiObjectFlag", 0),
                                    ("GUI_ROW", GUI_ROW_DYNAMIXEL_X),
                                    ("GUI_COLUMN", GUI_COLUMN_DYNAMIXEL_X),
                                    ("GUI_PADX", GUI_PADX_DYNAMIXEL_X),
                                    ("GUI_PADY", GUI_PADY_DYNAMIXEL_X),
                                    ("GUI_ROWSPAN", GUI_ROWSPAN_DYNAMIXEL_X),
                                    ("GUI_COLUMNSPAN", GUI_COLUMNSPAN_DYNAMIXEL_X)])

    global DYNAMIXEL_X_setup_dict
    DYNAMIXEL_X_setup_dict = dict([("SerialNumber", "FT3M9STOA"), #Change to the serial number of your unique device
                                    ("NameForU2D2UserProvided", "Example Name U2D2"),
                                    ("SerialBaudRate", 4000000),
                                    ("ENABLE_GETS", 1),
                                    ("ENABLE_SETS", 1),
                                    ("MainThread_TimeToSleepEachLoop", 0.002),
                                    ("MotorType_StringList", ["XM540-W270-R"]*len(DynamixelList_TestChannelsList)), #EACH INPUT LIST MUST BE THE SAME LENGTH AS NUMBER OF MOTORS.
                                    ("ControlType_StartingValueList", ["CurrentBasedPositionControl"]*len(DynamixelList_TestChannelsList)), #MOTOR ID'S MUST BE IN ORDER FROM 0 T0 (NumberOfMotors - 1) (E.G. FOR 3 MOTORS, THE ID'S WOULD BE 0, 1, AND 2).
                                    ("Position_Deg_StartingValueList", [150.0]*len(DynamixelList_TestChannelsList)),
                                    ("Position_Deg_min", [0.0]*len(DynamixelList_TestChannelsList)),
                                    ("Position_Deg_max", [300.0]*len(DynamixelList_TestChannelsList)),
                                    ("Current_Percent0to1_max", [0.5]*len(DynamixelList_TestChannelsList)),
                                    ("StartEngagedFlag", [1]*len(DynamixelList_TestChannelsList)),
                                    ("GUIparametersDict", DYNAMIXEL_X_GUIparametersDict)])

                            #("RxThread_TimeToSleepEachLoop", 0.001),
                            #("TxThread_TimeToSleepEachLoop", 0.001),
                            #("RxMessage_Queue_MaxSize", 1000),
                            #("TxMessage_Queue_MaxSize", 1000)])


    if USE_DYNAMIXEL_X_FLAG == 1:
        try:
            Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject = Dynamixel_Protocol2_Xseries_ReubenPython2and3Class(DYNAMIXEL_X_setup_dict)
            time.sleep(0.25)
            DYNAMIXEL_X_OPEN_FLAG = Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.OBJECT_CREATED_SUCCESSFULLY_FLAG

        except:
            exceptions = sys.exc_info()[0]
            print("Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject, exceptions: %s" % exceptions)
            traceback.print_exc()
    #################################################
    #################################################

    #################################################
    #################################################
    if USE_MYPRINT_FLAG == 1:

        MyPrint_ReubenPython2and3ClassObject_GUIparametersDict = dict([("USE_GUI_FLAG", USE_GUI_FLAG and SHOW_IN_GUI_MYPRINT_FLAG),
                                                                        ("root", root),
                                                                        ("UseBorderAroundThisGuiObjectFlag", 0),
                                                                        ("GUI_ROW", GUI_ROW_MYPRINT),
                                                                        ("GUI_COLUMN", GUI_COLUMN_MYPRINT),
                                                                        ("GUI_PADX", GUI_PADX_MYPRINT),
                                                                        ("GUI_PADY", GUI_PADY_MYPRINT),
                                                                        ("GUI_ROWSPAN", GUI_ROWSPAN_MYPRINT),
                                                                        ("GUI_COLUMNSPAN", GUI_COLUMNSPAN_MYPRINT)])

        MyPrint_ReubenPython2and3ClassObject_setup_dict = dict([("NumberOfPrintLines", 10),
                                                                ("WidthOfPrintingLabel", 200),
                                                                ("PrintToConsoleFlag", 1),
                                                                ("LogFileNameFullPath", os.getcwd() + "//TestLog.txt"),
                                                                ("GUIparametersDict", MyPrint_ReubenPython2and3ClassObject_GUIparametersDict)])

        try:
            MyPrint_ReubenPython2and3ClassObject = MyPrint_ReubenPython2and3Class(MyPrint_ReubenPython2and3ClassObject_setup_dict)
            time.sleep(0.25)
            MYPRINT_OPEN_FLAG = MyPrint_ReubenPython2and3ClassObject.OBJECT_CREATED_SUCCESSFULLY_FLAG

        except:
            exceptions = sys.exc_info()[0]
            print("MyPrint_ReubenPython2and3ClassObject __init__: Exceptions: %s" % exceptions)
            traceback.print_exc()
    #################################################
    #################################################

    #################################################
    #################################################
    if USE_MYPRINT_FLAG == 1 and MYPRINT_OPEN_FLAG != 1:
        print("Failed to open MyPrint_ReubenPython2and3ClassObject.")
        input("Press any key (and enter) to exit.")
        sys.exit()
    #################################################
    #################################################

    #################################################
    #################################################
    if USE_DYNAMIXEL_X_FLAG == 1 and DYNAMIXEL_X_OPEN_FLAG != 1:
        print("Failed to open Dynamixel_Protocol2_Xseries_ReubenPython2and3Class.")
        input("Press any key (and enter) to exit.")
        sys.exit()
    #################################################
    #################################################

    #################################################
    #################################################
    print("Starting main loop 'test_program_for_Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_WoVa.")
    StartingTime_MainLoopThread = getPreciseSecondsTimeStampString()

    while(EXIT_PROGRAM_FLAG == 0):

        ###################################################
        CurrentTime_MainLoopThread = getPreciseSecondsTimeStampString() - StartingTime_MainLoopThread
        ###################################################

        ###################################################
        if USE_DYNAMIXEL_X_FLAG == 1:

            ##################### GET's
            Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict = Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.GetMostRecentDataDict()

            if "RxMessageCounter" in Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict:
                print("Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict: " + str(Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict))
                Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageCounter = Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict["RxMessageCounter"]
                Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageTimeSeconds = Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict["RxMessageTimeSeconds"]
                Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageTopic = Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict["RxMessageTopic"]
                Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageData = Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict["RxMessageData"]

                if Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject_MostRecentRxMessageDict_RxMessageData.lower() == "ping":
                    Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.AddDataToBeSent(DYNAMIXEL_X_setup_dict["MQTT_Tx_topic_list"][0], "Received your message!", DYNAMIXEL_X_setup_dict["MQTT_Tx_QOS_list"][0])
            #####################

            ##################### SET's
            time_gain = math.pi / (2.0 * SINUSOIDAL_MOTION_INPUT_ROMtestTimeToPeakAngle)

            if USE_DYNAMIXEL_SINUSOIDAL_INPUT_FLAG == 1:

                if USE_DYNAMIXEL_POSITION_CONTROL_FLAG == 1:
                    SINUSOIDAL_INPUT_TO_COMMAND = (SINUSOIDAL_MOTION_INPUT_MaxValue_PositionControl + SINUSOIDAL_MOTION_INPUT_MinValue_PositionControl)/2.0 + 0.5*abs(SINUSOIDAL_MOTION_INPUT_MaxValue_PositionControl - SINUSOIDAL_MOTION_INPUT_MinValue_PositionControl)*math.sin(time_gain*CurrentTime_MainLoopThread)

                    for DynamixelChannel in range(0, len(DynamixelList_TestChannelsList)):
                        if DynamixelChannel in DynamixelList_TestChannelsList:
                            Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.SetPosition_FROM_EXTERNAL_PROGRAM(DynamixelChannel, SINUSOIDAL_INPUT_TO_COMMAND, "deg")

                else:
                    SINUSOIDAL_INPUT_TO_COMMAND = (SINUSOIDAL_MOTION_INPUT_MaxValue_VelocityControl + SINUSOIDAL_MOTION_INPUT_MinValue_VelocityControl)/2.0 + 0.5*abs(SINUSOIDAL_MOTION_INPUT_MaxValue_VelocityControl - SINUSOIDAL_MOTION_INPUT_MinValue_VelocityControl)*math.sin(time_gain*CurrentTime_MainLoopThread)

                    for DynamixelChannel in range(0, len(DynamixelList_TestChannelsList)):
                        if DynamixelChannel in DynamixelList_TestChannelsList:
                            Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.SetVelocity_FROM_EXTERNAL_PROGRAM(DynamixelChannel, SINUSOIDAL_INPUT_TO_COMMAND)
            #####################

        else:
            time.sleep(0.005)
        ###################################################

    #################################################
    #################################################

    ################################################# THIS IS THE EXIT ROUTINE!
    #################################################
    print("Exiting main program 'test_program_for_Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.")

    #################################################
    if DYNAMIXEL_X_OPEN_FLAG == 1:
        Dynamixel_Protocol2_Xseries_ReubenPython2and3ClassObject.ExitProgram_Callback()
    #################################################

    #################################################
    if MYPRINT_OPEN_FLAG == 1:
        MyPrint_ReubenPython2and3ClassObject.ExitProgram_Callback()
    #################################################

    #################################################
    #################################################

    ##########################################################################################################
    ##########################################################################################################