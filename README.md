# Sternhalma (Chinese Checkers)

Files from https://github.com/suragnair/alpha-zero-general

SternhalmaGame.py: Implementation of Sternhalma game logic (simplified version)
Coach.py: Modified so that self-play considers previously-seen states to be a draw
MCTS.py: Modified so that MCTS considers previously seen states a draw, and to limit recursion depth
Arena.py: Modified like Coach.py
script.py: Run ablation over numMCTSSims
