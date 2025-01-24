import ply.yacc as yacc
from lexer import tokens


def p_program(p):
    """program : stmts"""
    p[0] = p[1]


def p_stmts(p):
    """
    stmts : stmt
          | stmts stmt
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_stmt(p):
    """
    stmt : simple_stmt NEWLINE
         | compound_stmt
    """
    p[0] = p[1]


def p_simple_stmt(p):
    """
    simple_stmt : declare
                | assign
                | declare_assign
                | enum_declare
                | return_stmt
                | pass_stmt
    """
    p[0] = p[1]


def p_compound_stmt(p):
    """
    compound_stmt : func_declare
                  | when_stmt
                  | loop_stmt
                  | until_stmt
                  | struct
                  | struct_constructor
    """
    p[0] = p[1]


def p_declare(p):
    """declare : type ID"""
    p[0] = ("declare", p[1], p[2])


def p_assign(p):
    """assign : ID assign_op expr"""
    p[0] = ("assign", p[1], p[2], p[3])


def p_assign_op(p):
    """
    assign_op : EQUALS
              | PLUS_EQUALS
              | MINUS_EQUALS
              | STAR_EQUALS
              | SLASH_EQUALS
              | MOD_EQUALS
              | DOUBLE_STAR_EQUALS
    """
    p[0] = p[1]


def p_declare_assign(p):
    """declare_assign : type ID EQUALS expr"""
    p[0] = ("declare_assign", p[1], p[2], p[4])


def p_lambda_func(p):
    """
    lambda_func : LPAR params RPAR ARROW expr
    """
    p[0] = ("lambda_func", p[1], p[3])


def p_enum_declare(p):
    """enum_declare : ENUM ID LBRACE enum_items RBRACE"""
    p[0] = ("enum_declare", p[2], p[4])


def p_enum_items(p):
    """
    enum_items :
               | ID
               | enum_items COMMA ID
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_array_lit(p):
    """
    expr : LBRACKET array_items  RBRACKET
    """
    p[0] = ("array_lit", p[2])


def p_array_items(p):
    """
    array_items :
                | expr
                | expr COMMA  array_items
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_index(p):
    """
    expr : expr LBRACKET expr RBRACKET
    """
    p[0] = ("index", p[1], p[3])


def p_spread(p):
    """
    expr : STAR expr
    """
    p[0] = ("spread", p[2])


def p_modifier(p):
    """
    modifier : AT expr
    """
    p[0] = ("modifier", p[2])


def p_pass_stmt(p):
    """
    pass_stmt : PASS
    """
    p[0] = ("pass",)


def p_return_stmt(p):
    """
    return_stmt : RETURN
                | RETURN expr
    """
    if len(p) == 1:
        p[0] = ("return",)
    else:
        p[0] = ("return", p[2])


def p_block(p):
    """
    block : NEWLINE INDENT stmts DEDENT
    """
    p[0] = p[3]


def p_func_declare(p):
    """
    func_declare : type ID LPAR params RPAR COLON block
    """
    p[0] = ("func_declare", p[1], p[2], p[4], p[7])


def p_struct(p):
    """
    struct : STRUCT ID COLON block
           | STRUCT ID EXTENDS ID COLON block
    """
    if len(p) == 5:
        p[0] = ("struct", p[2], [], p[4])
    else:
        p[0] = ("struct", p[2], [p[4]], p[6])


def p_struct_constructor(p):
    """
    struct_constructor : LPAR params RPAR COLON block
    """
    p[0] = ("struct_ctor", p[2], p[5])


def p_when_stmt(p):
    """
    when_stmt : when_blocks
              | when_blocks default_block
    """
    if len(p) == 2:
        p[0] = ("when_stmt", p[1])
    else:
        p[0] = ("when_stmt", p[1] + [p[2]])


def p_when_blocks(p):
    """
    when_blocks : when_block
                | when_blocks when_block
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_when_block(p):
    """
    when_block : WHEN expr COLON block
    """
    p[0] = ("when", p[2], p[4])


def p_default_block(p):
    """
    default_block : DEFAULT COLON block
    """
    p[0] = ("when_default", p[3])


def p_loop_stmt(p):
    """
    loop_stmt : LOOP declare IN expr COLON block
    """
    p[0] = ("loop", p[2], p[4], p[6])


def p_until_stmt(p):
    """
    until_stmt : UNTIL expr COLON block
    """
    p[0] = ("until", p[2], p[4])


def p_expr_func_call(p):
    """
    expr : ID LPAR args RPAR
    """
    p[0] = ("func_call", p[1], p[3])


def p_expr_binop(p):
    """
    expr : expr PLUS expr
         | expr MINUS expr
         | expr SLASH expr
         | expr STAR expr
         | expr MOD expr
         | expr DOUBLE_STAR expr
    """
    p[0] = ("binop", p[2], p[1], p[3])


def p_expr_unary(p):
    """
    expr : DOUBLE_PLUS ID
         | DOUBLE_MINUS ID
    """
    p[0] = ("unary", p[1], p[2])


def p_expr_logic_not(p):
    """
    expr : EXCLAMATION expr
    """
    p[0] = ("logic_not", p[2])


def p_epxr_logic_and(p):
    """expr : expr DOUBLE_AMP expr"""
    p[0] = ("logic_and", p[1], p[3])


def p_epxr_logic_or(p):
    """expr : expr DOUBLE_VBAR expr"""
    p[0] = ("logic_or", p[1], p[3])


def p_expr_comop(p):
    """
    expr : expr EQ expr
         | expr NEQ expr
         | expr LT expr
         | expr GT expr
         | expr LTE expr
         | expr GTE expr
    """
    p[0] = ("comop", p[2], p[1], p[3])


def p_expr_conop(p):
    """expr : expr QUESTION expr EXCLAMATION expr"""
    p[0] = ("conop", p[1], p[3], p[5])


def p_expr_group(p):
    """expr : LPAR expr RPAR"""
    p[0] = p[2]


def p_expr_access(p):
    """expr : expr DOT expr"""
    p[0] = ("access", p[1], p[3])


def p_expr_integer(p):
    """expr : INTEGER"""
    p[0] = ("integer", p[1])


def p_expr_string(p):
    """expr : STRING"""
    p[0] = ("string", p[1])


def p_expr_boolean(p):
    """expr : BOOLEAN"""
    p[0] = ("boolean", p[1])


def p_expr_double(p):
    """expr : DOUBLEL"""
    p[0] = ("doublel", p[1])


def p_expr_id(p):
    """expr : ID"""
    p[0] = ("id", p[1])


def p_expr_cast(p):
    """expr : LPAR type RPAR expr"""
    p[0] = ("cast", p[2], p[4])


def p_expr_range(p):
    """expr : expr DOUBLE_DOT expr"""
    p[0] = ("range", p[1], p[3])


def p_params(p):
    """
    params :
           | param
           | params COMMA param
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_param(p):
    """
    param : declare
          | declare_assign
    """
    p[0] = p[1]


def p_args(p):
    """
    args :
         | expr
         | args COMMA expr
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_type(p):
    """
    type : primitive
         | composed
    """
    p[0] = p[1]


def p_type_primitive(p):
    """
    primitive : INT
              | STR
              | BOOL
              | DOUBLE
              | VOID
    """
    p[0] = p[1]


def p_type_composed(p):
    """
    composed : array
    """
    p[0] = p[1]


def p_array(p):
    """
    array : type LBRACKET RBRACKET
    """
    p[0] = ("array", p[1])


# TODO Implement dict type
def p_dict(p):
    """
    dict : LBRACE  RBRACE
    """


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")


def ensure_newline_at_end(data):
    if not data.endswith("\n"):
        return data + "\n"
    return data


parser = yacc.yacc()
parser_function = parser.parse
parser.parse = lambda data: parser_function(ensure_newline_at_end(data))
