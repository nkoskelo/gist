"""
    My parser. This will assume that you have a string of mathematical operations.
    We will also assume that the order of operations is PEMDAS.
"""

from enum import Enum
import numpy as np

RESERVED_PAIR_OPERATOR_SYMBOLS = ["+", "-", "/", "*", "^"]

class Sym(Enum):
    PLUS = 0
    MINUS = 1
    PRODUCT = 2
    DIVIDE = 3
    EXPONENT = 4


class Expression:

    def __init__(self) -> None:
        return
    
    def __add__(self, other):
        return Sum(self, other)
    
    def __mul__(self, other):
        return Product(self, other)
    
    def __sub__(self, other):
        return Sub(self, other)
    
    def __div__(self, other):
        return Div(self, other)
    
class Div(Expression):
    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return "Div(" + str(self.a) + str(", ") + str(self.b) + ")"
    
class Product(Expression):

    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return "Prod(" + str(self.a) + str(", ") + str(self.b) + ")"
    
class Sum(Expression):

    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return "Sum(" + str(self.a) + ", " + str(self.b) + ")"
    
class Sub(Expression):
    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a
        self.b = b
    def __repr__(self) -> str:
        return str(self.a) + str("-") + str(self.b)
    
class Exponent(Expression):
    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a
        self.b = b
    def __repr__(self) -> str:
        return str(self.a) + str("**") + str(self.b)


class Variable(Expression):
    def __init__(self, name, val) -> None:
        super().__init__()
        self.name = name
        try:
            self.val = float(val)
        except:
            self.val = val
    def __repr__(self) -> str:
        return str(self.val)
    
class ArrayAccess(Variable):
    def __init__(self, name, array_ind) -> None:
        super().__init__(name, array_ind)
        self.index = array_ind
    def __repr__(self) -> str:
        return "ArrayAccess(" + str(self.name) + ", " + str(self.index) + ")"

class Parens(Variable):
    def __init__(self, name, val) -> None:
        super().__init__(name, val)

def _parse_interior_known_right(my_str, right_expr: Expression,
                                 operator: str, op_ind: int) -> Expression:
    """
        Build the tree if you have the right expression.
    """
    if operator == "+":
        return right_expr + parse_string(my_str[:op_ind])
    elif operator == "-":
        return parse_string(my_str[:op_ind]) - right_expr
    elif operator == "^":
        return Exponent(parse_string(my_str[:op_ind]), right_expr)
    elif operator == "*":
        return right_expr * parse_string(my_str[:op_ind])
    elif operator == "/":
        return parse_string(my_str[:op_ind]) / right_expr
    raise ValueError("Operator: " + str(operator) + " not implemented")

def ind_of_next_operator(my_str, min_ind) -> tuple[int, str]:
    """
        Find the index of the operator when looking forwards.
    """
    ind = len(my_str)
    best_symbol = 0
    for sym in RESERVED_PAIR_OPERATOR_SYMBOLS:
        best = str.find(my_str,sym,min_ind,ind)
        if best < ind and best > 0:
            ind = best
            best_symbol = sym
            return ind, best_symbol # This will give us the first one that we find.
    return ind, best_symbol

def _parse_interior_known_left(my_str, left_expr: Expression, operator, op_ind) -> Expression:
    """
        Build the tree if you have the left expression.
    """
    if operator == "+":
        return left_expr + parse_string(my_str[op_ind:])
    elif operator == "-":
        return left_expr - parse_string(my_str[op_ind:])
    elif operator == "^":
        return Exponent(left_expr, parse_string(my_str[op_ind:]))
    elif operator == "*":
        return left_expr * parse_string(my_str[op_ind:])
    elif operator == "/":
        return left_expr / parse_string(my_str[op_ind:])
    raise ValueError("Operator: " + str(operator) + " not implemented")


def ind_of_prev_operator(my_str, max_ind) -> tuple[int, str]:
    """
        Find the index of the operator when looking backwards.
    """
    ind = 0
    best_symbol = 0
    for sym in RESERVED_PAIR_OPERATOR_SYMBOLS:
        best = str.rfind(my_str,sym,ind,max_ind)
        if best > ind and best > 0:
            ind = best
            best_symbol = sym
            return ind, best_symbol # This will give us the first one that we find.
    return ind, best_symbol

def find_next_close(my_str, open_sym, close_sym, open_ind) -> int:
    """
        Find the next time that we close the expression.
        Opens after an open increases the number of closes we need.
        -1 if we could not find a match.
        Otherwise int in the range of [open_ind + 1, len(my_str)]
    """
    close_ind = -1
    open_count = 1
    for ind,char in enumerate(my_str[open_ind + 1:]):
        if char == open_sym:
            open_count += 1
        elif char == close_sym:
            open_count -= 1
        if open_count == 0:
            close_ind = ind
            break # We are done.
    if close_ind > 0:
        return close_ind + open_ind + 1
    return close_ind

def parse_string(my_str) -> Expression:
    """
        Build an abstract syntax tree from the string.
    """
    
    my_str = str.replace(my_str," ", "") # Remove all the spaces.
    
    for ind, open_sym in enumerate(["(", "["]):
        # Handle the priority makers
        close_sym = [")", "]"][ind]
        open_ind = str.find(my_str, open_sym)
        if open_ind > -1: # Did not fail to find a paren.
            
            close_ind = find_next_close(my_str, open_sym, close_sym, open_ind)
            
            if close_ind >-1:
                
                prev_ind, symbol_left = ind_of_prev_operator(my_str, open_ind)
                next_ind, symbol_right = ind_of_next_operator(my_str, close_ind)
                    
                name = my_str[prev_ind+1:open_ind]
                if prev_ind == 0:
                    # We are on the left side of the operator.
                    name = my_str[prev_ind:open_ind]
                    if next_ind >= len(my_str):
                        val = parse_string(my_str[open_ind+1:close_ind])
                        if open_sym == "[":
                            return ArrayAccess(name, val) # It is a variable!
                        else:
                            return Variable(name, val)
                    return _parse_interior_known_left(my_str, parse_string(my_str[:next_ind]),
                                                    symbol_right, next_ind+1)
                else:
                    return _parse_interior_known_right(my_str, parse_string(my_str[prev_ind+1:]),
                                                    symbol_left, prev_ind)
            else:
                raise ValueError("My string did not contain a matching pair of brackets")


    ind, symbol_right = ind_of_next_operator(my_str, 0)
    if ind < len(my_str):
        return _parse_interior_known_left(my_str, parse_string(my_str[:ind]), symbol_right, ind+1)
    return Variable(str.strip(my_str), str.strip(my_str))


def evaluate_expression(my_expr, named_vals) -> float:
    """ Execute the expression as if the named_vals have the specified values.
    """

    if isinstance(my_expr, Sum):
        return evaluate_expression(my_expr.a, named_vals) + evaluate_expression(my_expr.b, named_vals)
    elif isinstance(my_expr, Sub):
        return evaluate_expression(my_expr.a, named_vals) - evaluate_expression(my_expr.b, named_vals)
    elif isinstance(my_expr, Div):
        return evaluate_expression(my_expr.a, named_vals) / evaluate_expression(my_expr.b, named_vals)
    elif isinstance(my_expr, Product):
        return evaluate_expression(my_expr.a, named_vals) * evaluate_expression(my_expr.b, named_vals)
    elif isinstance(my_expr, Exponent):
        return evaluate_expression(my_expr.a, named_vals) ** evaluate_expression(my_expr.b, named_vals)
    elif isinstance(my_expr, ArrayAccess):
        if my_expr.name in named_vals.keys():
            var = named_vals[my_expr.name]
            return var[int(evaluate_expression(my_expr.index, named_vals))]

    elif isinstance(my_expr, Variable):
        if my_expr.name in named_vals.keys():
            return named_vals[my_expr.name]
        else:
            return my_expr.val

def evaluate_expression_to_writeable_tree(my_expr, named_vals, tree,
                                          index: int=0, array_access_num: int=0):
    if not tree:
        tree = []
    start_var = "x"*(array_access_num+1)
    if index == 1:
        start_var ="y"*(array_access_num+1)
    elif index == 2:
        start_var = "z"*(array_access_num+1)
    if isinstance(my_expr, tuple([Sum, Sub, Product, Div, Exponent])):
        left = evaluate_expression_to_writeable_tree(my_expr.a, named_vals, tree, 1, array_access_num) # Left
        right = evaluate_expression_to_writeable_tree(my_expr.b, named_vals, tree, 2, array_access_num) # Right
        # Got the recusive calls. Now we need to work on the combine step.
        mid = ""
        op = ""
        if isinstance(my_expr, Sum):
            op = "+"
        elif isinstance(my_expr, Sub):
            op = "-"
        elif isinstance(my_expr, Product):
            op = "*"
        elif isinstance(my_expr, Div):
            op = "/"
        elif isinstance(my_expr, Exponent):
            op = "**"
        
        mid = start_var + " = " + ("y"*(array_access_num+1)) + str(op) + ("z"*(array_access_num+1))
        tmp = [mid] + [left] + [right]
        
        tree.extend(tmp)
        return tree
    elif isinstance(my_expr, ArrayAccess):
        if my_expr.name in named_vals.keys():
            interior = evaluate_expression_to_writeable_tree(my_expr.index, named_vals, tree,
                                                              index, array_access_num+1)
            tree.append(str(start_var) + " = " + str(my_expr.name) +
                         "[" + start_var + start_var[0] + "]") # add another char to match the array access.
            tree.append(my_expr.name + " = " + str(list(named_vals[my_expr.name]))) 
            # We will be reading backwards. So append the variable name after the access.
            tree.append(interior)
        return tree
    elif isinstance(my_expr, Variable):
        assign = str(my_expr.name)
        if my_expr.name in named_vals.keys():
            assign = str(named_vals[my_expr.name])
        tree.append(str(start_var) + " = " + assign)
        return tree
    
def tree_to_file(tree, file):

    for i in range(len(tree)-1,-1,-1): # backwards
        
        if isinstance(tree[i], list):
            tree_to_file(tree[i], file) # recursive call.
        else:
            file.write(tree[i] + "\n")
            # exec(tree[i]) # exec for statements and eval for expressions.
    
