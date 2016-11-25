# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 16:01:17 2016

@author: vfolomeev
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:29:02 2016

@author: vfolomeev
"""
import xml.dom.minidom
import numpy as np
import scipy as sc
import math
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import preprocessing
import scipy.integrate as spint

from OCC.Display.SimpleGui import init_display
from OCC.gp import *
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.BRepPrimAPI import BRepPrimAPI_MakePrism
#from OCC.BRepPrimAPI import BRepPrimAPI_MakePolygon
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakePolygon 
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeFace 

from Curve import Curve

from prim import Vector,Line,Arc,Circle 



class Floor:
    'class part definition'
    def __init__(self):
        self.name=''
        self.thickness=0
        self.curve=Curve()
    
                  
      
    def out(self):
        print ("name=",self.name)
        print( " thickness=",self.thickness)
        
        print (" lines=")
        for l in self.curve.lines:
            l.out()
    def center(self):
        R1=self.curve.center()
        R2=Vector(0,0,1)
        R2.scale(0.5*self.thickness)
        return R1+R2
    def draw(self,display,c):
        pol=self.curve.polygon()
        if pol!=None:
            pol=pol.Wire()
            face=BRepBuilderAPI_MakeFace(pol,True).Face()
            
            #prism = BRepPrimAPI_MakePrism(pol,n).Shape()
            if c==0: color='YELLOW'
            elif c==1: color='BLUE'
            elif c==2: color='GREEN'
            elif c==3: color='BLACK'
            elif c==4: color='RED'
            elif c==5: color='WHITE'
            elif c==6: color='CYAN'
            else: color='ORANGE'
            display.DisplayColoredShape(face,color, update=True)

#        
            
            
    
        