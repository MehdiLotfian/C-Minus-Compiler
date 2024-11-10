from collections import defaultdict


class DFA:
    def __init__(self):
        self.dfa = {}

    def construct_dfa(self):
        for i in range(19):
            self.dfa['S' + str(i + 1)] = {}
        for i in range(1, 19):
            func_name = f"complete_s{i}"
            func = getattr(self, func_name, None)
            if func:
                func()
        return self.dfa

    def complete_s1(self):
        self.dfa['S1'] = {
            ' ': 'S1', '\n': 'S1', '\r': 'S1', '\t': 'S1', '\v': 'S1', '\f': 'S1',
            ';': 'S6', ':': 'S6', ',': 'S6', '[': 'S6', ']': 'S6', '(': 'S6', ')': 'S6', '{': 'S6', '}': 'S6',
            '+': 'S6', '-': 'S6', '<': 'S6',
            '=': 'S7',
            '/': 'S10',
            '*': 'S16',
            '$$': 'S21',
        }
        self.add_alphanumeric('S1', 'S2', True, False)
        self.add_alphanumeric('S1', 'S4', False)

    def complete_s2(self):
        self.add_alphanumeric('S2', 'S2', True, False)
        others_acceptable = [' ', '\n', '\r', '\t', '\v', '\f', ';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-',
                             '<',
                             '*', '/', '=', '$$']
        for character in others_acceptable:
            self.dfa['S2'][character] = 'S3'
        self.add_alphanumeric('S2', 'S19', False, True)

    def complete_s3(self):
        self.add_alphanumeric('S3', 'S1', True, False)

    def complete_s4(self):
        self.add_alphanumeric('S4', 'S4')
        others_acceptable = [' ', '\n', '\r', '\t', '\v', '\f', ';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-',
                             '<',
                             '*', '/', '=', '$$']
        for character in others_acceptable:
            self.dfa['S4'][character] = 'S5'

    def complete_s5(self):
        self.add_alphanumeric('S5', 'S1')

    def complete_s6(self):
        acceptable = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<']
        for character in acceptable:
            self.dfa['S6'][character] = 'S1'

    def complete_s7(self):
        self.dfa['S7']['='] = 'S8'
        self.add_alphanumeric('S7', 'S9')
        others_acceptable = [' ', '\n', '\r', '\t', '\v', '\f', '/', '$$', ';', ':', ',', '[', ']', '(', ')', '{', '}',
                             '+', '-', '<']
        for character in others_acceptable:
            self.dfa['S7'][character] = 'S9'

    def complete_s8(self):
        self.dfa['S8']['='] = 'S1'

    def complete_s9(self):
        self.dfa['S9']['='] = 'S1'

    def complete_s10(self):
        self.dfa['S10']['*'] = 'S11'
        self.add_alphanumeric('S10', 'S15')
        others_acceptable = [' ', '\n', '\r', '\t', '\v', '\f', '/', '$$', ';', ':', ',', '[', ']', '(', ')', '{', '}',
                             '+', '-', '<']
        for character in others_acceptable:
            self.dfa['S10'][character] = 'S15'

    def complete_s11(self):
        self.dfa['S11'] = defaultdict(lambda: 'S11')
        self.dfa['S11']['*'] = 'S12'
        self.dfa['S11']['$$'] = 'S20'

    def complete_s12(self):
        self.dfa['S12'] = defaultdict(lambda: 'S13')
        self.dfa['S12']['/'] = 'S14'
        self.dfa['S12']['$$'] = 'S20'

    def complete_s13(self):
        self.dfa['S13']['*'] = 'S11'

    def complete_s14(self):
        self.dfa['S14']['/'] = 'S1'

    def complete_s15(self):
        self.dfa['S15']['/'] = 'S1'

    def complete_s16(self):
        self.add_alphanumeric('S16', 'S18')
        others_acceptable = [' ', '\n', '\r', '\t', '\v', '\f', '/', '$$', ';', ':', ',', '[', ']', '(', ')', '{', '}',
                             '+', '-', '<']
        for character in others_acceptable:
            self.dfa['S16'][character] = 'S18'
        self.dfa['S16']['/'] = 'S17'

    def complete_s17(self):
        self.dfa['S17']['/'] = 'S1'

    def complete_s18(self):
        self.dfa['S18'] = defaultdict(lambda: 'S1')
        self.dfa['S18']['/'] = None

    def complete_s19(self):
        self.add_alphanumeric('S19', 'S1', False, True)

    def add_alphanumeric(self, current_state, next_state, numbers=True, alphabets=True):
        if numbers:
            for i in range(10):
                self.dfa[current_state][str(i)] = next_state
        if alphabets:
            for i in range(ord('A'), ord('Z') + 1):
                self.dfa[current_state][chr(i)] = next_state
            for i in range(ord('a'), ord('z') + 1):
                self.dfa[current_state][chr(i)] = next_state
