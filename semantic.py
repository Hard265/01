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
