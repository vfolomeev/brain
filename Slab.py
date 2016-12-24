# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:27:35 2016

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
from Wall import Wall
from Floor import Floor
       
class Slab:
    'class part definition'
    def __init__(self):
        self.name=''
        self.normal=Vector()
        self.thickness=0
        self.curve=Curve()
        
    def getNode(self,node):
        nameNodes=node.getElementsByTagName('OID')
        self.name=nameNodes[0].firstChild.nodeValue
        normNodes=node.getElementsByTagName('Normal')
        self.normal=Vector().getNode(normNodes[0])
        thicknessNodes=node.getElementsByTagName('TotalThickness')
        if len(thicknessNodes)==0: thicknessNodes=node.getElementsByTagName('Thickness')
        self.thickness=float(thicknessNodes[0].firstChild.nodeValue)
        boundaryNodes=node.getElementsByTagName('Boundary')
        if len(boundaryNodes)==0: boundaryNodes=node.getElementsByTagName('Contour')
        complexString3dNodes=boundaryNodes[0].getElementsByTagName('ComplexString3d')
        if len(complexString3dNodes)==0: complexString3dNodes=node.getElementsByTagName('Contour')
        self.curve=Curve().getNode(complexString3dNodes[0])
        return self
    def center(self):
        R1=self.curve.center()
        R2=copy.deepcopy(self.normal)
        R2.scale(0.5*self.thickness)
        return R1+R2
    def toWall(self):
        w=Wall()
        w.name=self.name+'wall'
        w.curve.lines.clear()
        n=self.normal
        deep=self.thickness
        l=self.curve.lines
        
        if n.z!=0:
            if l[0].dr().mag()>l[1].dr().mag(): 
                line=l[0]
                dr=l[2].start-l[0].start
            else: 
                line=l[1]
                dr=l[3].start-l[1].start
            
            
            line=line.translate(dr,0.5)
            #line.out()
            w.curve.lines.append(line)
            w.height=deep
            w.thickness=dr.mag()
            
        else:
            max=self.maxV()
            min=self.minV()
            
            diag=max-min
            if diag.x>diag.y:
                start=Vector(min.x,(min.y+max.y)/2,min.z)
                end=Vector(max.x,(min.y+max.y)/2,min.z)
                thick=diag.y
            else:
                start=Vector((min.x+max.x)/2,min.y,min.z)
                end=Vector((min.x+max.x)/2,max.y,min.z)
                thick=diag.x
            line=Line(start,end)
            
            w.curve.lines.append(line)
            w.height=diag.z
            w.thickness=thick
        return w
    def toFloor(self)        :
        f=Floor()
        f.name=self.name+'floor'
        n=self.normal
        deep=self.thickness
        lines=self.curve.lines
        f.curve.lines.clear()
        newlines1=[]
        newlines1.clear()
        newlines2=[]
        newlines2.clear()
        if n.z!=0:
            f.curve.lines=copy.deepcopy(lines)
            f.thickness=deep
            
        else: 
            min=self.minV()
            dz=self.dR().z
            for l in lines:
                if l.start.z==min.z and l.end.z==min.z:
                   newlines1.append(l)
                   newlines2.append(l.translate(n,deep))
            start1=newlines1[len(newlines1)-1].end
            end1=newlines2[len(newlines1)-1].end
            start2=newlines1[0].start
            end2=newlines2[0].start
            newlines1.append(Line(start1,end1))
            newlines1.extend(newlines2)
            newlines1.append(Line(start2,end2))
            f.curve.lines.extend(newlines1)
            f.thickness=dz
        return f    
                    
                
        
        
        
        
        
    def out(self):
        print ("name=",self.name)
        print ("normal=")
        self.normal.out()
        print( " thickness=",self.thickness)
        print (" lines=")
        for l in self.curve.lines:
            l.out()
          
    def draw(self,display,c) :
        pol=self.curve.polygon()
        if pol!=None:
            pol=pol.Wire()
            n=copy.copy(self.normal)
            n.scale(self.thickness)
            n=n.gpV()
            face=BRepBuilderAPI_MakeFace(pol,True).Face()
#my_shell = BRepPrimAPI_MakePrism(my_pol,n1).Shape() 
            prism = BRepPrimAPI_MakePrism(face,n).Shape()
            if c==0: color='YELLOW'
            elif c==1: color='BLUE'
            elif c==2: color='GREEN'
            elif c==3: color='BLACK'
            elif c==4: color='RED'
            elif c==5: color='WHITE'
            elif c==6: color='CYAN'
            else: color='ORANGE'
            display.DisplayColoredShape(prism,color, update=True)
    def minV(self)        :
        minV=copy.deepcopy(self.curve.minV())
        
        n=copy.deepcopy(self.normal)
        sign=n.x+n.y+n.z
        if sign<0: return minV+n.scale(self.thickness)
        else: return minV
    def maxV(self)        :
        maxV=copy.deepcopy(self.curve.maxV())
       
        n=copy.deepcopy(self.normal)
        sign=n.x+n.y+n.z
        if sign>0: return maxV+n.scale(self.thickness)
        else: return maxV
    def dR(self)    :
        return self.maxV()-self.minV()
    def isWall(self):
        r=self.dR()
        n=self.normal
        i=0
        k=0
        b=0
        if n.x!=0:b+=1
        if n.y!=0:b+=1
        if n.z!=0:b+=1
        for l in self.curve.lines:
            if isinstance(l,Line):       i+=1
            else: k+=1
        if r.z>2*r.y or r.z>2*r.x: 
            if i==4 and k==0 and b==1:return True
            else : return False
        else: return False
    def isFloor(self):
        r=self.dR()
        if (self.isWall()==False): 
            if 2*r.z<r.y or 2*r.z<r.x: return True
            else: return False
        else : return False
#    def isWall(self):
#        n=self.normal
#        l=self.curve.lines
#        if len(l)==4: 
#           l1=l[1].end-l[0].start
#           l2=l[0].end-l[3].start
#           if l1.mag()==l2.mag():
#                    #box
#              h=self.thickness
#              r1=l[0].dr()
#              r2=l[1].dr()
#              r=r1+r2
#              if (n.x==0 and n.y==0 and n.z!=0):
#                  Sxy=(r1*r2).mag()
#                  Sz1=h*r1.mag()
#                  Sz2=h*r2.mag()
#                  if Sxy<min(Sz1,Sz2): return True
#                  else: return False
#              elif (n.x==0 and n.y!=0 and n.z==0):
#                  Sxz=(r1*r2).mag()
#                  Sxy=h*math.fabs(r.x)
#                  Szy=h*math.fabs(r.z)
#                  if Sxy<min(Sxz,Szy): return True
#                  else: return False
#              elif (n.x!=0 and n.y==0 and n.z==0):
#                  Szy=(r1*r2).mag()
#                  Sxz=h*math.fabs(r.z)
#                  Sxy=h*math.fabs(r.y)
#                  if Sxy<min(Sxz,Szy): return True
#                  else: return False
#              else: return False
#        
#                    
#              
#                    
#              
#           else: return False
#        else: return False
#    def isFloor(self):
#        n=self.normal
#        l=self.curve.lines
#        if len(l)==4: 
#           l1=l[1].end-l[0].start
#           l2=l[0].end-l[3].start
#           if l1.mag()==l2.mag():
#                    #box
#              h=self.thickness
#              r1=l[0].dr()
#              r2=l[1].dr()
#              r=r1+r2
#              if (n.x==0 and n.y==0 and n.z!=0):
#                  Sxy=(r1*r2).mag()
#                  Sz1=h*r1.mag()
#                  Sz2=h*r2.mag()
#                  if Sxy>max(Sz1,Sz2): return True
#                  else: return False
#              elif (n.x==0 and n.y!=0 and n.z==0):
#                  if Vector.dot(r1,Vector(0,0,1))==0 or Vector.dot(r2,Vector(0,0,1))==0:
#                      Sxz=(r1*r2).mag()
#                      Sxy=h*math.fabs(r.x)
#                      Szy=h*math.fabs(r.z)
#                      if Sxy>max(Sxz,Szy): return True
#                      else: return False
#                  else: return False
#              elif (n.x!=0 and n.y==0 and n.z==0):
#                  if Vector.dot(r1,Vector(0,0,1))==0 or Vector.dot(r2,Vector(0,0,1))==0:
#                      Szy=(r1*r2).mag()
#                      Sxz=h*math.fabs(r.z)
#                      Sxy=h*math.fabs(r.y)
#                      if Sxy>max(Sxz,Szy): return True
#                      else: return False
#                  else: return False
#              else: return False  