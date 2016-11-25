



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

 
from Slab import Slab
from Wall import Wall    

      



  
dom = xml.dom.minidom.parse("F:\AtomEnergyProject\XMLExport\!ExportStructure.xml")
#dom = xml.dom.minidom.parse("F:\AtomEnergyProject\Structure.xml")
dom.normalize()

WallNodes=dom.getElementsByTagName('SPSWallPart')
Walls=[]
print (len(WallNodes))
for wallNode in WallNodes:
    wall=Wall().getNode(wallNode)
    Walls.extend(wall.split())
#print(len(WallNodes),len(Walls))    

SlabNodes=dom.getElementsByTagName('CSPSSlabEntity')
Slabs=[]
print (len(SlabNodes))
for slabNode in SlabNodes:
    slab=Slab().getNode(slabNode)
    Slabs.append(slab)


i=0
X=[]
Y=[]
Z=[]
    
for wall in Walls:
    #slab.out()
    X.append(wall.center().x)
    Y.append(wall.center().y)
    Z.append(wall.center().z)

Xnp=np.array(X)
   
Ynp=np.array(Y)
Znp=np.array(Z)

rx=[]
rz=[]
ry=[]
drx=[]
dry=[]
drz=[]

#for wall in Walls:
#    x=wall.curve.lines[0].start.x
#    z=wall.curve.lines[0].start.z
#    y=wall.curve.lines[0].start.y
#    dx=wall.curve.lines[0].end.x-wall.curve.lines[0].start.x
#    dy=wall.curve.lines[0].end.y-wall.curve.lines[0].start.y
#    dz=wall.curve.lines[0].end.z-wall.curve.lines[0].start.z
#    rx.append(x)
#    ry.append(y)
#    rz.append(z)
#    drx.append(dx)
#    dry.append(dy)
#    drz.append(dz)
#
#rx=np.array(rx)  
#ry=np.array(ry)
#rz=np.array(rz)
#drx=np.array(drx)
#dry=np.array(dry)
#drz=np.array(drz)

#print ('number ',i)
fig = plt.figure(figsize=[10,10])
iwalls=[]
jwalls=[]
k=0
#for i in range(len(Walls)):
#    for j in range(i+1,len(Walls)):
#        iwalls.clear()
#        jwalls.clear()
#        Walls[i].intersect(Walls[j],0.1)
#        iwalls=Walls[i].split()
#        jwalls=Walls[j].split()
#        #print (len(iwalls),len(iwalls))
#        #print(i,j)
#        if len(iwalls)==2:
#            k+=1
#            Walls.pop(i)
#            Walls.insert(i,iwalls[0])
#            Walls.append(iwalls[1])
#        if len(jwalls)==2:
#            k+=1
#            Walls.pop(j)
#            Walls.insert(j,jwalls[0])#break
#            Walls.append(jwalls[1])
           

#print(k)


# normalize the data attributes
normalized_X = preprocessing.normalize(Xnp)
normalized_Y = preprocessing.normalize(Ynp)
# standardize the data attributes
feature=np.column_stack((normalized_X.transpose(), normalized_Y.transpose()))

rzn=preprocessing.normalize(Znp)
rzn=rzn.transpose()
#plt.scatter(Ynp,Znp)
km=KMeans(n_clusters=8, random_state=0)
c=km.fit_predict(feature)
f=np.column_stack(c)
plt.scatter(Xnp,Ynp,c=c)

#plt.quiver(rx.transpose(),ry.transpose(),drx.transpose(),dry.transpose(),c,units='xy')
display, start_display, add_menu, add_function_to_menu = init_display()
#for i in range(len(Walls)):
    
   #Walls[i].draw(display,1)
print(len(Slabs))
k=0
l=0
for i in range(len(Slabs)):
    
    if Slabs[i].isWall(): 
        c=1
        l=l+1
#        Slabs[i].out
#        Slabs[i].toWall().draw(display,c)
       
    elif Slabs[i].isFloor():
        c=4
        k=k+1
        Slabs[i].toFloor().draw(display,c)

        
    else:
        c=2
#        Slabs[i].draw(display,c)
   

print (k,l)  
start_display()




    
        
    
    
        
 
          

        
  

    

    