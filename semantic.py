class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Stack of scopes, starting with global scope

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, type_):
        if name in self.scopes[-1]:
            raise SemanticError(f"Variable {name} already declared in current scope")
        self.scopes[-1][name] = type_

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variable {name} not declared")


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function = None

    def analyze(self, ast):
        """Main entry point for semantic analysis"""
        for node in ast:
            self.analyze_node(node)

    def analyze_node(self, node):
        if not isinstance(node, tuple):
            return

        node_type = node[0]

        # Dispatch to appropriate handler method
        method_name = f"analyze_{node_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            raise SemanticError(f"Unknown node type: {node_type}")

    def analyze_declare(self, node):
        _, type_, name = node
        self.symbol_table.declare(name, type_)

    def analyze_declare_assign(self, node):
        _, type_, name, expr = node
        expr_type = self.analyze_node(expr)
        if not self.type_compatible(type_, expr_type):
            raise SemanticError(f"Type mismatch: cannot assign {expr_type} to {type_}")
        self.symbol_table.declare(name, type_)

    def analyze_assign(self, node):
        _, name, op, expr = node
        var_type = self.symbol_table.lookup(name)
        expr_type = self.analyze_node(expr)
        if not self.type_compatible(var_type, expr_type):
            raise SemanticError(
                f"Type mismatch in assignment: {expr_type} cannot be assigned to {var_type}"
            )

    def analyze_func_declare(self, node):
        _, return_type, name, params, body = node
        self.symbol_table.declare(
            name, ("function", return_type, [p[1] for p in params])
        )

        # Create new scope for function body
        self.symbol_table.enter_scope()
        self.current_function = return_type

        # Declare parameters in new scope
        for param in params:
            self.analyze_node(param)

        # Analyze function body
        for stmt in body:
            self.analyze_node(stmt)

        self.current_function = None
        self.symbol_table.exit_scope()

    def analyze_return(self, node):
        if len(node) == 1:  # return without expression
            expr_type = "void"
        else:
            expr_type = self.analyze_node(node[1])

        if self.current_function is None:
            raise SemanticError("Return statement outside function")

        if not self.type_compatible(self.current_function, expr_type):
            raise SemanticError(
                f"Return type mismatch: expected {self.current_function}, got {expr_type}"
            )

    def analyze_func_call(self, node):
        _, name, args = node
        func_type = self.symbol_table.lookup(name)
        if not isinstance(func_type, tuple) or func_type[0] != "function":
            raise SemanticError(f"{name} is not a function")

        if len(args) != len(func_type[2]):
            raise SemanticError(f"Wrong number of arguments for function {name}")

        for arg, param_type in zip(args, func_type[2]):
            arg_type = self.analyze_node(arg)
            if not self.type_compatible(param_type, arg_type):
                raise SemanticError(
                    f"Argument type mismatch: expected {param_type}, got {arg_type}"
                )

        return func_type[1]  # Return type

    def analyze_binop(self, node):
        _, op, left, right = node
        left_type = self.analyze_node(left)
        right_type = self.analyze_node(right)

        if not self.type_compatible(left_type, right_type):
            raise SemanticError(
                f"Type mismatch in binary operation: {left_type} {op} {right_type}"
            )

        return self.result_type(op, left_type, right_type)

    def analyze_id(self, node):
        _, name = node
        return self.symbol_table.lookup(name)

    def analyze_integer(self, node):
        return "int"

    def analyze_string(self, node):
        return "str"

    def analyze_boolean(self, node):
        return "bool"

    def analyze_doublel(self, node):
        return "double"

    def type_compatible(self, expected, actual):
        """Check if actual type can be assigned to expected type"""
        if expected == actual:
            return True

        # Add type conversion rules here
        # For example: int can be assigned to double
        if expected == "double" and actual == "int":
            return True

        return False

    def result_type(self, op, left_type, right_type):
        """Determine result type of binary operations"""
        if op in ["+", "-", "*", "/"]:
            if left_type == "double" or right_type == "double":
                return "double"
            return "int"
        elif op in ["==", "!=", "<", ">", "<=", ">="]:
            return "bool"
        elif op == "&&" or op == "||":
            if left_type == "bool" and right_type == "bool":
                return "bool"
            raise SemanticError(f"Logical operators require boolean operands")

        raise SemanticError(f"Unknown operator: {op}")

    def analyze_enum_declare(self, node):
        _, name, items = node
        self.symbol_table.declare(name, "enum")
        for item in items:
            self.symbol_table.declare(item, name)

    def analyze_array_lit(self, node):
        _, items = node
        item_types = [self.analyze_node(item) for item in items]
        if not all(t == item_types[0] for t in item_types):
            raise SemanticError("Array elements must be of the same type")
        return f"array[{item_types[0]}]"

    def analyze_index(self, node):
        _, array, index = node
        array_type = self.analyze_node(array)
        index_type = self.analyze_node(index)
        if not array_type.startswith("array["):
            raise SemanticError("Indexing is only supported on arrays")
        if index_type != "int":
            raise SemanticError("Array index must be an integer")
        return array_type[6:-1]  # Return the type of the array elements

    def analyze_spread(self, node):
        _, expr = node
        expr_type = self.analyze_node(expr)
        if not expr_type.startswith("array["):
            raise SemanticError("Spread operator is only supported on arrays")
        return expr_type

    def analyze_modifier(self, node):
        _, expr = node
        return self.analyze_node(expr)

    def analyze_pass(self, node):
        pass  # No semantic checks needed for pass statement

    def analyze_when_stmt(self, node):
        _, blocks = node
        for block in blocks:
            self.analyze_node(block)

    def analyze_loop(self, node):
        _, var_decl, iterable, body = node
        self.analyze_node(var_decl)
        iterable_type = self.analyze_node(iterable)
        if not iterable_type.startswith("array["):
            raise SemanticError("Loop iterable must be an array")
        self.symbol_table.enter_scope()
        self.analyze_node(body)
        self.symbol_table.exit_scope()

    def analyze_until(self, node):
        _, condition, body = node
        condition_type = self.analyze_node(condition)
        if condition_type != "bool":
            raise SemanticError("Until condition must be a boolean")
        self.symbol_table.enter_scope()
        self.analyze_node(body)
        self.symbol_table.exit_scope()

    def analyze_unary(self, node):
        _, op, operand = node
        operand_type = self.analyze_node(operand)
        if op in ["++", "--"]:
            if operand_type != "int":
                raise SemanticError(f"Unary operator {op} requires integer operand")
            return "int"
        raise SemanticError(f"Unknown unary operator: {op}")

    def analyze_logic_not(self, node):
        _, expr = node
        expr_type = self.analyze_node(expr)
        if expr_type != "bool":
            raise SemanticError("Logical NOT operator requires boolean operand")
        return "bool"

    def analyze_logic_and(self, node):
        _, left, right = node
        left_type = self.analyze_node(left)
        right_type = self.analyze_node(right)
        if left_type != "bool" or right_type != "bool":
            raise SemanticError("Logical AND operator requires boolean operands")
        return "bool"

    def analyze_logic_or(self, node):
        _, left, right = node
        left_type = self.analyze_node(left)
        right_type = self.analyze_node(right)
        if left_type != "bool" or right_type != "bool":
            raise SemanticError("Logical OR operator requires boolean operands")
        return "bool"

    def analyze_comop(self, node):
        _, op, left, right = node
        left_type = self.analyze_node(left)
        right_type = self.analyze_node(right)
        if not self.type_compatible(left_type, right_type):
            raise SemanticError(f"Type mismatch in comparison: {left_type} {op} {right_type}")
        return "bool"

    def analyze_conop(self, node):
        _, condition, true_expr, false_expr = node
        condition_type = self.analyze_node(condition)
        true_type = self.analyze_node(true_expr)
        false_type = self.analyze_node(false_expr)
        if condition_type != "bool":
            raise SemanticError("Conditional operator requires boolean condition")
        if not self.type_compatible(true_type, false_type):
            raise SemanticError(f"Type mismatch in conditional operator: {true_type} vs {false_type}")
        return true_type

    def analyze_cast(self, node):
        _, target_type, expr = node
        expr_type = self.analyze_node(expr)
        # Add casting rules here if needed
        return target_type

    def analyze_range(self, node):
        _, start, end = node
        start_type = self.analyze_node(start)
        end_type = self.analyze_node(end)
        if start_type != "int" or end_type != "int":
            raise SemanticError("Range bounds must be integers")
        return "range"
