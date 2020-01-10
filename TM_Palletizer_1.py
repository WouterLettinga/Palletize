#included project libraries
from TM_Functions_1 import *
from Pallet_Build_1 import create_layer_Z

# included libraries
import time
import xmlrpc.client

# Set safe points
_safePoint = [447.66, 503.45, 668.45, 179.64, -1.06, 33.22]
_safePoint1 = [665.66, -156.17, 668.45, 179.64, -1.06, 33.22]

#Begin point of the pallet
Layer = 0
Number = 0
setlift = 0
layerchange = True

B = Box(GetBoxtype())

#Before starting the pallet go to the safepoint
safe_point(_safePoint)


#while ReadMemory(plc, 16, 0 ,S7WLByte) != 0:
while True:
    while (Layer <= (B.Layers - 1)):

        if Number >= len(create_layer_Z(0, 0)): #Check length with Dummy
            Layer += 1
            Number = 0
            setlift += 1
            layerchange = True
            print ("Layer: ", Layer)
            print ("Lift layer: ", setlift)
            print ("Layer change: ", layerchange)
#            if (Layer <= (B.Layers - 1)):
#                break

#        if (B.Height * Layer > 550 and layerchange == True):
#            print ("Layerchange: Going up")
#            liftkit_connect()
#            time.sleep(3)
#            print ("Goal hoogte: ", B.Height * setlift)
#            #print (Y.get_position())
#            hoogte = B.Height * setlift
#            Y.trigger_watchdog('move')
#            Y.move_to_remote_position(hoogte)
#            time.sleep(B.Height * 0.025)
#            print ("Eind hoogte: ", Y.get_position())
#            layerchange = False
#        elif (B.Height * Layer < 550 and layerchange == True):
#            print ("Layerchange: Going Down")
#            time.sleep(3)
#            print ("Goal hoogte: ", 0)
#            setlift = 0
#            if setlift * B.Height != 0:
#                liftkit_connect()
#                Y.trigger_watchdog('move')
#                Y.move_to_remote_position(0)
#                time.sleep(abs(Y.get_position()) * 0.025)
#            print ("Eind hoogte: ",Y.get_position())
#            layerchange = False
#
#        Y.com_stop()
#        WriteMemory(plc, 10, 0, S7WLByte, int(Number))
#        WriteMemory(plc, 14, 0, S7WLByte, int(Layer))

        change_base("RobotBase")
        safe_point(_safePoint)

        while True:
#            if ReadMemory(plc, 12, 0, S7WLByte) != 0: #PLC FLAG FOR GO!

                change_base('vision_Conveyer')
                pickup_point(Layer, setlift, B.Height)
######                Y.trigger_watchdog('running')
                change_base("RobotBase")
#                if mass_payload(B.Mass) > 2:
#                    print ("Faulty pick")
#                    safe_point(_safePoint)
#                    toggle_suck()
#                    continue

#                change_base("RobotBase")
                safe_point(_safePoint1)
                safe_point(_safePoint)

#                if mass_payload(B.Mass) == 2:
#                    print("Dropped while moving")
#                    safe_point(_safePoint)
#                    PTP([1168.83,333.68,-264.79,176.11,0.27,101.84])
#                    toggle_suck()
#                    continue

                change_base("vision_VisionBase")
                drop_point(create_layer_Z(Layer, setlift)[Number], Layer)  # Safe position above the drop-off ( Lets do it in a function)
                Number += 1
                break
    #print ("Finished Pallet: Disconnecting")
    #if (Layer + 1 == B.Layers):
    #    scriptExit()
    #    s.close()
    #    break
print ("Closed connection")
