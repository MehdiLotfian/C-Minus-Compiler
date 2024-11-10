# Mehdi Lotfian 99105689 - Amir Mohammad Izadi 99105283
from scanner import Scanner


def remove_empty_lines(text):
    lines = text.split('\n')
    non_empty_lines = filter(lambda line: line.strip(), lines)
    return '\n'.join(non_empty_lines)


if __name__ == "__main__":
    with open('input.txt', 'r', encoding='utf-8') as file:
        code_string = file.read()

    scanner = Scanner(code_string)
    while scanner.code_pointer < len(code_string):
        token = scanner.get_next_token()
        if token[0] == 'End':
            break
        if token[0] != 'COMMENT':
            scanner.update_file_strings(token)

    with open('tokens.txt', 'w') as file:
        file.write(remove_empty_lines(scanner.get_tokens_string()))
    with open('symbol_table.txt', 'w') as file:
        file.write(remove_empty_lines(scanner.get_symbol_tabel_string()))
    with open('lexical_errors.txt', 'w') as file:
        file.write(remove_empty_lines(scanner.get_lexical_errors_string()))
