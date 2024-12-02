from enum import Enum, auto
import re
from typing import List


# Состояния лексера
class State(Enum):
    S = auto()
    ID = auto()
    NUM = auto()
    COM = auto()
    OP = auto()
    SEP = auto()


# Лексические типы
class LexType(Enum):
    LEX_NULL = 0
    LEX_INT = 1
    LEX_FLOAT = 2
    LEX_BOOL = 3
    LEX_REAL = 4
    LEX_BOOLEAN = 5
    LEX_DIM = 6
    LEX_AS = 7
    LEX_THEN = 8
    LEX_FOR = 9
    LEX_TO = 10
    LEX_DO = 11
    LEX_WHILE = 12
    LEX_PROGRAM = 13
    LEX_VAR = 14
    LEX_SEMICOLON = 15
    LEX_COMMA = 16
    LEX_ASSIGN = 17
    LEX_EQ = 18
    LEX_NEQ = 19
    LEX_LSS = 20
    LEX_GTR = 21
    LEX_REQ = 22
    LEX_LEQ = 23
    LEX_PLUS = 24
    LEX_MINUS = 25
    LEX_OR = 26
    LEX_MULT = 27
    LEX_DIV = 28
    LEX_AND = 29
    LEX_NOT = 30
    LEX_START_COM = 31
    LEX_FINISH_COM = 32
    LEX_LPAREN = 33
    LEX_RPAREN = 34
    LEX_LBRACKET = 35
    LEX_RBRACKET = 36
    LEX_NUM = 37
    LEX_ID = 38
    LEX_INTEGER = 39
    LEX_TRUE = 40
    LEX_FALSE = 41
    LEX_IF = 42
    LEX_ELSE = 43
    LEX_READ = 44
    LEX_WRITE = 45
    LEX_COLON = 46


KEYWORDS = {
    "integer": LexType.LEX_INTEGER,
    "real": LexType.LEX_REAL,
    "boolean": LexType.LEX_BOOLEAN,
    "dim": LexType.LEX_DIM,
    "as": LexType.LEX_AS,
    "if": LexType.LEX_IF,
    "then": LexType.LEX_THEN,
    "else": LexType.LEX_ELSE,
    "for": LexType.LEX_FOR,
    "to": LexType.LEX_TO,
    "do": LexType.LEX_DO,
    "while": LexType.LEX_WHILE,
    "read": LexType.LEX_READ,
    "write": LexType.LEX_WRITE,
    "true": LexType.LEX_TRUE,
    "false": LexType.LEX_FALSE,
    "program": LexType.LEX_PROGRAM,
    "end": LexType.LEX_NULL
}

OPERATORS = {
    "=": LexType.LEX_ASSIGN,
    "EQ": LexType.LEX_EQ,
    "NE": LexType.LEX_NEQ,
    "LT": LexType.LEX_LSS,
    "LE": LexType.LEX_LEQ,
    "GT": LexType.LEX_GTR,
    "GE": LexType.LEX_REQ,
    "plus": LexType.LEX_PLUS,
    "min": LexType.LEX_MINUS,
    "or": LexType.LEX_OR,
    "mult": LexType.LEX_MULT,
    "div": LexType.LEX_DIV,
    "and": LexType.LEX_AND,
    "~": LexType.LEX_NOT,
}

SEPARATORS = {
    "[": LexType.LEX_LBRACKET,
    "]": LexType.LEX_RBRACKET,
    "(": LexType.LEX_LPAREN,
    ")": LexType.LEX_RPAREN,
    ":": LexType.LEX_COLON,
    ";": LexType.LEX_SEMICOLON,
    ",": LexType.LEX_COMMA
}


class Token:
    def __init__(self, type_: str, value: str, x_coord: int, y_coord: int):
        self.type = type_
        self.value = value
        self.x_coord = x_coord
        self.y_coord = y_coord

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, x={self.x_coord}, y={self.y_coord})"


class Lexer:
    def __init__(self, keywords: List[str], separators: List[str], operators: List[str]):
        self.tokens = []
        self.input_lines = []
        self.keywords = keywords
        self.separators = separators
        self.operators = operators
        self.x_coord = 0
        self.y_coord = 0
        self.lex_buff = ""
        self.state = State.S  # Инициализируем состояние как элемент перечисления State

    def read_file(self, filename: str):
        with open(filename, "r") as f:
            self.input_lines = f.readlines()
        print(f"Содержимое файла '{filename}':")
        for line in self.input_lines:
            print(line.rstrip())

    def tokenize(self, lines: List[str]) -> List[Token]:
        self.tokens = []
        self.y_coord = 0
        for line in lines:
            self.process_line(line)
        return self.tokens

    def process_line(self, line: str) -> None:
        self.y_coord += 1
        print(f"Обработка строки {self.y_coord}: {line.strip()}")
        self.x_coord = 0  # Сбрасываем координату x в начале каждой строки
        i = 0
        while i < len(line):
            c = line[i]
            self.x_coord = i + 1
            self.process_char(c)
            i += 1
        self.finalize_token()
        print(f"Текущие токены после строки {self.y_coord}: {self.tokens}")

    def process_char(self, c: str) -> None:
        print(f"Обработка символа: {c}, Текущее состояние: {self.state}")

        if self.state == State.S:
            if c.isspace():
                return
            elif c.isalpha():
                self.start_token(c, State.ID)
            elif c.isdigit():
                self.start_token(c, State.NUM)
            elif c == ".":
                # Начало дробного числа
                self.start_token(c, State.NUM)
            elif c == "{":
                self.start_token(c, State.COM)
            elif c in self.operators:
                if c == "~":  # Если это унарная операция
                    self.start_token(c, State.OP)
                    self.finalize_token()
                else:
                    self.start_token(c, State.ID)
            elif c in self.separators:
                self.start_token(c, State.SEP)
                self.finalize_token()
            else:
                self.error(f"Invalid character: {c}")
        elif self.state == State.ID:
            if c.isalnum() or c == '_':
                self.lex_buff += c
            else:
                self.finalize_token()
                self.process_char(c)
        elif self.state == State.NUM:
            if self.is_number_part(c):
                self.lex_buff += c
            else:
                self.finalize_token()
                self.process_char(c)
        elif self.state == State.COM:
            if c == '}':
                self.lex_buff += c
                self.finalize_token()
            else:
                self.lex_buff += c
        elif self.state == State.OP:
            if self.lex_buff + c in self.operators:
                self.lex_buff += c
                self.finalize_token()
            else:
                self.finalize_token()
                self.process_char(c)
        elif self.state == State.SEP:
            # Разделители уже обработаны в State.S
            self.error("Invalid state in separator processing")
        else:
            self.error(f"Unknown state: {self.state}")

    def is_number_part(self, c: str) -> bool:
        """Проверяет, может ли символ быть частью числа (целого или действительного)."""
        return c.isdigit() or c in {'B', 'b', 'O', 'o', 'D', 'd', 'H', 'h', '.', 'E', 'e', '+', '-'}

    def start_token(self, c: str, new_state: State) -> None:
        self.lex_buff = c
        self.state = new_state

    def finalize_token(self) -> None:
        if not self.lex_buff:
            return
        print(f"Финализация токена: {self.lex_buff} (State: {self.state})")
        token_type = None
        if self.state == State.ID:
            if self.lex_buff in self.keywords:
                token_type = "KEYWORD"
            elif self.lex_buff in self.operators:
                token_type = "OPERATOR"
            else:
                token_type = "IDENTIFIER"
        elif self.state == State.NUM and self.is_valid_number(self.lex_buff):
            token_type = "NUMBER"
        elif self.state == State.COM:
            token_type = "COMMENT"
        elif self.state == State.OP:
            if self.lex_buff in self.operators:
                token_type = "OPERATOR"
            else:
                self.error(f"Invalid operator: {self.lex_buff}")
        elif self.state == State.SEP:
            if self.lex_buff in self.separators:
                token_type = "SEPARATOR"
            else:
                self.error(f"Invalid separator: {self.lex_buff}")
        else:
            self.error(f"Invalid token: {self.lex_buff}")

        self.tokens.append(Token(token_type, self.lex_buff, self.x_coord - len(self.lex_buff) + 1, self.y_coord))
        self.lex_buff = ""
        self.state = State.S
        print(f"Токен добавлен: {self.tokens[-1]}")

    def is_valid_number(self, lexeme: str) -> bool:
        """Проверяет корректность числа согласно новым правилам."""
        # Регулярные выражения для разных типов чисел
        binary_pattern = r"^[01]+[Bb]$"
        octal_pattern = r"^[0-7]+[Oo]$"
        decimal_pattern = r"^\d+([Dd]?)$"
        hex_pattern = r"^[0-9A-Fa-f]+[Hh]$"
        real_pattern = r"^\d*(\.\d+)?([Ee][+-]?\d+)?$"

        patterns = [binary_pattern, octal_pattern, decimal_pattern, hex_pattern, real_pattern]
        return any(re.fullmatch(pattern, lexeme) for pattern in patterns)

    def error(self, message: str) -> None:
        raise ValueError(f"{message} at ({self.y_coord}, {self.x_coord})")

    def print_tokens(self):
        for token in self.tokens:
            print(token)


class VarToken:
    def __init__(self, var_type="", var_name=""):
        self.var_type = var_type
        self.var_name = var_name


class Parser:
    def __init__(self, tokens):
        self.idx = 0
        self.tokens = tokens
        self.token_count = len(tokens)
        self.tokens_var = []
        self.single_token_var = VarToken()
        self.if_while_check = 0
        self.if_while_flag = False


        if not self.tokens:
            raise SyntaxError("Token list is empty.")
        if self.current_token().type != "KEYWORD" or self.current_token().value != "program":
            self.error("The program must start with the keyword 'program'", self.current_token())
        self.idx += 1
        # Ожидаем идентификатор после 'program'
        if self.current_token().type != "IDENTIFIER":
            self.error("Expected program name after 'program'", self.current_token())
        self.program_name = self.current_token().value
        self.idx += 1

    def current_token(self):
        """Возвращает текущий токен или вызывает ошибку, если индекс выходит за пределы."""
        if self.idx >= self.token_count:
            self.error("Unexpected end of tokens", Token("", "", 0, 0))
        return self.tokens[self.idx]

    def error(self, message, token):
        raise SyntaxError(f"ERROR ({message}) -> {token.value} ({token.x_coord}, {token.y_coord})")

    def start_prog(self):
        print(f"Текущий токен: {self.current_token()}")  # Добавьте вывод текущего токена
        self.start_vars()
        self.start_begin()
        if self.current_token().type == "KEYWORD" and self.current_token().value == "end":
            print("Программа корректна.")
        else:
            self.error("Program must end with 'end'", self.current_token())

    def start_vars(self):
        while self.current_token().type == "KEYWORD" and self.current_token().value == "dim":
            self.idx += 1
            self.start_id()
            if self.current_token().type == "KEYWORD" and self.current_token().value == "as":
                self.idx += 1
                if self.current_token().type == "KEYWORD":
                    token_value = self.current_token().value
                    if token_value == "integer":
                        self.single_token_var.var_type = "INT"
                    elif token_value == "real":
                        self.single_token_var.var_type = "REAL"
                    elif token_value == "boolean":
                        self.single_token_var.var_type = "BOOL"
                    else:
                        self.error("Unknown variable type", self.current_token())
                    self.tokens_var.append(self.single_token_var)
                    self.idx += 1
                else:
                    self.error("Expected variable type", self.current_token())
            else:
                self.error("Expected 'as' after variable name", self.current_token())

    def start_id(self, flag_token=True):
        if self.current_token().type == "IDENTIFIER":
            if flag_token:
                self.single_token_var = VarToken(self.single_token_var.var_type, self.current_token().value)
            else:
                self.id_check()
            self.idx += 1
        else:
            self.error("Expected an identifier", self.current_token())


    def start_begin(self):
        while self.idx < self.token_count and (self.current_token().type != "KEYWORD" or self.current_token().value not in {"end", "else"}):
            current_type = self.current_token().type
            if current_type == "IDENTIFIER":
                self.id_check()
                self.idx += 1
                if self.current_token().type == "OPERATOR" and self.current_token().value == "=":
                    self.idx += 1
                    self.start_v()
                else:
                    self.error("Expected assignment '='", self.current_token())
            elif current_type == "KEYWORD":
                keyword = self.current_token().value
                if keyword == "if":
                    self.handle_if_statement()
                elif keyword == "while":
                    self.handle_while_loop()
                elif keyword == "read":
                    self.handle_read()
                elif keyword == "write":
                    self.handle_write()
                else:
                    self.error("Unexpected keyword", self.current_token())
            else:
                self.error("Incorrect input", self.current_token())

    def handle_if_statement(self):
        self.idx += 1
        self.start_v()
        if self.current_token().type == "KEYWORD" and self.current_token().value == "then":
            self.idx += 1
            self.start_begin()
            if self.current_token().type == "KEYWORD" and self.current_token().value == "else":
                self.idx += 1
                self.start_begin()
            # Здесь не увеличиваем idx, так как 'end' будет обработан в start_begin
        else:
            self.error("Missing 'then' in if statement", self.current_token())

    def handle_while_loop(self):
        self.idx += 1
        self.start_v()
        if self.current_token().type == "KEYWORD" and self.current_token().value == "do":
            self.idx += 1
            self.start_begin()
        else:
            self.error("Missing 'do' in while loop", self.current_token())

    def handle_read(self):
        self.idx += 1
        if self.current_token().type == "IDENTIFIER":
            self.start_id(False)
        else:
            self.error("Expected identifier after 'read'", self.current_token())

    def handle_write(self):
        self.idx += 1
        self.start_v()

    def start_v(self):
        self.start_o()
        while self.current_token().type == "OPERATOR" and self.current_token().value in {"EQ", "NE", "LT", "LE", "GT", "GE"}:
            self.if_while_flag = True
            self.idx += 1
            self.start_o()

    def start_o(self):
        self.start_s()
        while self.current_token().type == "OPERATOR" and self.current_token().value in {"plus", "min", "or"}:
            self.idx += 1
            self.start_s()

    def start_s(self):
        self.start_m()
        while self.current_token().type == "OPERATOR" and self.current_token().value in {"mult", "div", "and"}:
            self.idx += 1
            self.start_m()

    def start_m(self):
        current_token = self.current_token()
        if current_token.type == "IDENTIFIER":
            self.id_check()
            self.idx += 1
        elif current_token.value in {"true", "false"}:
            self.if_while_flag = True
            self.idx += 1
        elif current_token.type == "NUMBER":
            self.idx += 1
        elif current_token.type == "OPERATOR" and current_token.value == "~":
            self.idx += 1
            self.start_m()
        elif current_token.type == "SEPARATOR" and current_token.value == "(":
            self.idx += 1
            self.start_v()
            if self.current_token().type == "SEPARATOR" and self.current_token().value == ")":
                self.idx += 1
            else:
                self.error("Expected closing parenthesis", current_token)
        else:
            self.error("Unexpected token", current_token)


    def id_check(self):
        for var in self.tokens_var:
            if var.var_name == self.current_token().value:
                return
        self.error("Undeclared or incorrect variable", self.current_token())

    def parse_number(self):
        """
        Синтаксический анализ чисел.
        Распознает как целые числа (включая двоичные, восьмеричные, десятичные, шестнадцатеричные),
        так и действительные числа с порядком (e, E).
        """
        token = self.current_token()
        if token.token_type != "NUMBER":
            self.error(f"Ожидалось число, но найдено {token.token_type}: {token.value}")

        lexeme = token.value

        if re.fullmatch(r"^[01]+[Bb]$", lexeme):
            print(f"Двоичное число: {lexeme}")
            return {"type": "binary", "value": int(lexeme[:-1], 2)}
        elif re.fullmatch(r"^[0-7]+[Oo]$", lexeme):
            print(f"Восьмеричное число: {lexeme}")
            return {"type": "octal", "value": int(lexeme[:-1], 8)}
        elif re.fullmatch(r"^\d+([Dd]?)$", lexeme):
            print(f"Десятичное число: {lexeme}")
            return {"type": "decimal", "value": int(lexeme.rstrip('Dd'))}
        elif re.fullmatch(r"^[0-9A-Fa-f]+[Hh]$", lexeme):
            print(f"Шестнадцатеричное число: {lexeme}")
            return {"type": "hexadecimal", "value": int(lexeme[:-1], 16)}
        elif re.fullmatch(r"^\d*(\.\d+)?([Ee][+-]?\d+)?$", lexeme):
            print(f"Действительное число: {lexeme}")
            return {"type": "real", "value": float(lexeme)}
        else:
            self.error(f"Некорректный формат числа: {lexeme}")

        self.advance_token()

    def parse_expression(self):
        """
        Пример использования чисел в выражениях.
        """
        left = self.parse_number()

        while self.current_token().token_type == "OPERATOR":
            operator = self.current_token().value
            self.advance_token()
            right = self.parse_number()

            # Выполнение операций (если нужно)
            if operator == "+":
                left = {"type": "sum", "value": left["value"] + right["value"]}
            elif operator == "-":
                left = {"type": "difference", "value": left["value"] - right["value"]}
            elif operator == "*":
                left = {"type": "product", "value": left["value"] * right["value"]}
            elif operator == "/":
                left = {"type": "division", "value": left["value"] / right["value"]}
            else:
                self.error(f"Неизвестный оператор: {operator}")

        return left

def main():
    input_file = "input_file_4.txt"  # Имя входного файла
    try:
        # Создаем экземпляр лексера и анализируем входной файл
        lexer = Lexer(keywords=KEYWORDS.keys(), separators=SEPARATORS.keys(), operators=OPERATORS.keys())
        lexer.read_file(input_file)
        tokens = lexer.tokenize(lexer.input_lines)

        # Печать всех токенов
        print("\n=== Лексический анализ ===")
        lexer.print_tokens()

        if not tokens:
            print("Ошибка: список токенов пуст после лексера.")
        else:
            print("\nСписок токенов после лексического анализа:")
            for token in tokens:
                print(token)

        # Создаем экземпляр парсера и анализируем токены
        print("\n=== Синтаксический анализ ===")
        parser = Parser(tokens)
        parser.start_prog()

    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
    except ValueError as e:
        print(f"Лексическая ошибка: {e}")
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    main()
