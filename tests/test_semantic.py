import pytest
from semantic import SemanticAnalyzer, SemanticError


def test_simple_declaration():
    analyzer = SemanticAnalyzer()
    ast = [("declare", "int", "x")]
    analyzer.analyze(ast)
    assert analyzer.symbol_table.lookup("x") == "int"


def test_multiple_declarations():
    analyzer = SemanticAnalyzer()
    ast = [("declare", "int", "x"), ("declare", "str", "y")]
    analyzer.analyze(ast)
    assert analyzer.symbol_table.lookup("x") == "int"
    assert analyzer.symbol_table.lookup("y") == "str"


def test_assignment():
    analyzer = SemanticAnalyzer()
    ast = [("declare", "int", "x"), ("assign", "x", "=", ("integer", "42"))]
    analyzer.analyze(ast)
    assert analyzer.symbol_table.lookup("x") == "int"


def test_type_mismatch():
    analyzer = SemanticAnalyzer()
    ast = [("declare", "int", "x"), ("assign", "x", "=", ("string", "hello"))]
    with pytest.raises(SemanticError):
        analyzer.analyze(ast)


def test_function_declaration():
    analyzer = SemanticAnalyzer()
    ast = [
        (
            "func_declare",
            "int",
            "add",
            [("declare", "int", "x"), ("declare", "int", "y")],
            [("return", ("id", "x"))],
        )
    ]
    analyzer.analyze(ast)
    func_type = analyzer.symbol_table.lookup("add")
    assert func_type == ("function", "int", ["int", "int"])


def test_function_call():
    analyzer = SemanticAnalyzer()
    ast = [
        (
            "func_declare",
            "int",
            "add",
            [("declare", "int", "x"), ("declare", "int", "y")],
            [("return", ("id", "x"))],
        ),
        ("declare", "int", "result"),
        (
            "assign",
            "result",
            "=",
            ("func_call", "add", [("integer", "1"), ("integer", "2")]),
        ),
    ]
    analyzer.analyze(ast)
    assert analyzer.symbol_table.lookup("result") == "int"


def test_return_type_mismatch():
    analyzer = SemanticAnalyzer()
    ast = [
        (
            "func_declare",
            "int",
            "add",
            [("declare", "int", "x"), ("declare", "int", "y")],
            [("return", ("string", "hello"))],
        )
    ]
    with pytest.raises(SemanticError):
        analyzer.analyze(ast)


def test_enum_declare():
    analyzer = SemanticAnalyzer()
    ast = [("enum_declare", "Color", ["RED", "GREEN", "BLUE"])]
    analyzer.analyze(ast)
    assert analyzer.symbol_table.lookup("Color") == "enum"
    assert analyzer.symbol_table.lookup("RED") == "Color"


def test_index():
    analyzer = SemanticAnalyzer()
    ast = [("declare", "array[int]", "arr"), ("index", ("id", "arr"), ("integer", 0))]
    analyzer.analyze(ast)
    result = analyzer.analyze_node(ast[1])
    assert result == "int"


def test_spread():
    analyzer = SemanticAnalyzer()
    ast = [("declare", "array[int]", "arr"), ("spread", ("id", "arr"))]
    analyzer.analyze(ast)
    result = analyzer.analyze_node(ast[1])
    assert result == "array[int]"


def test_pass():
    analyzer = SemanticAnalyzer()
    ast = [("pass",)]
    result = analyzer.analyze(ast)
    assert result is None  # Pass statement should not affect analysis


# def test_when_stmt():
#     analyzer = SemanticAnalyzer()
#     ast = [("when_stmt", [("when", ("boolean", True), [("declare", "int", "x")])])]
#     analyzer.analyze(ast)
#     assert analyzer.symbol_table.lookup("x") == "int"


# def test_loop():
#     analyzer = SemanticAnalyzer()
#     ast = [
#         (
#             "loop",
#             ("declare", "int", "i"),
#             ("array_lit", [("integer", 1)]),
#             [("declare", "int", "x")],
#         )
#     ]
#     analyzer.analyze(ast)
#     assert analyzer.symbol_table.lookup("x") == "int"


# def test_until():
#     analyzer = SemanticAnalyzer()
#     ast = [("until", ("boolean", True), [("declare", "int", "x")])]
#     analyzer.analyze(ast)
#     assert analyzer.symbol_table.lookup("x") == "int"


# def test_unary():
#     analyzer = SemanticAnalyzer()
#     ast = [("unary", "++", ("id", "x"))]
#     with pytest.raises(SemanticError):
#         analyzer.analyze(ast)


# def test_logic_not():
#     analyzer = SemanticAnalyzer()
#     ast = [("logic_not", ("boolean", True))]
#     result = analyzer.analyze(ast)
#     assert result == "bool"


# def test_logic_and():
#     analyzer = SemanticAnalyzer()
#     ast = [("logic_and", ("boolean", True), ("boolean", False))]
#     result = analyzer.analyze(ast)
#     assert result == "bool"


# def test_logic_or():
#     analyzer = SemanticAnalyzer()
#     ast = [("logic_or", ("boolean", True), ("boolean", False))]
#     result = analyzer.analyze(ast)
#     assert result == "bool"


# def test_comop():
#     analyzer = SemanticAnalyzer()
#     ast = [("comop", "==", ("integer", 1), ("integer", 1))]
#     result = analyzer.analyze(ast)
#     assert result == "bool"


# def test_conop():
#     analyzer = SemanticAnalyzer()
#     ast = [("conop", ("boolean", True), ("integer", 1), ("integer", 0))]
#     result = analyzer.analyze(ast)
#     assert result == "int"


# def test_cast():
#     analyzer = SemanticAnalyzer()
#     ast = [("cast", "double", ("integer", 1))]
#     result = analyzer.analyze(ast)
#     assert result == "double"


# def test_range():
#     analyzer = SemanticAnalyzer()
#     ast = [("range", ("integer", 1), ("integer", 10))]
#     result = analyzer.analyze(ast)
#     assert result == "range"
