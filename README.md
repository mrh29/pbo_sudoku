# Sudoku Generation by Constraint Solving

This repository contains a single python script for generating sudoku puzzles via constraint solving. 

It can be run with the following command where solver is a required command-line argumet for how to invoke your solver:
```
python sudoku.py --solver="solver invocation"
```

This will generate two text files: puzzle.txt and solution.txt. puzzle.txt is a sudoku puzzle to be
solved (with 0s representing squares to be solved). solution.txt is the unique solution to the puzzle.

### Arguments

_--solver:string_ — the invocation of your solver from the command line (make sure it prints the solution)

_--difficulty:easy|medium|hard_ — the difficulty of the generated puzzle

_--diag_ — if provided, the resulting puzzle with have diagonals with only value in [1,n]

_--n:int_ — generates an n x n sudoku puzzle
