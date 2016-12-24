



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

def Split(Walls):
    for i in range(len(Walls)):
        if Walls[i].isSplitable(): 
            print('split')
            w=Walls[i].split()
            Walls.pop(i)
            Walls.extend(w)    
class Level:
     'represents building floor'
     def __init__(self):
        self.walls=[]
        self.floors=[]
        self.slabs=[]
     def draw(self,display,c):
        for w in self.walls:
            if (len(w.connections)!=0): w.draw(display,c)
            
        for f in self.floors:
            f.draw(display,c+1)
        for s in self.slabs:
            s.draw(display,c+2)
     def removeSingular(self,tol)        :
        
        newWalls=[]
        newWalls.clear()
        for w in self.walls:
            if w.isSingular(tol):
                print('Singular')
                print(w.curve.lines[0].dr().mag())
            else: newWalls.append(w)
        self.walls.clear()
        self.walls.extend(newWalls)
     def intersectWalls(self,tol):
         iwalls=[]
         jwalls=[]
         k=0
         Walls=self.walls
         for i in range(len(Walls)):
             for j in range(i+1,len(Walls)):
                 iwalls.clear()
                 jwalls.clear()
                 Walls[i].intersect(Walls[j],tol)
                 iwalls=Walls[i].split()
                 jwalls=Walls[j].split()
        #print (len(iwalls),len(iwalls))
        #print(i,j)
                 if len(iwalls)==2:
                    k+=1
                    Walls.pop(i)
                    Walls.insert(i,iwalls[0])
                    Walls.append(iwalls[1])
                 if len(jwalls)==2:
                    k+=1
                    Walls.pop(j)
                    Walls.insert(j,jwalls[0])#break
                    Walls.append(jwalls[1])
         
         
class Building:
    'standalone constraction'
    def __init__(self):
        self.walls=[]
        self.floors=[]
        self.slabs=[]
        self.levels=[]
    def draw(self,display,c):
        
        for w in self.walls:
            w.draw(display,c)
        for f in self.floors:
            f.draw(display,c+1)
        for s in self.slabs:
            s.draw(display,c+2)
    def toShells(self):
        newSlab=[]
        newSlab.clear()
        newWall=[]
        newWall.clear()
        
        for  s in self.slabs:
            
                
            if s.isFloor():
                self.floors.append(s.toFloor())
            elif s.isWall():
                w=s.toWall()
                newWall.append(w)
            else : newSlab.append(s)
        self.slabs.clear()
        self.slabs=copy.deepcopy(newSlab)
        
        self.walls.extend(newWall)
            
    def removeSingular(self,tol)        :
        newWalls=[]
        newWalls.clear()
        for w in self.walls:
            if w.isSingular(tol):
                print('Singular')
                print(w.curve.lines[0].dr().mag())
            else: newWalls.append(w)
        self.walls.clear()
        self.walls.extend(newWalls)
        
    def createLevels(self,n):
        Z=[]
        for wall in self.walls:
            Z.append(wall.center().z)
        for slab in self.slabs:
            Z.append(slab.center().z)
        for floor in self.floors:
            Z.append(floor.center().z)
        print('Z')
        print(len(Z))
        Znp=np.array(Z)
        # normalize the data attributes
        normalized_Z = preprocessing.normalize(Znp)
        
       


        km=KMeans(n_clusters=n, random_state=0)
        c=km.fit_predict(normalized_Z.transpose())
        #f=np.column_stack(c)
        
        for i in range(n):
            self.levels.append(Level())
        i=0
        for wall in self.walls:
            self.levels[c[i]].walls.append(wall)
            i+=1
        for slab in self.slabs:
            self.levels[c[i]].slabs.append(slab)
            i+=1
        for floor in self.floors:
            self.levels[c[i]].floors.append(floor)
            i+=1



class Structure:
    'entire structure'
    def __init__(self,file="F:\AtomEnergyProject\XMLExport\!ExportStructure.xml"):
            
        
        dom = xml.dom.minidom.parse(file)
#dom = xml.dom.minidom.parse("F:\AtomEnergyProject\Structure.xml")
        dom.normalize()

        WallNodes=dom.getElementsByTagName('SPSWallPart')
        self.walls=[]
        print (len(WallNodes))
        for wallNode in WallNodes:
            wall=Wall().getNode(wallNode)
            self.walls.extend(wall.split())
#print(len(WallNodes),len(Walls))    

        SlabNodes=dom.getElementsByTagName('CSPSSlabEntity')
        self.slabs=[]
        print (len(SlabNodes))
        for slabNode in SlabNodes:
            slab=Slab().getNode(slabNode)
            self.slabs.append(slab)

        self.buildings=[]

    def createBuildings(self,n=2):
   

        X=[]
        Y=[]
        Z=[]
    
        for wall in self.walls:
    #slab.out()
            X.append(wall.center().x)
            Y.append(wall.center().y)
            Z.append(wall.center().z)



        for slab in self.slabs:
    #slab.out()
            X.append(slab.center().x)
            Y.append(slab.center().y)
            Z.append(slab.center().z)

        Xnp=np.array(X)
        Ynp=np.array(Y)
        Znp=np.array(Z)
        # normalize the data attributes
        normalized_X = preprocessing.normalize(Xnp)
        normalized_Y = preprocessing.normalize(Ynp)
        # standardize the data attributes
        feature=np.column_stack((normalized_X.transpose(), normalized_Y.transpose()))

        rzn=preprocessing.normalize(Znp)
        rzn=rzn.transpose()

        km=KMeans(n_clusters=n, random_state=0)
        c=km.fit_predict(feature)
        #f=np.column_stack(c)
        
        for i in range(n):
            self.buildings.append(Building())
        i=0
        for wall in self.walls:
            self.buildings[c[i]].walls.append(wall)
            i+=1
        for slab in self.slabs:
            self.buildings[c[i]].slabs.append(slab)
            i+=1





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

struct=Structure('F:\AtomEnergyProject\!\!.xml')
struct.createBuildings(1)







#struct.buildings[0].toShells()
#struct.buildings[0].createLevels(3)

#struct.buildings[0].draw(display,1)


#for i in range(3):
#    
#    struct.buildings[0].levels[i].draw(display,i)

#struct.buildings[0].levels[0].intersectWalls(0.1)
#struct.buildings[0].levels[0].removeSingular(0.1)

#for w in struct.buildings[0].levels[0].walls:
#    for l in w.curve.lines:
#        if l.dr().mag()==0: print('pisdec')
#        else: 
#            print('good')
#            l.out()

    

display, start_display, add_menu, add_function_to_menu = init_display()
#struct.buildings[0].levels[0].draw(display,0)
struct.buildings[0].draw(display,0)

start_display()




    
        
    
    
        
 
          

        
  

    

    