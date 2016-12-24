# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 13:55:34 2016

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

from prim import Vector,Line,Arc,Circle



class Curve:
    'List of lines for skatch definition ComplexString3d'
    def __init__(self):
        self.lines=[]
    
    def getNode(self,node):
         self.lines=[]
         Lines3dNodes=node.getElementsByTagName('Line3d')
         Arcs3dNodes=node.getElementsByTagName('Arc3d')
         Circles3dNodes=node.getElementsByTagName('Circle3d')
         
         for l in Lines3dNodes:
             self.lines.append(Line().getNode(l))
         for a in Arcs3dNodes:
             self.lines.append(Arc().getNode(a))
         for c in Circles3dNodes:
             self.lines.append(Circle().getNode(c))
         return self
        
    def split(self,point):
        line=self.lines[0]
        if isinstance(line,Line):
            end=copy.copy(line.end)
            line.end.x=point.x
            line.end.y=point.y
            return Line(line.end,end)
        else: return False    
            
    def intersect(self,other,tol):
        line1=self.lines[0]
        line2=other.lines[0]
        if isinstance(line1,Line) and isinstance(line2,Line):
            point=line1.findIntersectionPoint(line2)
            if point==None: return False
            dist1=line1.distanceToPoint(point)
            dist2=line2.distanceToPoint(point)
            if (-tol<dist1 and dist1<0) or (1<dist1 and dist1 <(tol+1)): 
                if (-tol<dist2 and dist2<0) or (1<dist2 and dist2 <(tol+1)):
                    line1.extend(dist1)
                    line2.extend(dist2)
                    print('intersected')
                    return True
                else : return False
            elif dist1<1 and dist1>0:
                if dist2<1 and dist2>0:
                    self.lines.append(self.split(point))
                    other.lines.append(other.split(point))
                    print('splited')
                    return True
                else : return False
            elif dist1<1 and dist1>0:
                if (-tol<dist2 and dist2<0) or (1<dist2 and dist2 <(tol+1)):
                    self.lines.append(self.split(point))
                    line2.extend(dist2)
                    print('partialy')
                    return True
                else : return False    
            elif dist2<1 and dist2>0:
                if (-tol<dist1 and dist1<0) or (1<dist1 and dist1 <(tol+1)):
                    other.lines.append(other.split(point))
                    line1.extend(dist1)
                    print('partialy')
                    return True
                else : return False
            else: return False
        else :return False
        
    
    
    def center(self):
        R=Vector()
        s=0
        for l in self.lines:
            if isinstance(l,Line):
                R=R+l.start
                R=R+l.end
                s+=2
            elif isinstance(l,Arc):
                R=R+l.start
                R=R+l.end
                R=R+l.mid
                s+=3
            elif isinstance(l,Circle): 
                R=R+l.center
                s+=1
        return R.scale(1./s)
    def polygon(self):# creates openCad polygon
        l=self.lines
        l0=l[0]
        if isinstance(l0,Line):
            print(l0.dr().mag())
            Pstart=l0.start.gpP()
            Pend=l0.end.gpP()
            pol= BRepBuilderAPI_MakePolygon(Pstart,Pend)
            
            for i in range(1,len(l)):
                if isinstance(l[i],Line):
                    Pstarti=l[i].start.gpP()
                    Pendi=l[i].end.gpP()
                    pol.Add(Pstarti)
                    pol.Add(Pendi)
            #pol.Add(Pstart)
            return pol
    def areaZ(self) :
          s=0
          for l in self.lines:
              if isinstance(l,Line):
                  s=s+(l.start.y+l.end.y)*l.dr().x/2.
                  #print (s)
          return math.fabs(s)
    def areaY(self) :
          s=0
          for l in self.lines:
              if isinstance(l,Line):
                  s=s+(l.start.z+l.end.z)*l.dr().x/2.
                  #print (s)
          return math.fabs(s)    
    def areaX(self) :
          s=0
          for l in self.lines:
              if isinstance(l,Line):
                  s=s+(l.start.z+l.end.z)*l.dr().y/2.
                  #print (s)
          return math.fabs(s)    
    def minV(self)    :
        minV=Vector(2000,2000,2000)
        
        for l in self.lines:
            if isinstance(l,Line):
                minV.x=min(minV.x,l.start.x,l.end.x)
                minV.y=min(minV.y,l.start.y,l.end.y)
                minV.z=min(minV.z,l.start.z,l.end.z)
            if isinstance(l,Arc):
                minV.x=min(minV.x,l.start.x,l.end.x,l.mid.x)
                minV.y=min(minV.y,l.start.y,l.end.y,l.mid.y)
                minV.z=min(minV.z,l.start.z,l.end.z,l.mid.z)    
            if isinstance(l,Circle):
                minV.x=min(minV.x,l.center.x,l.center.x-l.r)
                minV.y=min(minV.y,l.center.y,l.center.y-l.r)
                minV.z=min(minV.z,l.center.z,l.center.z-l.r)
        return minV
    def maxV(self)    :
        maxV=Vector(-2000,-2000,-2000)
        
        for l in self.lines:
            if isinstance(l,Line):
                maxV.x=max(maxV.x,l.start.x,l.end.x)
                maxV.y=max(maxV.y,l.start.y,l.end.y)
                maxV.z=max(maxV.z,l.start.z,l.end.z)
            if isinstance(l,Arc):
                maxV.x=max(maxV.x,l.start.x,l.end.x,l.mid.x)
                maxV.y=max(maxV.y,l.start.y,l.end.y,l.mid.y)
                maxV.z=max(maxV.z,l.start.z,l.end.z,l.mid.z)    
            if isinstance(l,Circle):
                maxV.x=max(maxV.x,l.center.x,l.center.x-l.r)
                maxV.y=max(maxV.y,l.center.y,l.center.y-l.r)
                maxV.z=max(maxV.z,l.center.z,l.center.z-l.r)
        return maxV
    def translate(self,norm,deep):
        new=copy.deepcopy(self)
        new.lines.clear()
        for l in self.lines:
            new.lines.append(l.translate(norm,deep))
        return new
            
        