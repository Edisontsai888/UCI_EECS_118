# p1_Search.py
# ---------
# Based on search.py from the UC Berkeley Pacman AI Projects.
# Original authors: John DeNero, Dan Klein, Brad Miller, Nick Hay, Pieter Abbeel.
# Original project link: http://ai.berkeley.edu
#
# Modifications for UCI EECS 118 by Mahmoud Elfar, 2025.
# This version includes changes to <TBD>.
#
# Licensing: You may use or extend this file for educational purposes
# provided that (1) solutions are not distributed or published,
# (2) this notice is retained, and (3) clear attribution to UC Berkeley is kept.


"""
In p1_Search.py, you will implement generic search algorithms which are called by
Pacman agents (in p1_SearchAgents.py).
"""

import util
from game import Directions
from typing import List

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()




def tinyMazeSearch(problem: SearchProblem) -> List[Directions]:
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem) -> List[Directions]:
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    frontier = util.Stack()
    explored = set()
    startState = problem.getStartState()    
    startActions = []
    
    frontier.push((startState, startActions))
    while not frontier.isEmpty():
        currentState, actions = frontier.pop()

        if problem.isGoalState(currentState):
            return actions

        if currentState in explored:
            continue

        explored.add(currentState)

        for successorState, action, stepCost in problem.getSuccessors(currentState):
            if successorState not in explored:
                newActions = actions + [action]
                
                frontier.push((successorState, newActions))

    return []

    
                    

def breadthFirstSearch(problem: SearchProblem) -> List[Directions]:
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    frontier = util.Queue()
    explored = set() 
    startState = problem.getStartState()
    startActions = []
    frontier.push((startState, startActions))

    while not frontier.isEmpty():
        currentState, actions = frontier.pop()

        if currentState in explored:
            continue

        explored.add(currentState)
        
        if problem.isGoalState(currentState):
            return actions

        for successorState, action, stepCost in problem.getSuccessors(currentState):
            if successorState not in explored:
                newActions = actions + [action]
                
                frontier.push((successorState, newActions))

    return []
    
    

def uniformCostSearch(problem: SearchProblem) -> List[Directions]:
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    frontier = util.PriorityQueue()
    explored_cost = {}
    startState = problem.getStartState()
    startActions = []
    startCost = 0
    
    frontier.push((startState, startActions, startCost), startCost)
    
    explored_cost[startState] = startCost

    while not frontier.isEmpty():
        currentState, actions, currentCost = frontier.pop()

        if problem.isGoalState(currentState):
            return actions

        for successorState, action, stepCost in problem.getSuccessors(currentState):
            newCost = currentCost + stepCost
            newActions = actions + [action]
            
            if successorState not in explored_cost or newCost < explored_cost[successorState]:
                
                explored_cost[successorState] = newCost
                
                frontier.push((successorState, newActions, newCost), newCost)

    return []


def nullHeuristic(state, problem=None) -> float:
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic) -> List[Directions]:
    """Search the node that has the lowest combined cost and heuristic first."""
    
    frontier = util.PriorityQueue()

    explored_g_cost = {}

    startState = problem.getStartState()
    startActions = []
    startGCost = 0 
    
    startFCost = startGCost + heuristic(startState, problem)

    frontier.push((startState, startActions, startGCost), startFCost)

    explored_g_cost[startState] = startGCost

    while not frontier.isEmpty():
        currentState, actions, currentGCost = frontier.pop()
        if currentGCost > explored_g_cost[currentState]:
            continue

        if problem.isGoalState(currentState):
            return actions

        for successorState, action, stepCost in problem.getSuccessors(currentState):
            newGCost = currentGCost + stepCost
            newActions = actions + [action]
            
            if successorState not in explored_g_cost or newGCost < explored_g_cost[successorState]:

                explored_g_cost[successorState] = newGCost
                
                successorFCost = newGCost + heuristic(successorState, problem)

                frontier.push((successorState, newActions, newGCost), successorFCost)

    return []

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
