# BombSolver
### Defusing bombs in *Keep Talking and Nobody Explodes* using Image Analysis and Machine Learning

### Features
- Fully autonomous bomb solver using no knowledge of the game code.
- Uses screenshots and simple mouse movement to navigate and disarm any (non-modded) bomb.
- Module detection using a Convolutional Neural Network.
- Character detection (used to solve Who's on First, Memory Game, etc) also using a CNN.

### Usage
**_Note:_** Not usable yet, as the classifier model is not uploaded to Git yet (it will in the future, hopefully).
1. Install Anaconda (or Miniconda).
2. Activate the conda environment using `conda activate tens_gpu`.
3. Launch Keep Talking and Nobody Explodes (KTANE).
4. Select a level within the game, but do not press "Start".
5. Run `python main.py` in the root directory.
6. Press S while in the summary window of the selected KTANE level.
7. The program will start the level and do it's magic.
