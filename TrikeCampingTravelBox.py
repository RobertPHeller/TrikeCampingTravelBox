#*****************************************************************************
#
#  System        : 
#  Module        : 
#  Object Name   : $RCSfile$
#  Revision      : $Revision$
#  Date          : $Date$
#  Author        : $Author$
#  Created By    : Robert Heller
#  Created       : Sun Jul 28 13:57:52 2024
#  Last Modified : <240728.1941>
#
#  Description	
#
#  Notes
#
#  History
#	
#*****************************************************************************
#
#    Copyright (C) 2024  Robert Heller D/B/A Deepwoods Software
#			51 Locke Hill Road
#			Wendell, MA 01379-9728
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# 
#
#*****************************************************************************


import Part, TechDraw, Spreadsheet, TechDrawGui
import FreeCADGui
from FreeCAD import Console
from FreeCAD import Base
import FreeCAD as App
import os
import sys
sys.path.append(os.path.dirname(__file__))

import datetime

from PySide.QtCore import QCoreApplication, QEventLoop, QTimer
import time
from PySide import QtGui
def execute(loop, ms):
    timer = QTimer()
    timer.setSingleShot(True)
    
    timer.timeout.connect(loop.quit)
    timer.start(ms)
    loop.exec_()

def sleep(ms):
    if not QCoreApplication.instance():
        app = QCoreApplication([])
        execute(app, ms)
    else:
        loop = QEventLoop()
        execute(loop, ms)

class TrikeCampingTravelBox(object):
    __BoardThick = 1.0*25.4
    __BoxOuterWidth = 27.25*25.4
    __BoxOuterLength = 64*25.4
    __BoxOuterHeight = 24*25.4
    __CornerWidth = 1.25*25.4
    __CornerLength = (5.0/8.0)*25.4
    __CornerHeight = 2.5*25.4
    __HitchNotchWidth = (27.24-22.5)*25.4
    __HitchNotchLength = .75*25.4
    __HitchNotchHeight = 3*25.4
    __BoardWidth = 8**25.4
    __FloorThick = .5*25.4
    __Rabbet = .5*25.4
    def __init__(self,name,origin):
        self.name = name
        if not isinstance(origin,Base.Vector):
            raise RuntimeError("origin is not a Vector!")
        self.origin = origin
        negRabbet = self.__BoardThick - self.__Rabbet
        floorWidth = self.__BoxOuterWidth - 2*negRabbet
        floorLength = self.__BoxOuterLength - 2*negRabbet
        floorOrigin = origin.add(Base.Vector(negRabbet,negRabbet,0))
        self.floor = Part.makePlane(floorWidth,floorLength,floorOrigin)\
                    .extrude(Base.Vector(0,0,self.__FloorThick))
        frontOrig = origin.add(Base.Vector(negRabbet,0,0))
        endWidth = self.__BoxOuterWidth - 2*negRabbet
        self.front = Part.makePlane(endWidth,self.__BoardThick,frontOrig)\
                    .extrude(Base.Vector(0,0,self.__BoxOuterHeight))
        self.front = self.front.cut(self.floor)
        backOrig = origin.add(Base.Vector(negRabbet,\
                                          self.__BoxOuterLength-self.__BoardThick,\
                                          0))
        self.back = Part.makePlane(endWidth,self.__BoardThick,backOrig)\
                    .extrude(Base.Vector(0,0,self.__BoxOuterHeight))
        self.back = self.back.cut(self.floor)  
        self.left = Part.makePlane(self.__BoardThick,self.__BoxOuterLength,\
                                   origin)\
                    .extrude(Base.Vector(0,0,self.__BoxOuterHeight))
        self.left = self.left.cut(self.floor)
        self.left = self.left.cut(self.front)
        self.left = self.left.cut(self.back)
        rightOrig = origin.add(Base.Vector(self.__BoxOuterWidth - self.__BoardThick,0,0))
        self.right = Part.makePlane(self.__BoardThick,self.__BoxOuterLength,\
                                   rightOrig)\
                    .extrude(Base.Vector(0,0,self.__BoxOuterHeight))
        self.right = self.right.cut(self.floor)
        self.right = self.right.cut(self.front)
        self.right = self.right.cut(self.back)
        frontCenterOrig = origin.add(Base.Vector(self.__BoxOuterWidth/2,0,0))
        hitchSpaceOrig = frontCenterOrig.add(Base.Vector(-(self.__HitchNotchWidth/2),0,0))
        hitchSpace = Part.makePlane(self.__HitchNotchWidth,\
                                    self.__HitchNotchLength,\
                                    hitchSpaceOrig)\
                    .extrude(Base.Vector(0,0,self.__HitchNotchHeight))
        self.front = self.front.cut(hitchSpace)
        self.floor = self.floor.cut(hitchSpace)
        self.cornerNotch(origin)
        self.cornerNotch(origin.add(Base.Vector(self.__BoxOuterWidth-self.__CornerWidth,0,0)))
        self.cornerNotch(origin.add(Base.Vector(0,self.__BoxOuterLength-self.__CornerLength,0)))
        self.cornerNotch(origin.add(Base.Vector(self.__BoxOuterWidth-self.__CornerWidth,\
                                                self.__BoxOuterLength-self.__CornerLength,0)))
    def cornerNotch(self,cornerOrig):
        notch = Part.makePlane(self.__CornerWidth,self.__CornerLength,cornerOrig)\
                .extrude(Base.Vector(0,0,self.__CornerHeight))
        self.floor = self.floor.cut(notch)
        self.front = self.front.cut(notch)
        self.back = self.back.cut(notch)
        self.left = self.left.cut(notch)
        self.right = self.right.cut(notch)
    def show(self,doc=None):
        if doc==None:
            doc = App.activeDocument()
        obj = doc.addObject("Part::Feature",self.name+"_floor")
        obj.Shape=self.floor
        obj.Label=self.name+"_floor"
        obj.ViewObject.ShapeColor=tuple([210/255,180/255,140/255])
        obj = doc.addObject("Part::Feature",self.name+"_front")
        obj.Shape=self.front
        obj.Label=self.name+"_front"
        obj.ViewObject.ShapeColor=tuple([139/255,90/255,43/255])
        obj = doc.addObject("Part::Feature",self.name+"_back")
        obj.Shape=self.back
        obj.Label=self.name+"_back"
        obj.ViewObject.ShapeColor=tuple([139/255,90/255,43/255])
        obj = doc.addObject("Part::Feature",self.name+"_left")
        obj.Shape=self.left
        obj.Label=self.name+"_left"
        obj.ViewObject.ShapeColor=tuple([139/255,90/255,43/255])
        obj = doc.addObject("Part::Feature",self.name+"_right")
        obj.Shape=self.right
        obj.Label=self.name+"_right"
        obj.ViewObject.ShapeColor=tuple([139/255,90/255,43/255])
        

if __name__ == '__main__':
    docs = App.listDocuments()
    for k in docs:
        App.closeDocument(k)
    App.ActiveDocument=App.newDocument("Temp")
    doc = App.activeDocument()
    box = TrikeCampingTravelBox("box",Base.Vector(0,0,0))
    box.show()
    Gui.SendMsgToActiveView("ViewFit")
    Gui.activeDocument().activeView().viewTop()
