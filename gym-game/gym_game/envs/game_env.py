import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding
import nbimporter
import numpy as np
import math
import sys
if('..' not in sys.path):
    sys.path.insert(0,'..')
if('../..' not in sys.path):
    sys.path.insert(0,'../..')
from Maze.Maze import Maze
from Maze.MazeGenerator import MazeGenerator
from Agents.Worker import Worker
from Main.Simulator import Simulator
from Maths.Cord import Cord
from Maths.Action import Action

class GameEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
       # print("Initialising")
        m=        "Test,10,10,0,4,9,4,1111211111100000000111100110011000000001100001111111011000111000000001100101010110000000011111311111"
        #"Test,4,4,0,2,3,2,1121100110011131" MazeGenerator() 
        self.maze= Maze(m)
        self.s=Simulator(self.maze)
        self.span=6
        self.number=2
        self.pList=[]
        self.stateList=[]
        self.history=m+"|"+"0"
        self.finished=0
        for j in range(self.number):
            p=Worker(self.maze)
            self.s.add(p)
            self.pList.append(p)
            state= np.asarray(p.getView(p.getPos(),self.span))
            self.stateList.append(state)
            self.history+="#"+p.getName()+"-"+p.getPos().CordToString()
        self.history+="|"
        action_space=[]
        
        for i in range(0,len(Action)):            
            action_space.append(Action(i))
        self.action_space=np.asarray(action_space)
        self.observation_space= math.pow(2*self.span+1,2)*self.number
        self.shortestRoute=len(self.maze.GetOptimalRoute()[0])
        self.maze.printMaze()

    def step(self, action):        
        #print("Stepping")
        stateList=self.stateList
        state_nextList=np.empty([1,2*self.span+1,2*self.span+1])
        reward=0
        terminal=False
        info={}
        self.history+=str(self.pList[0].getTime())
        
        index=0
        for p in self.pList:            
            oldPosition=p.getPos()
            state_next=np.empty(1)
            if(action in self.maze.WhichWayIsClear(oldPosition)):
                p.Do(action,self.maze)
                state_Next=np.asarray(p.getView(p.getPos(),self.span))
                reward+=p.getReward(p.getPos(), True,oldPosition,p.getView(p.getPos(),self.span))
            else:
                state_Next=np.asarray(p.getView(p.getPos(),self.span))                
                reward+=p.getReward(p.getPos(), False,oldPosition,p.getView(p.getPos(),self.span))
            #print(state_nextList)
            #print(state_Next)
            #print(action, reward)
            state_nextList=np.append(state_nextList,[state_Next], axis=0)
            index+=1
            self.history+="#"+p.getName()+"-"+p.getPos().CordToString()
            if(self.maze.CheckExit(p.getPos())):
                self.finished+=1
        self.history+="|"   
        state_nextList=np.delete(state_nextList,0,axis=0)
        
        if(self.finished==len(self.pList)):
            file=open("Games.txt","a+")
            file.write(self.history+"\n")
            file.close()
            terminal=True
            
        return state_nextList, reward, terminal, info
    
    def reset(self):        
        #print("Resetting")
        self.stateList=[]
        self.history=self.maze.mazeString+"|"+"0"
        self.finished=0
        for p in self.pList:
            p.setInitPos(Cord(self.maze.getInitialX(),self.maze.getInitialY()))
            state=np.asarray(p.getView(p.getPos(),self.span))
            self.stateList.append(state)
            self.history+="#"+p.getName()+"-"+p.getPos().CordToString()
        self.history+="|"
        return self.stateList
    
    def resetNewMaze(self):        
        m= MazeGenerator()  
        self.maze= Maze(m)
        self.s=Simulator(self.maze)
        self.pList=[]
        self.stateList=[]
        self.history=m+"|"+"0"
        self.finished=0
        for j in range(self.number):
            p=Worker(self.maze)
            self.pList.append(p)
            self.s.add(p)
            state= np.asarray(p.getView(p.getPos(),self.span))
            self.stateList.append(state)
            self.history+="#"+p.getName()+"-"+p.getPos().CordToString()
        self.history+="|"
        self.shortestRoute=len(self.maze.GetOptimalRoute()[0])
        self.maze.printMaze()
        return self.stateList
        
    def render(self, mode='human', close=False):
        self.s.display()