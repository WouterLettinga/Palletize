from TM_Functions_1 import *

Start = [0.00, 0.00, 0.00, -179.64, -1.06, -95.31]

Size = [1200, 800, 2100]

P = Pallet(Start, Size)

B = Box(GetBoxtype())

#Box surface
def Box_Opp():
    return B.Width * B.Length

#Pattern surface 
def Pattern_Opp2():
    return (P.PalletWidth - 50) * B.Length

###################################################################################################################

# Calculation of the horizontal pattern
    
#Returns the amount of boxes that fit in the horizontal pattern
def Box_fit_Horizontal():
    return Pattern_Opp2() // Box_Opp()

#Returns the offset in the x-position to center the pattern
def Center_pallet_hor_xpos():
    return (P.PalletWidth - (Box_fit_Horizontal() * B.Width)) // 2

#Returns the offset in the y-position to center the pattern
def Center_pallet_hor_ypos():
    return (P.PalletLength - Box_fit_Vertical() * B.Width - B.Length) // 2

#Returns the x positions of the horizontal pattern
def Horizontal_xpos(x, off = 20):
    return  x * (B.Width + off) + 0.5 * B.Width + Center_pallet_hor_xpos() - 65 

#Returns the y positions of the horizontal pattern
def Horizontal_ypos(stackedLayer, off = 20):
    if stackedLayer % 2 != 0:
        return 0.5 * B.Width + (B.Length - B.Width) + off - 30 #+ Center_pallet_ver_ypos()
    else:
        return Box_fit_Vertical() * B.Width + 0.5 * B.Length + Center_pallet_ver_ypos()

###################################################################################################################

# Calculation of the vertical pattern
        
#Returns the amount of boxes that fit in the vertical pattern   
def Box_fit_Vertical():
    return (P.PalletLength - 100 - B.Length) // B.Width

#Returns the offset in the x-position to center the pattern
def Center_pallet_ver_xpos():
    return (P.PalletWidth - 50 - (2 * B.Length)) // 2

#Returns the offset in the y-position to center the pattern
def Center_pallet_ver_ypos():
    return (P.PalletLength - Box_fit_Vertical() * B.Width - B.Length) // 2

#Returns the x positions of the vertical pattern
def Vertical_ypos(x, stackedLayer, off = 20):
    if stackedLayer % 2 != 0:
        return (0.5 * B.Width + Box_fit_Vertical() * (B.Width + off) + (B.Length - B.Width) + Center_pallet_ver_ypos()) - x * (B.Width + off) - 60
    else:
        return 0.5 * B.Width + (B.Width + off) * x + Center_pallet_ver_ypos() - 60

#Returns the y positions of the vertical pattern
def Vertical_xpos(column, off = 20):
    if column == 1:
        return 0.5 * B.Length + Center_pallet_ver_xpos() + off
    else:
        return B.Length + 0.5 * B.Length + Center_pallet_ver_xpos() + off

###################################################################################################################

#Returns an array of all the horizontal x,y coordinates
def stitch_Horizontal_pos(xpos, stackedLayer):
    _pose = [Horizontal_xpos(xpos), Horizontal_ypos(stackedLayer), 0, 0.00, 0.00, 121.15]
    return _pose

#Returns an array of all the vertical x,y coordinates
def stitch_Vertical_pos(ypos, xpos, stackedLayers):
    _pose = [Vertical_xpos(xpos), Vertical_ypos(ypos, stackedLayers), 0, 0.00, 0.00, -148.25]
    return _pose

#Returns an array of all the x,y coordinates of a pattern
def create_layer_XY(stackedLayer):
    Vertical_Row = []
    Horizontal_Row = []
    for x in range(Box_fit_Vertical()):
        Vertical_Row += [stitch_Vertical_pos(x, 1, stackedLayer)]
        # print("First Row: ", stitch_Vertical_pos(x, 1))
    for x in range(Box_fit_Vertical()):
        # print("Second Row: ", stitch_Vertical_pos(x, 2))
        Vertical_Row += [stitch_Vertical_pos(x, 2, stackedLayer)]
    for x in range(Box_fit_Horizontal()):
        # print("Horizontal Row: ", stitch_Horizontal_pos(x))
        Horizontal_Row += [stitch_Horizontal_pos(x, stackedLayer)]
    return Vertical_Row, Horizontal_Row


#Returns an array of all the x,y,z coordinates of a pallet
def create_layer_Z(stackedLayer, liftLayer):
    VRow, HRow = create_layer_XY(stackedLayer)
    _XY = VRow + HRow
    for i in range(len(VRow + HRow)):
        _XY[i][2] = -B.Height - stackedLayer * B.Height + setLiftheight(stackedLayer, liftLayer)
    return _XY

#Return the hieght of the lift if the lift has moved
def setLiftheight(stackedLayer, setlift):
    if B.Height * stackedLayer > 550:
        if B.Height * setlift > 900 + 650:
            liftheight = 900
            return liftheight
        else:
            liftheight = setlift * B.Height
        return liftheight
    else:
        return 0
