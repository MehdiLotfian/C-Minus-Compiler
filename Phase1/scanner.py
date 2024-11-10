from dfa import DFA
from collections import defaultdict


class Scanner:
    def __init__(self, code_string):
        self.code_string = code_string
        self.line_number = 1
        self.code_pointer = 0
        self.token_string = ""
        self.error_string = ""
        self.key_words = ['break', 'else', 'if', 'endif', 'int', 'for', 'return', 'void']
        self.symbol_list = self.key_words.copy()
        self.current_state = 'S1'
        self.all_errors = ['Invalid input', 'Unclosed comment', 'Unmatched comment', 'Invalid number']
        self.dfa = DFA().construct_dfa()
        self.final_states = {'S3': 'NUM', 'S5': 'ID_KEYWORD', 'S6': 'SYMBOL', 'S8': 'SYMBOL', 'S9': 'SYMBOL',
                             'S14': 'COMMENT', 'S15': 'SYMBOL', 'S17': 'Unmatched comment', 'S18': 'SYMBOL',
                             'S19': 'Invalid number', 'S20': 'Unclosed comment', 'S21': 'End'}
        self.back_states = {'S3': 2, 'S5': 2, 'S6': 1, 'S8': 1, 'S9': 2, 'S14': 1, 'S15': 2, 'S17': 1, 'S18': 2,
                            'S19': 1}
        self.lexeme = ''

    def get_next_token(self):
        while True:
            if self.current_state == 'S1':
                self.lexeme = ''
            if self.code_pointer >= len(self.code_string):
                self.current_state = self.dfa[self.current_state]['$$']
                break
            current_char = self.code_string[self.code_pointer]
            self.code_pointer += 1
            self.lexeme += current_char
            if (current_char not in self.dfa[self.current_state] and
                    not isinstance(self.dfa[self.current_state], defaultdict)):
                self.current_state = 'S1'
                return self.lexeme, 'Invalid input'
            else:
                self.current_state = self.dfa[self.current_state][current_char]
            if self.current_state == 'S1':
                if current_char == '\n':
                    self.line_number += 1
                    self.token_string += '\n'
                    self.error_string += '\n'
            if self.current_state in self.final_states:
                break

        if self.current_state in self.back_states:
            self.code_pointer -= self.back_states[self.current_state]
            if self.back_states[self.current_state] == 2:
                self.lexeme = self.lexeme[:-1]
        if self.current_state in ['S17', 'S19', 'S20']:
            if self.current_state == 'S20':
                self.lexeme = self.lexeme[:7] + '...'
            self.code_pointer += 1
            token = self.lexeme, self.final_states[self.current_state]
            self.current_state = 'S1'
            return token
        elif self.current_state == 'S5':
            if self.lexeme in self.key_words:
                return 'KEYWORD', self.lexeme
            else:
                if self.lexeme not in self.symbol_list:
                    self.symbol_list.append(self.lexeme)
                return 'ID', self.lexeme
        return self.final_states[self.current_state], self.lexeme

    def get_line_number(self):
        return self.line_number

    def update_file_strings(self, token):
        if token[1] in self.all_errors:
            if len(self.error_string) == 0 or self.error_string[-1] == '\n':
                self.error_string += str(self.line_number) + '.\t' + str(token).replace("'", '') + ' '
            else:
                self.error_string += str(token).replace("'", '') + ' '
        else:
            if len(self.token_string) == 0 or self.token_string[-1] == '\n':
                self.token_string += str(self.line_number) + '.\t' + str(token).replace("'", '') + ' '
            else:
                self.token_string += str(token).replace("'", '') + ' '

    def get_tokens_string(self):
        return self.token_string

    def get_symbol_tabel_string(self):
        symbol_tabel_string = ""
        for i in range(len(self.symbol_list)):
            symbol_tabel_string += str(i + 1) + '.\t' + self.symbol_list[i] + '\n'
        return symbol_tabel_string

    def get_lexical_errors_string(self):
        if len(self.error_string.replace("\n", "")) == 0:
            return "There is no lexical error."
        return self.error_string
