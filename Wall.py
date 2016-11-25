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



class Wall:
    'class part definition'
    def __init__(self):
        self.name=''
        self.thickness=0
        self.height=0
        self.curve=Curve()
    def getNode(self,node):
        nameNodes=node.getElementsByTagName('OID')
        self.name=nameNodes[0].firstChild.nodeValue
        
        sectionNodes=node.getElementsByTagName('Section')
        if len(sectionNodes)==0: sectionNodes=node.getElementsByTagName('StructureCrossSection')
        
        thicknessNodes=sectionNodes[0].getElementsByTagName('Thickness')
        self.thickness=float(thicknessNodes[0].firstChild.nodeValue)
        heightNodes=sectionNodes[0].getElementsByTagName('Height')
        self.height=float(heightNodes[0].firstChild.nodeValue)
        pathNodes=node.getElementsByTagName('Path')
        complexString3dNodes=pathNodes[0].getElementsByTagName('ComplexString3d')
        if len(complexString3dNodes)==0: self.curve=Curve().getNode(pathNodes[0])
        else:self.curve=Curve().getNode(complexString3dNodes[0])
        return self
    def split(self) :
        listofNewWalls=[]
        i=0
        for l in self.curve.lines:
              listofNewLines=[]
              i+=1
              listofNewLines.append(l)
              newWall=copy.deepcopy(self)
              newWall.name=newWall.name+str(i)
              newWall.curve.lines=listofNewLines
              #print(len(newWall.curve.lines))
              listofNewWalls.append(newWall)        
        
        return listofNewWalls
    def intersect(self,other,tol):
        self.curve.intersect(other.curve,tol)
                
       
    def out(self):
        print ("name=",self.name)
        print( " thickness=",self.thickness)
        print( " height=",self.height)
        print (" lines=")
        for l in self.curve.lines:
            l.out()
    def center(self):
        R1=self.curve.center()
        R2=Vector(0,0,1)
        R2.scale(0.5*self.height)
        return R1+R2
    def draw(self,display,c):
        pol=self.curve.polygon()
        if pol!=None:
            pol=pol.Wire()
            n=Vector(0,0,1)
            n.scale(self.height)
            n=n.gpV()
            #face=BRepBuilderAPI_MakeFace(pol,True).Face()
#my_shell = BRepPrimAPI_MakePrism(my_pol,n1).Shape() 
            prism = BRepPrimAPI_MakePrism(pol,n).Shape()
            if c==0: color='YELLOW'
            elif c==1: color='BLUE'
            elif c==2: color='GREEN'
            elif c==3: color='BLACK'
            elif c==4: color='RED'
            elif c==5: color='WHITE'
            elif c==6: color='CYAN'
            else: color='ORANGE'
            display.DisplayColoredShape(prism,color, update=True)

#        l=self.curve.lines[0]
#        if isinstance(l,Line):
#            p1=copy.copy(l.start)
#            h=Vector(0,0,1)
#            h.scale(self.height)
#            t=l.dr()
#            t.scale(1/t.mag())
#            n=t*Vector(0,0,1)
#            tDir=gp_Dir(t.x,t.y,t.z)
#            nDir=gp_Dir(n.x,n.y,n.z)
#            
#            P1=gp_Pnt(p1.x,p1.y,p1.z)
#            axis=gp_Ax2(P1,tDir,nDir)
#            if c==0: color='YELLOW'
#            elif c==1: color='BLUE'
#            elif c==2: color='GREEN'
#            elif c==3: color='BLACK'
#            elif c==4: color='RED'
#            elif c==5: color='WHITE'
#            elif c==6: color='CYAN'
#            else: color='ORANGE'
#            my_box = BRepPrimAPI_MakeBox(axis,0.001,self.height,l.dr().mag()).Shape()
#            display.DisplayColoredShape(my_box,color, update=True)
            
            
    
        