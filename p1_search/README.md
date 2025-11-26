# EECS 118 -- P1: Searching for Something

Version 0.1

In this project lab, you will help your Cat-Man find its way through an Irvine... maze. The goal is to pick up some catnip.

Note: Details about how to submit your work for this project lab will be provided later on Canvas assignments page.

---

## Instructions

### Setting Up Your Environment

These instructions assume that you have your environment set up and you have your workspace folder ready. If that is not the case, please refer to the course setup instructions provided in Canvas homepage (the SadCat).

1. Download `p1_search.zip` from Canvas and unzip it into your working directory. Your folder structure should look like this:

	 ```
	 your_workspace_folder/
	 ├── p1_search/
	 │   ├── p1_Search.py
	 │   ├── p1_search_test.py
	 │   └── p1_search_test_cases.txt
	 :
	 └── (other files and folders from previous labs)
	 ```
	 
2. Run `autograder.py` to test your environment setup:

	 ```bash
	 python autograder.py
	 ```
	 If everything is set up correctly, you should see your score as `0 / 0` since you haven't implemented any functions yet.


### Working with the Code

You are only allowed to modify the following files:

- `p1_search/p1_Search.py`: Here, you will implement the search algorithms. Algorithms should not be dependent on the specific problem being solved (that's why we have formalized the search problem).
- `p1_search/p1_searchAgents.py`: Here, you will design Cat-Man's AI agent as a search-based one.

[WISDOM] Why do we separate the search algorithm from the agent?
- This modular design allows us to implement and test different search algorithms independently of the specific problem being solved.
- If we later develop a better search algorithm, we can easily swap it in without changing the agent's logic.

### How to Submit

1. Complete the implementations in `p1_Search.py` and `p1_searchAgents.py` according to the project requirements.
2. Run the autograder to ensure your implementations are correct:

	 ```bash
	 python autograder.py
	 ```
	 
3. Wait for Project 1 assignment to be posted on Canvas for submission instructions.
4. ...
5. Profit!

---

## P1 Exercises

### E11 -- Manually Control your Cat-Man

Before diving into coding, let's get familiar with the environment by manually controlling Cat-Man.
1. Open a terminal and navigate to the `p1_search` directory.
2. Run the following command to start the game in manual mode:

	 ```bash
	 python catman.py
	 ```

3. Use the arrow keys to navigate Cat-Man through the apartment while staying away from your roommates.

### E12 -- Equipping Cat-Man with an existing Algorithm

- You know the drill. Run the following command to start catman with some trivial algorithm:

	```bash
	python catman.py --layout testMaze --catman GoWestAgent
	```

### E13 -- Implementing a Search Algorithm

- Run the following command to start catman with the `SearchAgent` agent and the `tinyMazeSearch` algorithm:

	```bash
	python catman.py -l tinyMaze -p SearchAgent -a fn=tinyMazeSearch --frameTime 0.5
	```
- [HINT]: In the previous command, `-a fn=tinyMazeSearch`  passes the argument `fn=tinyMazeSearch` to the `SearchAgent`, specifying that it should use the `tinyMazeSearch` algorithm.

It's about time to implement your own search algorithm.

### E14 -- Implement Depth-First Search (DFS) for Cat-Man

Now, pay attention:
1. Open `p1_search/p1_Search.py`
2. Implement the `depthFirstSearch` function. Yes, `depthFirstSearch` is where you will now implement the infamous DFS algorithm.

Hints:
- In your implementation, you can import `util` module to use its data structures like `Stack`, `Queue`, and `PriorityQueue`.
- Our search algorithms use a data structure called `nodes` -- yes, the one that appeared in the midterm exam. Each node is a tuple of three or four elements. You will need to implement the `node` data structure as well.
- Recall that we mentioned in class that DFS, BFS, UCS, and A* share the same code base (we will call it `cat's algorithm`), and only differ in how they prioritize node retrieval from the frontier. Keep this in mind while implementing DFS. If you focus now on getting the DFS right, the other algorithms will be a breeze (easy to implement).

More Hints:
- Your checklist of things to implement: `node`, `frontier`, `explored set`, `goal test`, `cat's algorithm`.

After implementing DFS, test your implementation by running:

```bash
python catman.py -l tinyMaze -p SearchAgent
python catman.py -l mediumMaze -p SearchAgent
python catman.py -l bigMaze -z .5 -p SearchAgent
```

Grade yourself by running the autograder:

```bash
python autograder.py -q q1
```

### E15 -- Implement Breadth-First Search (BFS) for Cat-Man

Now that you have implemented DFS, implementing BFS should be straightforward.
1. Open `p1_search/p1_Search.py`
2. Implement the `breadthFirstSearch` function.
3. Test your implementation by running:

```bash
python catman.py -l tinyMaze -p SearchAgent -a fn=breadthFirstSearch
python catman.py -l mediumMaze -p SearchAgent -a fn=breadthFirstSearch
python catman.py -l bigMaze -z .5 -p SearchAgent -a fn=breadthFirstSearch
```

Grade yourself by running the autograder:

```bash
python autograder.py -q q2
```

### E16 -- Your search algorithms are independent of the problem

You don't believe us??? run the following command to see your search algorithms being used to solve the 8 puzzle sliding tile game:

```bash
python eightpuzzle.py
```

Didn't work? Go back and check your implementations in `p1_search/p1_Search.py`.


### E17 -- Implement Uniform Cost Search (UCS) for Cat-Man

Implement the `uniformCostSearch` function in `p1_search/p1_Search.py`.
Test your implementation by running:

```bash
python catman.py -l mediumMaze -p SearchAgent -a fn=ucs
```

Grade yourself by running the autograder:

```bash
python autograder.py -q q3
```

---

That's it for now.