# Pathfind ![Static Badge](https://img.shields.io/badge/License-MIT_License-green)

## Description
Welcome to Pathfind! This project will allow you to visualize different pathfinding and maze generation algorithms in an interactive and engaging way. I initially created this project as a task at school but I quickly realized how it could grow into a much more versatile and feature rich tool.
## Demo

https://github.com/user-attachments/assets/f184785c-2532-432c-9c4c-0cb6777a4288


## Supported Algorithms
### Pathfinding
- Depth First Search (*unweighted*)
- Dijkstra's (*weighted*)
- A* (*weighted*)
- BFS (Breadth First Search) (*unweighted*)
- Greedy BFS (*unweighted*)
- Bidirectional BFS (*unweighted*)

### Maze Generation
- Random Maze
- Random Weighted Maze
- RD (Recursive Division) No Skew
- RD Horizontal Skew
- RD Vertical Skew

# Features
- Supports a diverse range *weighted* and *unweighted* Pathfinding Algorithms.
- Supports a variety of Maze Generation Algorithms.
- Can select heuristics in certain Pathfinding Algorithms.
- Networking Functionality - Can have multiple players share the same board.
- Changing animation speed of Pathfinding and Maze Generation Algorithms.
- Add Custom Fonts for the UI.
- Resize Fonts in the UI.
- Change the shapes of elements in the UI.
- Build in Tutorial page.

# Running Project
## Requirements
- python>=3.10
- pygame-ce
- pygame_gui==0.6.9

## Setting up Virtual Env (recommended)
### Windows
1. Install `virutalenv` package
`pip install virtualenv`
2. Create virtual environemnt
`py -m venv venv`
3. Activate virtual environment
`venv\Scripts\activate.bat`
4. Install Packages
`pip install -r requirements.txt`

### Linux/Mac
1. Install `virutalenv` package
`pip3 install virtualenv`
2. Create virtual environemnt
`python3 -m venv venv`
3. Activate virtual environment
`source .venv/bin/activate`
4. Install Packages
`pip3 install -r requirements.txt`

## Run
After you have ensured that the requirements are installed on your system (or virtual environment) enter the root directory of the project and run the following command.
### Windows
`python source\main.py`
### Linux/Mac
`python3 source/main.py`
