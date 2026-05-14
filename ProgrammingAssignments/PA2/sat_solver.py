"""PA2 starter: implement a SAT solver for CNF formulas.

Clauses are lists of integer literals. For example:
  [1, -3, 4] means x1 OR not x3 OR x4.

Assignments are dictionaries from positive variable numbers to booleans.
"""

from __future__ import annotations

import ast
import sys


def literal_variable(literal):
    """Return the variable number appearing in a literal."""
    return abs(literal)


def literal_required_value(literal):
    """Return the value that makes a literal true."""
    return literal > 0


def evaluate_literal(literal, assignment):
    """Evaluate one literal under a partial assignment."""
    variable = literal_variable(literal)
    if variable not in assignment:
        return None
    return assignment[variable] == literal_required_value(literal)


def simplify(clauses, assignment):
    """Simplify clauses under a partial assignment.

    Clauses that are already true disappear. Literals that are already false are
    removed from their clauses. If a clause becomes empty, the current partial
    assignment cannot lead to a solution.
    """
    simplified = []
    for clause in clauses:
        new_clause = []
        clause_satisfied = False

        for literal in clause:
            value = evaluate_literal(literal, assignment)
            if value is True:
                clause_satisfied = True
                break
            if value is None:
                new_clause.append(literal)

        if clause_satisfied:
            continue
        if len(new_clause) == 0:
            # Contradiction: clause is empty and not satisfied
            return None
        simplified.append(new_clause)

    return simplified


def unit_propagate(clauses, assignment):
    """Repeatedly apply unit clauses.

    A unit clause is a clause with exactly one literal. To satisfy the formula,
    that literal must be true.
    """
    while True:
        # Simplify the formula with the current assignment
        simplified = simplify(clauses, assignment)
        
        # If simplify returns None, we've reached a contradiction
        if simplified is None:
            return None
        
        # Look for a unit clause (a clause of length 1)
        unit_clause = None
        for clause in simplified:
            if len(clause) == 1:
                unit_clause = clause
                break
        
        # If no unit clauses are found, we are done with propagation
        if unit_clause is None:
            return simplified
        
        # Force the variable assignment required by the unit clause
        literal = unit_clause[0]
        var = literal_variable(literal)
        val = literal_required_value(literal)
        
        # Add to assignment and repeat the loop to check for new unit clauses
        assignment[var] = val


def choose_variable(clauses, assignment):
    """Choose an unassigned variable to branch on."""
    for clause in clauses:
        for literal in clause:
            variable = literal_variable(literal)
            if variable not in assignment:
                return variable
    return None


def sat_solve(clauses, assignment):
    """Solve SAT for a CNF formula by extending the given partial assignment."""
    
    # 1. Run unit propagation (this modifies assignment in-place)
    # We work on a copy of the assignment to avoid corrupting previous recursive steps
    current_assignment = assignment.copy()
    simplified = unit_propagate(clauses, current_assignment)
    
    # 2. If propagation finds a contradiction, return None
    if simplified is None:
        return None
    
    # 3. If no clauses remain, the formula is satisfied!
    if not simplified:
        return current_assignment
    
    # 4. Choose a variable to branch on
    var = choose_variable(simplified, current_assignment)
    if var is None:
        return current_assignment # All variables assigned
        
    # 5. Recursively try True, then False (Backtracking)
    for value in [True, False]:
        # Branch with the chosen value
        new_assignment = current_assignment.copy()
        new_assignment[var] = value
        
        result = sat_solve(simplified, new_assignment)
        if result is not None:
            return result
            
    return None


def print_result(assignment):
    """Print the SAT result using the assignment handout format."""
    print(f'satisfiable: {str(assignment is not None).lower()}')
    print(f'assignment: {assignment}')


def main():
    """Run the solver from the command line on a CNF formula."""
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    try:
        clauses = ast.literal_eval(raw)
        print_result(sat_solve(clauses, {}))
    except (ValueError, SyntaxError):
        print("Error: Invalid CNF input format.")


if __name__ == '__main__':
    main()
