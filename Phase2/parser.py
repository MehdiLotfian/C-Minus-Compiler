import json
from copy import deepcopy
from terminals import Terminal
from nonterminals import NonTerminals
from anytree import Node, RenderTree


class Parser:
    def __init__(self, scanner):
        with open('first.json', 'r') as json_file:
            self.first = json.load(json_file)
        with open('follow.json', 'r') as json_file:
            self.follow = json.load(json_file)
        self.scanner = scanner
        self.token = self.scanner.get_next_token()
        self.lookahead = self.find_lookahead(self.token)
        self.root = None
        self.errored_root = None
        self.error_string = ""
        self.has_eof_error = False

    def get_syntax_errors_string(self):
        if len(self.error_string.replace("\n", "")) == 0:
            return "There is no syntax error."
        return self.error_string.strip()

    def get_tree(self):
        tree_string = ''
        if self.has_eof_error:
            for pre, fill, node in RenderTree(self.errored_root):
                tree_string += ("%s%s" % (pre, node.name) + '\n')
            return self.errored_root, tree_string
        for pre, fill, node in RenderTree(self.root):
            tree_string += ("%s%s" % (pre, node.name) + '\n')
        return self.root, tree_string

    def find_lookahead(self, token):
        if token[0] == 'COMMENT' or token[1] == 'Invalid input':
            self.token = self.scanner.get_next_token()
            return self.find_lookahead(self.token)
        if token[0] == 'KEYWORD' or token[0] == 'SYMBOL':
            return token[1]
        return token[0]

    def handle_error(self, non_terminal, parent):
        if self.has_eof_error:
            return
        if self.lookahead in self.follow[non_terminal]:
            self.add_missing_error(non_terminal)
        else:
            self.add_illegal_errors()
            func_name = non_terminal.lower().replace('-', '_')
            func = getattr(self, func_name)
            func(parent)

    def add_missing_error(self, missed_term):
        line_number = self.scanner.get_line_number()
        self.error_string += f"#{line_number} : syntax error, missing {missed_term}\n"

    def add_illegal_errors(self):
        if self.lookahead == "End":
            self.add_eof_error()
        else:
            line_number = self.scanner.get_line_number()
            self.error_string += f"#{line_number} : syntax error, illegal {self.lookahead}\n"
            self.token = self.scanner.get_next_token()
            self.lookahead = self.find_lookahead(self.token)

    def add_eof_error(self):
        self.has_eof_error = True
        self.errored_root = deepcopy(self.root)
        line_number = self.scanner.get_line_number()
        self.error_string += f"#{line_number} : syntax error, Unexpected EOF\n"

    def match(self, expected_token, parent):
        if self.has_eof_error:
            return
        if self.lookahead == expected_token:
            Node(str(self.token).replace("'", ""), parent=parent)
            self.token = self.scanner.get_next_token()
            self.lookahead = self.find_lookahead(self.token)
        else:
            self.add_missing_error(expected_token)

    # 1
    def program(self):
        if self.lookahead in self.first[NonTerminals.Declaration_list]\
                or Terminal.EPSILON in self.first[NonTerminals.Declaration_list]:
            self.root = Node(NonTerminals.Program)
            self.declaration_list(self.root)
            Node('$', parent=self.root)
        else:
            self.handle_error(NonTerminals.Program, None)

    # 2
    def declaration_list(self, parent):
        if self.lookahead in self.first[NonTerminals.Declaration]\
                or Terminal.EPSILON in self.first[NonTerminals.Declaration]:
            node = Node(NonTerminals.Declaration_list, parent=parent)
            self.declaration(node)
            self.declaration_list(node)
        elif self.lookahead in self.follow[NonTerminals.Declaration_list]:
            node = Node(NonTerminals.Declaration_list, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Declaration_list, parent)

    # 3
    def declaration(self, parent):
        if self.lookahead in self.first[NonTerminals.Declaration_initial]\
                or Terminal.EPSILON in self.first[NonTerminals.Declaration_initial]:
            node = Node(NonTerminals.Declaration, parent=parent)
            self.declaration_initial(node)
            self.declaration_prime(node)
        else:
            self.handle_error(NonTerminals.Declaration, parent)

    # 4
    def declaration_initial(self, parent):
        if self.lookahead in self.first[NonTerminals.Type_specifier]\
                or Terminal.EPSILON in self.first[NonTerminals.Type_specifier]:
            node = Node(NonTerminals.Declaration_initial, parent=parent)
            self.type_specifier(node)
            self.match(Terminal.ID, node)
        else:
            self.handle_error(NonTerminals.Declaration_initial, parent)

    # 5
    def declaration_prime(self, parent):
        if self.lookahead in self.first[NonTerminals.Fun_declaration_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Fun_declaration_prime]:
            node = Node(NonTerminals.Declaration_prime, parent=parent)
            self.fun_declaration_prime(node)
        elif self.lookahead in self.first[NonTerminals.Var_declaration_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Var_declaration_prime]:
            node = Node(NonTerminals.Declaration_prime, parent=parent)
            self.var_declaration_prime(node)
        else:
            self.handle_error(NonTerminals.Declaration_prime, parent)

    # 6
    def var_declaration_prime(self, parent):
        if self.lookahead == Terminal.semicolon:
            node = Node(NonTerminals.Var_declaration_prime, parent=parent)
            self.match(Terminal.semicolon, node)
        elif self.lookahead == Terminal.bracket_open:
            node = Node(NonTerminals.Var_declaration_prime, parent=parent)
            self.match(Terminal.bracket_open, node)
            self.match(Terminal.NUM, node)
            self.match(Terminal.bracket_close, node)
            self.match(Terminal.semicolon, node)
        else:
            self.handle_error(NonTerminals.Var_call_prime, parent)

    # 7
    def fun_declaration_prime(self, parent):
        if self.lookahead == Terminal.parenthesis_open:
            node = Node(NonTerminals.Fun_declaration_prime, parent=parent)
            self.match(Terminal.parenthesis_open, node)
            self.params(node)
            self.match(Terminal.parenthesis_close, node)
            self.compound_stmt(node)
        else:
            self.handle_error(NonTerminals.Fun_declaration_prime, parent)

    # 8
    def type_specifier(self, parent):
        if self.lookahead == Terminal.int_terminal:
            node = Node(NonTerminals.Type_specifier, parent=parent)
            self.match(Terminal.int_terminal, node)
        elif self.lookahead == Terminal.void_terminal:
            node = Node(NonTerminals.Type_specifier, parent=parent)
            self.match(Terminal.void_terminal, node)
        else:
            self.handle_error(NonTerminals.Type_specifier, parent)

    # 9
    def params(self, parent):
        if self.lookahead == Terminal.int_terminal:
            node = Node(NonTerminals.Params, parent=parent)
            self.match(Terminal.int_terminal, node)
            self.match(Terminal.ID, node)
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead == Terminal.void_terminal:
            node = Node(NonTerminals.Params, parent=parent)
            self.match(Terminal.void_terminal, node)
        else:
            self.handle_error(NonTerminals.Params, parent)

    # 10
    def param_list(self, parent):
        if self.lookahead == Terminal.comma:
            node = Node(NonTerminals.Param_list, parent=parent)
            self.match(Terminal.comma, node)
            self.param(node)
            self.param_list(node)
        elif self.lookahead in self.follow[NonTerminals.Param_list]:
            node = Node(NonTerminals.Param_list, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Param_list, parent)

    # 11
    def param(self, parent):
        if self.lookahead in self.first[NonTerminals.Declaration_initial]\
                or Terminal.comma in self.first[NonTerminals.Declaration_initial]:
            node = Node(NonTerminals.Param, parent=parent)
            self.declaration_initial(node)
            self.param_prime(node)
        else:
            self.handle_error(NonTerminals.Param, parent)

    # 12
    def param_prime(self, parent):
        if self.lookahead == Terminal.bracket_open:
            node = Node(NonTerminals.Param_prime, parent=parent)
            self.match(Terminal.bracket_open, node)
            self.match(Terminal.bracket_close, node)
        elif self.lookahead in self.follow[NonTerminals.Param_prime]:
            node = Node(NonTerminals.Param_prime, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Param_prime, parent)

    # 13
    def compound_stmt(self, parent):
        if self.lookahead == Terminal.brace_open:
            node = Node(NonTerminals.Compound_stmt, parent=parent)
            self.match(Terminal.brace_open, node)
            self.declaration_list(node)
            self.statement_list(node)
            self.match(Terminal.brace_close, node)
        else:
            self.handle_error(NonTerminals.Compound_stmt, parent)

    # 14
    def statement_list(self, parent):
        if self.lookahead in self.first[NonTerminals.Statement]\
                or Terminal.EPSILON in self.first[NonTerminals.Statement]:
            node = Node(NonTerminals.Statement_list, parent=parent)
            self.statement(node)
            self.statement_list(node)
        elif self.lookahead in self.follow[NonTerminals.Statement_list]:
            node = Node(NonTerminals.Statement_list, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Statement_list, parent)

    # 15
    def statement(self, parent):
        if self.lookahead in self.first[NonTerminals.Expression_stmt]\
                or Terminal.EPSILON in self.first[NonTerminals.Expression_stmt]:
            node = Node(NonTerminals.Statement, parent=parent)
            self.expression_stmt(node)
        elif self.lookahead in self.first[NonTerminals.Compound_stmt]\
                or Terminal.EPSILON in self.first[NonTerminals.Compound_stmt]:
            node = Node(NonTerminals.Statement, parent=parent)
            self.compound_stmt(node)
        elif self.lookahead in self.first[NonTerminals.Selection_stmt]\
                or Terminal.EPSILON in self.first[NonTerminals.Selection_stmt]:
            node = Node(NonTerminals.Statement, parent=parent)
            self.selection_stmt(node)
        elif self.lookahead in self.first[NonTerminals.Iteration_stmt]\
                or Terminal.EPSILON in self.first[NonTerminals.Iteration_stmt]:
            node = Node(NonTerminals.Statement, parent=parent)
            self.iteration_stmt(node)
        elif self.lookahead in self.first[NonTerminals.Return_stmt]\
                or Terminal.EPSILON in self.first[NonTerminals.Return_stmt]:
            node = Node(NonTerminals.Statement, parent=parent)
            self.return_stmt(node)
        else:
            self.handle_error(NonTerminals.Statement, parent)

    # 16
    def expression_stmt(self, parent):
        if self.lookahead in self.first[NonTerminals.Expression]\
                or Terminal.EPSILON in self.first[NonTerminals.Expression]:
            node = Node(NonTerminals.Expression_stmt, parent=parent)
            self.expression(node)
            self.match(Terminal.semicolon, node)
        elif self.lookahead == Terminal.break_terminal:
            node = Node(NonTerminals.Expression_stmt, parent=parent)
            self.match(Terminal.break_terminal, node)
            self.match(Terminal.semicolon, node)
        elif self.lookahead == Terminal.semicolon:
            node = Node(NonTerminals.Expression_stmt, parent=parent)
            self.match(Terminal.semicolon, node)
        else:
            self.handle_error(NonTerminals.Expression_stmt, parent)

    # 17
    def selection_stmt(self, parent):
        if self.lookahead == Terminal.if_terminal:
            node = Node(NonTerminals.Selection_stmt, parent=parent)
            self.match(Terminal.if_terminal, node)
            self.match(Terminal.parenthesis_open, node)
            self.expression(node)
            self.match(Terminal.parenthesis_close, node)
            self.statement(node)
            self.else_stmt(node)
        else:
            self.handle_error(NonTerminals.Selection_stmt, parent)

    # 18
    def else_stmt(self, parent):
        if self.lookahead == Terminal.endif:
            node = Node(NonTerminals.Else_stmt, parent=parent)
            self.match(Terminal.endif, node)
        elif self.lookahead == Terminal.else_terminal:
            node = Node(NonTerminals.Else_stmt, parent=parent)
            self.match(Terminal.else_terminal, node)
            self.statement(node)
            self.match(Terminal.endif, node)
        else:
            self.handle_error(NonTerminals.Else_stmt, parent)

    # 19
    def iteration_stmt(self, parent):
        if self.lookahead == Terminal.for_terminal:
            node = Node(NonTerminals.Iteration_stmt, parent=parent)
            self.match(Terminal.for_terminal, node)
            self.match(Terminal.parenthesis_open, node)
            self.expression(node)
            self.match(Terminal.semicolon, node)
            self.expression(node)
            self.match(Terminal.semicolon, node)
            self.expression(node)
            self.match(Terminal.parenthesis_close, node)
            self.statement(node)
        else:
            self.handle_error(NonTerminals.Iteration_stmt, parent)

    # 20
    def return_stmt(self, parent):
        if self.lookahead == Terminal.return_terminal:
            node = Node(NonTerminals.Return_stmt, parent=parent)
            self.match(Terminal.return_terminal, node)
            self.return_stmt_prime(node)
        else:
            self.handle_error(NonTerminals.Return_stmt, parent)

    # 21
    def return_stmt_prime(self, parent):
        if self.lookahead == Terminal.semicolon:
            node = Node(NonTerminals.Return_stmt_prime, parent=parent)
            self.match(Terminal.semicolon, node)
        elif self.lookahead in self.first[NonTerminals.Expression]\
                or Terminal.EPSILON in self.first[NonTerminals.Expression]:
            node = Node(NonTerminals.Return_stmt_prime, parent=parent)
            self.expression(node)
            self.match(Terminal.semicolon, node)
        else:
            self.handle_error(NonTerminals.Return_stmt_prime, parent)

    # 22
    def expression(self, parent):
        if self.lookahead in self.first[NonTerminals.Simple_expression_zegond]\
                or Terminal.EPSILON in self.first[NonTerminals.Simple_expression_zegond]:
            node = Node(NonTerminals.Expression, parent=parent)
            self.simple_expression_zegond(node)
        elif self.lookahead == Terminal.ID:
            node = Node(NonTerminals.Expression, parent=parent)
            self.match(Terminal.ID, node)
            self.b(node)
        elif self.lookahead in self.follow[NonTerminals.Expression]:
            node = Node(NonTerminals.Expression, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Expression, parent)

    # 23
    def b(self, parent):
        if self.lookahead == Terminal.equal:
            node = Node(NonTerminals.B, parent=parent)
            self.match(Terminal.equal, node)
            self.expression(node)
        elif self.lookahead == Terminal.bracket_open:
            node = Node(NonTerminals.B, parent=parent)
            self.match(Terminal.bracket_open, node)
            self.expression(node)
            self.match(Terminal.bracket_close, node)
            self.h(node)
        elif self.lookahead in self.first[NonTerminals.Simple_expression_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Simple_expression_prime]:
            node = Node(NonTerminals.B, parent=parent)
            self.simple_expression_prime(node)
        else:
            self.handle_error(NonTerminals.B, parent)

    # 24
    def h(self, parent):
        if self.lookahead == Terminal.equal:
            node = Node(NonTerminals.H, parent=parent)
            self.match(Terminal.equal, node)
            self.expression(node)
        elif self.lookahead in self.first[NonTerminals.G]\
                or Terminal.EPSILON in self.first[NonTerminals.G]:
            node = Node(NonTerminals.H, parent=parent)
            self.g(node)
            self.d(node)
            self.c(node)
        else:
            self.handle_error(NonTerminals.H, parent)

    # 25
    def simple_expression_zegond(self, parent):
        if self.lookahead in self.first[NonTerminals.Additive_expression_zegond]\
                or Terminal.EPSILON in self.first[NonTerminals.Additive_expression_zegond]:
            node = Node(NonTerminals.Simple_expression_zegond, parent=parent)
            self.additive_expression_zegond(node)
            self.c(node)
        else:
            self.handle_error(NonTerminals.Simple_expression_zegond, parent)

    # 26
    def simple_expression_prime(self, parent):
        if self.lookahead in self.first[NonTerminals.Additive_expression_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Additive_expression_prime]:
            node = Node(NonTerminals.Simple_expression_prime, parent=parent)
            self.additive_expression_prime(node)
            self.c(node)
        else:
            self.handle_error(NonTerminals.Simple_expression_prime, parent)

    # 27
    def c(self, parent):
        if self.lookahead in self.first[NonTerminals.Relop]\
                or Terminal.EPSILON in self.first[NonTerminals.Relop]:
            node = Node(NonTerminals.C, parent=parent)
            self.relop(node)
            self.additive_expression(node)
        elif self.lookahead in self.follow[NonTerminals.C]:
            node = Node(NonTerminals.C, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.C, parent)

    # 28
    def relop(self, parent):
        if self.lookahead == Terminal.less:
            node = Node(NonTerminals.Relop, parent=parent)
            self.match(Terminal.less, node)
        elif self.lookahead == Terminal.equal_equal:
            node = Node(NonTerminals.Relop, parent=parent)
            self.match(Terminal.equal_equal, node)
        else:
            self.handle_error(NonTerminals.Relop, parent)

    # 29
    def additive_expression(self, parent):
        if self.lookahead in self.first[NonTerminals.Term]\
                or Terminal.EPSILON in self.first[NonTerminals.Term]:
            node = Node(NonTerminals.Additive_expression, parent=parent)
            self.term(node)
            self.d(node)
        else:
            self.handle_error(NonTerminals.Additive_expression, parent)

    # 30
    def additive_expression_prime(self, parent):
        if self.lookahead in self.first[NonTerminals.Term_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Term_prime]:
            node = Node(NonTerminals.Additive_expression_prime, parent=parent)
            self.term_prime(node)
            self.d(node)
        else:
            self.handle_error(NonTerminals.Additive_expression_prime, parent)

    # 31
    def additive_expression_zegond(self, parent):
        if self.lookahead in self.first[NonTerminals.Term_zegond]\
                or Terminal.EPSILON in self.first[NonTerminals.Term_zegond]:
            node = Node(NonTerminals.Additive_expression_zegond, parent=parent)
            self.term_zegond(node)
            self.d(node)
        else:
            self.handle_error(NonTerminals.Additive_expression_zegond, parent)

    # 32
    def d(self, parent):
        if self.lookahead in self.first[NonTerminals.Addop]\
                or Terminal.EPSILON in self.first[NonTerminals.Addop]:
            node = Node(NonTerminals.D, parent=parent)
            self.addop(node)
            self.term(node)
            self.d(node)
        elif self.lookahead in self.follow[NonTerminals.D]:
            node = Node(NonTerminals.D, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.D, parent)

    # 33
    def addop(self, parent):
        if self.lookahead == Terminal.plus:
            node = Node(NonTerminals.Addop, parent=parent)
            self.match(Terminal.plus, node)
        elif self.lookahead == Terminal.minus:
            node = Node(NonTerminals.Addop, parent=parent)
            self.match(Terminal.minus, node)
        else:
            self.handle_error(NonTerminals.Addop, parent)

    # 34
    def term(self, parent):
        if self.lookahead in self.first[NonTerminals.Signed_factor]\
                or Terminal.EPSILON in self.first[NonTerminals.Signed_factor]:
            node = Node(NonTerminals.Term, parent=parent)
            self.signed_factor(node)
            self.g(node)
        else:
            self.handle_error(NonTerminals.Term, parent)

    # 35
    def term_prime(self, parent):
        if self.lookahead in self.first[NonTerminals.Signed_factor_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Signed_factor_prime]:
            node = Node(NonTerminals.Term_prime, parent=parent)
            self.signed_factor_prime(node)
            self.g(node)
        else:
            self.handle_error(NonTerminals.Term_prime, parent)

    # 36
    def term_zegond(self, parent):
        if self.lookahead in self.first[NonTerminals.Signed_factor_zegond]\
                or Terminal.EPSILON in self.first[NonTerminals.Signed_factor_zegond]:
            node = Node(NonTerminals.Term_zegond, parent=parent)
            self.signed_factor_zegond(node)
            self.g(node)
        else:
            self.handle_error(NonTerminals.Term_zegond, parent)

    # 37
    def g(self, parent):
        if self.lookahead == Terminal.product:
            node = Node(NonTerminals.G, parent=parent)
            self.match(Terminal.product, node)
            self.signed_factor(node)
            self.g(node)
        elif self.lookahead in self.follow[NonTerminals.G]:
            node = Node(NonTerminals.G, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.G, parent)

    # 38
    def signed_factor(self, parent):
        if self.lookahead == Terminal.plus:
            node = Node(NonTerminals.Signed_factor, parent=parent)
            self.match(Terminal.plus, node)
            self.factor(node)
        elif self.lookahead == Terminal.minus:
            node = Node(NonTerminals.Signed_factor, parent=parent)
            self.match(Terminal.minus, node)
            self.factor(node)
        elif self.lookahead in self.first[NonTerminals.Factor]\
                or Terminal.EPSILON in self.first[NonTerminals.Factor]:
            node = Node(NonTerminals.Signed_factor, parent=parent)
            self.factor(node)
        else:
            self.handle_error(NonTerminals.Signed_factor, parent)

    # 39
    def signed_factor_prime(self, parent):
        if self.lookahead in self.first[NonTerminals.Factor_prime]\
                or Terminal.EPSILON in self.first[NonTerminals.Factor_prime]:
            node = Node(NonTerminals.Signed_factor_prime, parent=parent)
            self.factor_prime(node)
        else:
            self.handle_error(NonTerminals.Signed_factor_prime, parent)

    # 40
    def signed_factor_zegond(self, parent):
        if self.lookahead == Terminal.plus:
            node = Node(NonTerminals.Signed_factor_zegond, parent=parent)
            self.match(Terminal.plus, node)
            self.factor(node)
        elif self.lookahead == Terminal.minus:
            node = Node(NonTerminals.Signed_factor_zegond, parent=parent)
            self.match(Terminal.minus, node)
            self.factor(node)
        elif self.lookahead in self.first[NonTerminals.Factor_zegond]\
                or Terminal.EPSILON in self.first[NonTerminals.Factor_zegond]:
            node = Node(NonTerminals.Signed_factor_zegond, parent=parent)
            self.factor_zegond(node)
        else:
            self.handle_error(NonTerminals.Signed_factor_zegond, parent)

    # 41
    def factor(self, parent):
        if self.lookahead == Terminal.parenthesis_open:
            node = Node(NonTerminals.Factor, parent=parent)
            self.match(Terminal.parenthesis_open, node)
            self.expression(node)
            self.match(Terminal.parenthesis_close, node)
        elif self.lookahead == Terminal.ID:
            node = Node(NonTerminals.Factor, parent=parent)
            self.match(Terminal.ID, node)
            self.var_call_prime(node)
        elif self.lookahead == Terminal.NUM:
            node = Node(NonTerminals.Factor, parent=parent)
            self.match(Terminal.NUM, node)
        else:
            self.handle_error(NonTerminals.Factor, parent)

    # 42
    def var_call_prime(self, parent):
        if self.lookahead == Terminal.parenthesis_open:
            node = Node(NonTerminals.Var_call_prime, parent=parent)
            self.match(Terminal.parenthesis_open, node)
            self.args(node)
            self.match(Terminal.parenthesis_close, node)
        elif self.lookahead in self.first[NonTerminals.Var_prime]\
                or (Terminal.EPSILON in self.first[NonTerminals.Var_prime]
                    and self.lookahead in self.follow[NonTerminals.Var_prime]):
            node = Node(NonTerminals.Var_call_prime, parent=parent)
            self.var_prime(node)
        else:
            self.handle_error(NonTerminals.Var_call_prime, parent)

    # 43
    def var_prime(self, parent):
        if self.lookahead == Terminal.bracket_open:
            node = Node(NonTerminals.Var_prime, parent=parent)
            self.match(Terminal.bracket_open, node)
            self.expression(node)
            self.match(Terminal.bracket_close, node)
        elif self.lookahead in self.follow[NonTerminals.Var_prime]:
            node = Node(NonTerminals.Var_prime, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Var_prime, parent)

    # 44
    def factor_prime(self, parent):
        if self.lookahead == Terminal.parenthesis_open:
            node = Node(NonTerminals.Factor_prime, parent=parent)
            self.match(Terminal.parenthesis_open, node)
            self.args(node)
            self.match(Terminal.parenthesis_close, node)
        elif self.lookahead in self.follow[NonTerminals.Factor_prime]:
            node = Node(NonTerminals.Factor_prime, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Factor_prime, parent)

    # 45
    def factor_zegond(self, parent):
        if self.lookahead == Terminal.parenthesis_open:
            node = Node(NonTerminals.Factor_zegond, parent=parent)
            self.match(Terminal.parenthesis_open, node)
            self.expression(node)
            self.match(Terminal.parenthesis_close, node)
        elif self.lookahead == Terminal.NUM:
            node = Node(NonTerminals.Factor_zegond, parent=parent)
            self.match(Terminal.NUM, node)
        else:
            self.handle_error(NonTerminals.Factor_zegond, parent)

    # 46
    def args(self, parent):
        if self.lookahead in self.first[NonTerminals.Arg_list]\
                or Terminal.EPSILON in self.first[NonTerminals.Arg_list]:
            node = Node(NonTerminals.Args, parent=parent)
            self.arg_list(node)
        elif self.lookahead in self.follow[NonTerminals.Args]:
            node = Node(NonTerminals.Args, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Args, parent)

    # 47
    def arg_list(self, parent):
        if self.lookahead in self.first[NonTerminals.Expression]\
                or Terminal.EPSILON in self.first[NonTerminals.Expression]:
            node = Node(NonTerminals.Arg_list, parent=parent)
            self.expression(node)
            self.arg_list_prime(node)
        else:
            self.handle_error(NonTerminals.Arg_list, parent)

    # 48
    def arg_list_prime(self, parent):
        if self.lookahead == Terminal.comma:
            node = Node(NonTerminals.Arg_list_prime, parent=parent)
            self.match(Terminal.comma, node)
            self.expression(node)
            self.arg_list_prime(node)
        elif self.lookahead in self.follow[NonTerminals.Arg_list_prime]:
            node = Node(NonTerminals.Arg_list_prime, parent=parent)
            Node(Terminal.EPSILON.lower(), parent=node)
        else:
            self.handle_error(NonTerminals.Arg_list_prime, parent)
