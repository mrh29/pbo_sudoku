import sys, math, random, subprocess, copy, argparse

# creates an array of length n with unique integers [1,n]
def unique_row(n):
    l = []
    row = []
    for i in range(n):
        l.append(i+1)
    while len(l):
        row.append(l.pop(int((random.random() * len(l)))))
    return row

''' 
square_rules:
    adds PBO constraints to s
    that ensures that each square only has one variable assigned 1
    i.e. each square should only have one number in the solution
'''
def square_rules(n, s, vars, num_constraints):
    s += '* square constraints\n'
    for i in range(n):
        for j in range(n):
            for k in range(n):
                s += '+1 ' + vars[i][j][k] + ' '
            s += ' = 1;\n'
            num_constraints += 1
    return s, num_constraints

'''
row_rules:
    adds PBO constraints to s
    that ensures each row has one of each value in [1,n]
'''
def row_rules(n, s, vars, num_constraints):
    s += '* row constraints\n'
    for i in range(n):
        for j in range(n):
            for k in range(n):
                s += '+1 ' + vars[i][k][j] + ' '
            s += ' = 1;\n'
            num_constraints += 1
    return s, num_constraints

'''
column_rules:
    adds PBO constraints to s
    that ensures each column has one of each value in [1,n]
'''
def column_rules(n, s, vars, num_constraints):
    s += '* column constraints\n'
    for i in range(n):
        for j in range(n):
            for k in range(n):
                s += '+1 ' + vars[k][i][j] + ' '
            s += ' = 1;\n'
            num_constraints += 1
    return s, num_constraints

'''
box_rules:
    adds PBO constraints to s
    that ensure each root(n) x root(n) box is unique
'''
def box_rules(n, s, vars, num_constraints):
    root = int(math.sqrt(n))
    s += '* box constraints\n'
    constraints = {}
    # for each box
    for r in range(0, n, root):
        constraints[r] = {}
        for c in range(0, n, root):
            constraints[r][c] = {}
            for i in range(root):
                for j in range(root):
                    for k in range(n):
                        if i == 0 and j == 0:
                            constraints[r][c][k] = '+1 ' + vars[r + i][c + j][k] + ' '
                        else:
                            constraints[r][c][k] += '+1 ' + vars[r + i][c + j][k] + ' '
    
    for r in range(0, n, root):
        for c in range(0, n, root):
            for k in range(n):
                s += constraints[r][c][k] + ' = 1;\n'
                num_constraints += 1
    return s, num_constraints


'''
diag_rules:
    adds PBO constraints to s
    that ensure unique diagonals
'''
def diag_rules(n, s, vars, num_constraints):
    s += '* diagonal constraints\n'
    down = {}
    up = {}
    for i in range(n):
        down[i] = ''
        up[i] = ''
    
    for i in range(n):
        for j in range(n):
            if i == j:
                for k in range(n):
                    down[k] += '+1 ' + vars[i][j][k] + ' '
            if i + j + 1 == n:
                for k in range(n):
                    up[k] += '+1 ' + vars[i][j][k] + ' '
    
    for i in range(n):
        s += down[i] + ' = 1;\n'
        s += up[i] + ' = 1;\n'
        num_constraints += 2
    return s, num_constraints

'''
sudoku_constraints:
    construct a PBO problem that represents
    the constraints for a sudoku puzzle
    if diag == True, makes this a puzzle w/ unique diagonals
'''
def sudoku_constraints(n, diag, vars):
    s = ''
    num_constraints = 0
    s, num_constraints = square_rules(n, s, vars, num_constraints)
    s,num_constraints =row_rules(n, s, vars, num_constraints)
    s,num_constraints = column_rules(n, s, vars, num_constraints)
    s,num_constraints = box_rules(n, s, vars, num_constraints)
    if diag:
        s,num_constraints = diag_rules(n, s, vars, num_constraints)
    return s, num_constraints


'''
parse_solution:
    given an opb solution of form x1 x2 x3 ... xn in string form
    returns a dictionary mapping variables to their value in the solution
'''
def parse_solution(sol):
    d = {}
    # it should always produce a solution
    index = sol.find('s')
    if index == -1:
        return d
    
    sol = sol[index:]
    sol = sol[sol.find('v'):]
    vars = sol.split(' ')
    for var in vars:
        d[var.strip('-')] = var.find('-') == -1
    
    count = 0
    for k,v in d.items():
        if v:
            count += 1
    return d

'''
construct_puzzle:
    given a mapping from vars to their ooolean value
    in a solution construct the sudoku puzzle
'''
def construct_puzzle(n, vars, solution):
    s = []
    for i in range(n):
        s.append([])
        for j in range(n):
            for k in range(n):
                if solution[vars[i][j][k]]:
                    s[i].append(k + 1)
    return s

'''
check_sudoku:
    checks if the list of lists is a valid sudoku puzzle
'''
def check_sudoku(l):
    # check rows/columns O(n^3)
    for i in range(len(l)):
        if len(set(l[i])) != len(l):
            return False
        for j in range(len(l[i])):
            for k in range(len(l)):
                if i != k and l[i][j] == l[k][j]:
                    return False
    
    # check boxes O(n^2)
    root = int(math.sqrt(len(l)))
    top_left_row, top_left_col = 0,0
    box_set = set([])
    count = 0
    for m in range(root):
        for n in range(root):
            for i in range(root):
                for j in range(root):
                    if l[i + top_left_row][top_left_col] != 0:
                        box_set.add(l[i + top_left_row][j + top_left_col])
                        count += 1
            if len(box_set) != len(l):
                return False
            box_set = set([])
            top_left_col += root
        top_left_col = 0
        top_left_row += root
    return True

'''
solver:
    given an n x n array solve it as a sudoku puzzle
    assumes any value not in [1,n] is unsolved
    returns a solution iff the puzzle has that as its unique solution
'''
def solver(n, diag, puzzle, solver_invocation):
    

    # constructing a mapping from (colum,row,number) -> PBO variable
    vars = {}
    var_count = 1
    for i in range(n):
        vars[i] = {}
        for j in range(n):
            vars[i][j] = {}
            for k in range(n):
                vars[i][j][k] = 'x{}'.format(var_count)
                var_count += 1

    
    s, num_constraints = sudoku_constraints(n, diag, vars)

    solved = set([])

    # for every row
    s += '* solved squares\n'
    for r in range(n):
        # for every column
        for c in range(n):
            # we have a number
            x = puzzle[r][c]
            if x > 0 and x < n + 1:
                s += '+1 {} = 1;\n'.format(vars[r][c][x-1])
                solved.add(vars[r][c][x-1])
                num_constraints += 1
    
    coefs = [int ((int(random.random() * 100) + 1) * (random.random() + 1)) for i in range(n * n * n)]
    multiplier = [ (-1) ** int(random.random() * 2) for i in range(n * n * n)]
    for i in range(n):
        # if coef[i] == 0, then solution may not be unique w.r.t. var[i]
        assert(coefs[i] != 0)
        coefs[i] *= multiplier[i]

    # we could be more careful and remove variables
    # that have constrained values (i.e. xn = 1; is a constraint), 
    # but they cannot impact the optimization, so for completeness we add them
    o_func = 'min: '
    for i in range(n * n * n):
        o_func += '{} x{} '.format(coefs[i], i + 1)
    o_func += ';\n'
    
    with open('sudoku.opb', 'w') as f:
        f.write('* #variable= {} #constraint= {}\n'.format(var_count, num_constraints))
        f.write(o_func)
        f.write(s)
    
    status, output = subprocess.getstatusoutput(solver_invocation + ' sudoku.opb')
    
    result = parse_solution(output)
    sudoku = construct_puzzle(n, vars, result)

    # reverse the objective function (now finding the max of f)
    for i in range(n * n * n):
        coefs[i] *= -1
    
    o_func = 'min: '
    for i in range(n * n * n):
        o_func += '{} x{} '.format(coefs[i], i+1)
    o_func += ';\n'

    with open('sudoku2.opb', 'w') as f:
        f.write('* #variable= {} #constraint= {}\n'.format(var_count, num_constraints))
        f.write(o_func)
        f.write(s)
    
    status, output = subprocess.getstatusoutput(solver_invocation + ' sudoku2.opb')
    
    result = parse_solution(output)
    sudoku2 = construct_puzzle(n, vars, result)

    # if minimizing and maximizing f gives the same result, f must have a unique solution w.r.t. variables
    if sudoku == sudoku2:
        return sudoku

    return []

def main():
    # parsing our argument options
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', help='size of the sudoku puzzle', default=9)
    parser.add_argument('--difficulty', help='puzzle difficulty', default='easy')
    parser.add_argument('--diag', help='toggle diagonal constraints', action='store_true')
    parser.add_argument('--solver', help='solver invocation', required=True)
    args = parser.parse_args()
    n = int(args.n)
    root = int(math.sqrt(n))
    if root * root != n:
        print('Must provide a square number (defaulting to 9)')
        n = 9
        root = 3

    # change the number of removed squares based on difficulty
    num_holes = 0
    if args.difficulty == 'hard':
        num_holes = float('inf')
    elif args.difficulty == 'medium':
        num_holes = 50
    else:
        num_holes = 46


    # construct our mapping from (row,col,number) -> PBO variable
    num_vars = 1
    d = {}
    for i in range(n):
        d[i] = {}
        for j in range(n):
            d[i][j] = {}
            for k in range(n):
                d[i][j][k] = 'x{}'.format(num_vars)
                num_vars += 1
            
    s, num_constraints = sudoku_constraints(n, args.diag, d)

    r = unique_row(n)
    s += '* first row\n'
    for i in range(len(r)):
        s += '+1 ' + d[0][i][r[i] - 1] + ' = 1;\n'
        num_constraints += 1

    # We want more randomness than just the first row
    # but we don't want to restrict our solution space with extra constraints
    # so we use a random objective function
    coefs = [int (int(random.random() * 100) + 1 * (random.random() + 1)) for i in range(n * n)]
    multiplier = [ (-1) ** int(random.random() * 2) for i in range(n * n)]
    for i in range(n):
        coefs[i] *= multiplier[i]

    o_func = 'min: '
    for i in range(n * n):
        o_func += '{} x{} '.format(coefs[i], int(random.random() * (num_vars - 1)) + 1 + (n * n)) # n * n to avoid variables in the solved first row
    o_func += ';\n'


    with open('solution.opb', 'w') as f:
        f.write('* #variable= {} #constraint= {}\n'.format(num_vars - 1, num_constraints))
        f.write(o_func)
        f.write(s)
    
    status, output = subprocess.getstatusoutput(args.solver + ' solution.opb')
    
    result = parse_solution(output)
    sudoku = construct_puzzle(n, d, result)
    solution = copy.deepcopy(sudoku)
    assert(solution == sudoku)
    assert(check_sudoku(sudoku))
    with open('solution.txt', 'w') as f:
        f.write('{} x {} Sudoku Puzzle (solution):\n====================\n'.format(n,n))
        for i in range(n):
            for j in range(n):
                f.write('{} '.format(sudoku[i][j]))
                if (j + 1) % root == 0:
                        f.write('| ')
            f.write('\n')
            if (i + 1) % root == 0:
                f.write('====================\n')
    
    last_removed = [(0,0,0),(0,0,0)]
    removed = 0
    counts = [n] * n
    row_counts = [n] * n
    col_counts = [n] * n
    box_counts = [n] * n

    coords = [(i,j) for i in range(n) for j in range(n)]
    while removed < num_holes and len(coords) > 0:
        j,k = coords.pop(int(random.random() * len(coords)))
        box_num = (root * (j // root)) + (k // root)
        tmp = sudoku[j][k]
        if counts[tmp - 1] > 2 and col_counts[k] > 1 and row_counts[j] > 1 and box_counts[box_num] > 2:
            sudoku[j][k] = 0
            if solver(n, args.diag, sudoku, args.solver) != solution:
                sudoku[j][k] = tmp
            else:
                counts[tmp - 1] -= 1
                removed += 1
                row_counts[j] -= 1
                col_counts[k] -= 1
                box_counts[box_num] -= 1
    
    puzzle = solver(n, args.diag, sudoku, args.solver)
    if puzzle == []:
        for i in range(n):
            print(sudoku[i])
        print(counts)
        assert(puzzle != [])
    if puzzle != solution:
        for i in range(n):
            print(puzzle[i], solution[i])
    assert(puzzle == solution)
    
    with open('puzzle.txt', 'w') as f:
        f.write('{} x {} Sudoku Puzzle:\n====================\n'.format(n,n))
        for i in range(n):
            for j in range(n):
                f.write('{} '.format(sudoku[i][j]))
                if (j + 1) % root == 0:
                    f.write('| ')
            f.write('\n')
            if (i + 1) % root == 0:
                f.write('====================\n')
    
    subprocess.check_call('rm sudoku.opb sudoku2.opb solution.opb', shell=True)

if __name__ == '__main__':
    main()