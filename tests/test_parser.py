import pytest
from parser import parser
from textwrap import dedent


def normalize(text):
    return dedent(text).strip() + "\n"


def test_simple_declaration():
    code = "int x\n"
    result = parser.parse(code)
    assert result == [("declare", "int", "x")]


def test_multiple_declarations():
    code = """
    int x
    str y
    """
    result = parser.parse(normalize(code))
    assert result == [("declare", "int", "x"), ("declare", "str", "y")]


def test_assignment():
    code = "x = 42\n"
    result = parser.parse(code)
    assert result == [("assign", "x", "=", ("integer", "42"))]


def test_compound_assignment():
    operators = ["+=", "-=", "*=", "/=", "%=", "**="]
    for op in operators:
        code = f"x {op} 5\n"
        result = parser.parse(code)
        assert result == [("assign", "x", op, ("integer", "5"))]


def test_declare_assign():
    code = "int x = 42\n"
    result = parser.parse(code)
    assert result == [("declare_assign", "int", "x", ("integer", "42"))]


def test_enum_declaration():
    code = "enum Color { RED, GREEN, BLUE }\n"
    result = parser.parse(code)
    assert result == [("enum_declare", "Color", ["RED", "GREEN", "BLUE"])]


def test_function_declaration():
    code = """
    int add(int x, int y):
        return x
    """
    result = parser.parse(normalize(code))
    assert result == [
        (
            "func_declare",
            "int",
            "add",
            [("declare", "int", "x"), ("declare", "int", "y")],
            [("return", ("id", "x"))],
        )
    ]


def test_array_literals():
    code = "x = [1, 2, 3]\n"
    result = parser.parse(code)
    assert result == [
        (
            "assign",
            "x",
            "=",
            ("array_lit", [("integer", "1"), ("integer", "2"), ("integer", "3")]),
        )
    ]


def test_array_indexing():
    code = "x = arr[0]\n"
    result = parser.parse(code)
    assert result == [("assign", "x", "=", ("index", ("id", "arr"), ("integer", "0")))]


def test_binary_operations():
    operators = ["+", "-", "*", "/", "%", "**"]
    for op in operators:
        code = f"x = a {op} b\n"
        result = parser.parse(code)
        assert result == [("assign", "x", "=", ("binop", op, ("id", "a"), ("id", "b")))]


def test_logical_operations():
    code = """
    x = !true
    y = a && b
    z = a || b
    """
    result = parser.parse(normalize(code))
    assert result == [
        ("assign", "x", "=", ("logic_not", ("boolean", "true"))),
        ("assign", "y", "=", ("logic_and", ("id", "a"), ("id", "b"))),
        ("assign", "z", "=", ("logic_or", ("id", "a"), ("id", "b"))),
    ]


def test_comparison_operations():
    operators = ["==", "!=", "<", ">", "<=", ">="]
    for op in operators:
        code = f"x = a {op} b\n"
        result = parser.parse(code)
        assert result == [("assign", "x", "=", ("comop", op, ("id", "a"), ("id", "b")))]


def test_function_calls():
    code = "result = add(x, y)\n"
    result = parser.parse(code)
    assert result == [
        ("assign", "result", "=", ("func_call", "add", [("id", "x"), ("id", "y")]))
    ]


def test_type_casting():
    code = "x = (int)y\n"
    result = parser.parse(code)
    assert result == [("assign", "x", "=", ("cast", "int", ("id", "y")))]


def test_string_literals():
    code = 'x = "hello"\n'
    result = parser.parse(code)
    assert result == [("assign", "x", "=", ("string", "hello"))]


def test_boolean_literals():
    code = """
    x = true
    y = false
    """
    result = parser.parse(normalize(code))
    assert result == [
        ("assign", "x", "=", ("boolean", "true")),
        ("assign", "y", "=", ("boolean", "false")),
    ]


def test_double_literals():
    code = "x = 3.14\n"
    result = parser.parse(code)
    assert result == [("assign", "x", "=", ("doublel", "3.14"))]


def test_when_statement():
    code = """
    when x:
        return 1
    when y:
        return 2
    default:
        return 3
    """
    result = parser.parse(normalize(code))
    assert result == [
        (
            "when_stmt",
            [
                ("when", ("id", "x"), [("return", ("integer", "1"))]),
                ("when", ("id", "y"), [("return", ("integer", "2"))]),
                ("when_default", [("return", ("integer", "3"))]),
            ],
        )
    ]


def test_until_statement():
    code = """
    until x > 10:
        x += 1
    """
    result = parser.parse(normalize(code))
    assert result == [
        (
            "until",
            ("comop", ">", ("id", "x"), ("integer", "10")),
            [("assign", "x", "+=", ("integer", "1"))],
        )
    ]


def test_loop_statement():
    code = """
    loop int i in 1..10:
        x += i
    """
    result = parser.parse(normalize(code))
    assert result == [
        (
            "loop",
            ("declare", "int", "i"),
            ("range", ("integer", "1"), ("integer", "10")),
            [("assign", "x", "+=", ("id", "i"))],
        )
    ]


def test_conditional_operator():
    code = "x = condition ? value1 ! value2\n"
    result = parser.parse(code)
    assert result == [
        (
            "assign",
            "x",
            "=",
            ("conop", ("id", "condition"), ("id", "value1"), ("id", "value2")),
        )
    ]


def test_array_type_declaration():
    code = """
    int[] numbers
    str[][] matrix
    """
    result = parser.parse(normalize(code))
    assert result == [
        ("declare", ("array", "int"), "numbers"),
        ("declare", ("array", ("array", "str")), "matrix"),
    ]
