# BombSolver
### Defusing bombs in *Keep Talking and Nobody Explodes* using Image Analysis and Machine Learning

### How it works
The BombSolver has ***no*** knowledge of the game code.
It only controls the cursor and identifies features on the bomb by taking screenshots.

It starts by rotating the bomb to capture images of all six sides.
It then identifies all the modules and features of the specific bomb
(does it have any indicators, how many batteries are there, what is the serial number, etc.).

It then goes through each module/puzzle and uses image analysis / machine learning to identify the different
parts of the specific puzzle. The solutions from the bomb manual (which are hard coded into the program) is then used to 
actually solve the modules (again, simply by controlling the cursor).

OCI, using a seperate Neural Network, is used to solve the *Who's On First?*, *Memory Game*, *Button*, and *Password* modules
(as well as for some other miscellaneous things).

A seperate network is used for solving the *Symbols* module.

The *Maze* module is solved by first detecting which maze it is, and then finding the optimal path using BFS.

The *Password* module uses a DFS-ish approach, in order to quickly find the most likely word.

Any (non-modded) bomb can be defused in record time!

### Video of the program in action
[![The Bomb Solver in action](https://img.youtube.com/vi/ciO1RNPe2g0/maxresdefault.jpg)](https://www.youtube.com/watch?v=ciO1RNPe2g0)
