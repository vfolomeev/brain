# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:01:54 2016

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

class Vector:
    'Cartesian vector'
    def __init__(self,x=0,y=0,z=0):
        self.x=x
        self.y=y
        self.z=z
    def getNode(self,node):
        self.x=float(node.getAttribute('X'))
        self.y=float(node.getAttribute('Y'))
        self.z=float(node.getAttribute('Z'))
        return self
    def out(self):
        print( "(",self.x,",",self.y,",",self.z,")")
    def scale(self,s):
        self.x=self.x*s
        self.y=self.y*s
        self.z=self.z*s
        return self
    def mag(self):
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)
    @staticmethod
    def dot(a,b):
        return (a.x*b.x+a.y*b.y+a.z*b.z)
                
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y,self.z+other.z)
  
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y,self.z-other.z)
    def __mul__(self, other):
        return Vector(self.z*other.y-self.y*other.z,self.x*other.z-self.z*other.x,self.y*other.x-self.x*other.y)
    def gpP(self):  # Creates OpenCad point type  
        P=gp_Pnt(self.x,self.y,self.z)
        return P
    def gpV(self):# Creates OpenCad vector type
        V=gp_Vec(self.x,self.y,self.z)
        return V
class Line:
    'line between two points Line3d'
    def __init__(self,start=Vector(),end=Vector(1,1,1)):
        self.start=start
        self.end=end
    def getNode(self,node):
        startNodes=node.getElementsByTagName('StartPoint')
        endNodes=node.getElementsByTagName('EndPoint')
        self.start=Vector().getNode(startNodes[0])
        self.end=Vector().getNode(endNodes[0])
        return self       
    def out(self):
        self.start.out()
        print (" ")
        self.end.out()
    def dr(self):
        dr=self.end-self.start
        return dr 
    def findIntersectionPoint(self,other):
        dx1=self.dr().x
        dx2=other.dr().x
        dy1=self.dr().y
        dy2=other.dr().y
        y10=self.start.y
        x10=self.start.x
        y20=other.start.y
        x20=other.start.x
        if dx1!=0 and dx2!=0:
            #both not parallel y
            a1=dy1/dx1
            b1=y10-(a1*x10)
            a2=dy2/dx2
            b2=y20-(a2*x20)
            if (a1-a2)!=0:
                x=(b2-b1)/(a1-a2)
                y=a1*x+b1
                return Vector(x,y,0)
            else: pass #print ('parallel')
        elif dy1!=0 and dy2!=0:
            #both not parallel x
            a1=dx1/dy1
            b1=x10-(a1*y10)
            a2=dx2/dy2
            b2=x20-(a2*y20)
            if (a1-a2)!=0:
                y=(b2-b1)/(a1-a2)
                x=a1*y+b1
                return Vector(x,y,0)
            else: pass #print ('parallel')
        elif dy1==0 and dx2==0: 
            #first parallel x and second parallel y
            x=x20
            y=y10
            return Vector(x,y,0)
        elif dx1==0 and dy2==0: 
            #first parallel y and second parallel x
            y=y20
            x=x10
            return Vector(x,y,0)       
        else:    pass #print ('parallel')
    def distanceToPoint(self,point):# distance to point along line
        dr=self.dr()
        dr.z=0
        r0=copy.copy(self.start)
        r0.z=0
        dl=point-r0
        mdr=Vector.dot(dr,dr)
        dist=Vector.dot(dr,dl)/mdr
        return dist
    
    def extend(self,dist):
        start=self.start
        end=self.end
        dr=self.dr()
        if dist>=1: end=end+dr.scale(dist)
        elif dist<=0: start=start+dr.scale(dist)
        else: return False
    def translate(self,norm,deep):
        n=copy.copy(norm)
        start=self.start+n.scale(deep)
        end=self.end+n.scale(deep)
        return Line(start,end)

class Arc:
    'Arc between tree points Arc3d'
    def __init__(self,s=Vector(),m=Vector(0.5,1,0),e=Vector(1,0,0)):
        self.start=s
        self.mid=m
        self.end=e
        
    def getNode(self,node):
        startNodes=node.getElementsByTagName('StartPoint')
        midNodes=node.getElementsByTagName('AlongPoint')
        endNodes=node.getElementsByTagName('EndPoint')
        self.start=Vector().getNode(startNodes[0])
        self.mid=Vector().getNode(midNodes[0])
        self.end=Vector().getNode(endNodes[0])
        return self
        
    def out(self):
        self.start.out()
        print (" ")
        self.mid.out()
        print (" ")
        self.end.out()
    def translate(self,norm,deep):
        n=copy.copy(norm)
        arc=copy.copy(self)
        arc.start=arc.start+n.scale(deep)
        arc.end=arc.end+n.scale(deep)
        arc.mid=arc.mid+n.scale(deep)
        return arc

        
class Circle:
    'Circle center and radius Circle3d'
    def __init__(self, cent=Vector(),rad=1):
        self.center=cent
        self.r=rad
        
    def getNode(self,node):
        centerNodes=node.getElementsByTagName('CenterPoint')
        rNodes=node.getElementsByTagName('Radius')
        self.center=Vector().getNode(centerNodes[0])
        self.r=float(rNodes[0].firstChild.nodeValue)
        return self
    def out(self):
        self.center.out()
        print (" ",self.r)
    def translate(self,norm,deep):
        n=copy.copy(norm)
        cir=copy.copy(self)
        cir.r=cir.r+n.scale(deep)
       
        return cir    
  
        
 