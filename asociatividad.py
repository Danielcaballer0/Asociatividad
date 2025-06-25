import re
from typing import List, Union, Any
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Tipos de tokens para el analizador léxico"""
    NUMBER = "NUMBER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    POWER = "POWER"
    ASSIGN = "ASSIGN"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    IDENTIFIER = "IDENTIFIER"
    EOF = "EOF"


@dataclass
class Token:
    """Representa un token del analizador léxico"""
    type: TokenType
    value: Any
    position: int = 0


class Lexer:
    """Analizador léxico básico"""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def error(self):
        raise Exception(f"Carácter inválido en posición {self.pos}")
    
    def advance(self):
        """Avanza al siguiente carácter"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        """Omite espacios en blanco"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def number(self):
        """Extrae un número"""
        result = ''
        while (self.current_char is not None and 
               (self.current_char.isdigit() or self.current_char == '.')):
            result += self.current_char
            self.advance()
        return float(result) if '.' in result else int(result)
    
    def identifier(self):
        """Extrae un identificador"""
        result = ''
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        return result
    
    def get_next_token(self):
        """Obtiene el siguiente token"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit():
                return Token(TokenType.NUMBER, self.number())
            
            if self.current_char.isalpha() or self.current_char == '_':
                return Token(TokenType.IDENTIFIER, self.identifier())
            
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+')
            
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')
            
            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(TokenType.POWER, '**')
                return Token(TokenType.MULTIPLY, '*')
            
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/')
            
            if self.current_char == '=':
                self.advance()
                return Token(TokenType.ASSIGN, '=')
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
            
            self.error()
        
        return Token(TokenType.EOF, None)


class ASTNode:
    """Clase base para nodos del AST"""
    pass


@dataclass
class BinaryOp(ASTNode):
    """Nodo para operaciones binarias"""
    left: ASTNode
    op: Token
    right: ASTNode
    
    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op.value}, {self.right})"


@dataclass
class UnaryOp(ASTNode):
    """Nodo para operaciones unarias"""
    op: Token
    expr: ASTNode
    
    def __repr__(self):
        return f"UnaryOp({self.op.value}, {self.expr})"


@dataclass
class Num(ASTNode):
    """Nodo para números"""
    value: Union[int, float]
    
    def __repr__(self):
        return f"Num({self.value})"


@dataclass
class Var(ASTNode):
    """Nodo para variables"""
    value: str
    
    def __repr__(self):
        return f"Var({self.value})"


@dataclass
class Assign(ASTNode):
    """Nodo para asignaciones"""
    left: Var
    right: ASTNode
    
    def __repr__(self):
        return f"Assign({self.left}, {self.right})"


class Parser:
    """Parser descendente recursivo que implementa asociatividad"""
    
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.variables = {}
    
    def error(self):
        raise Exception(f"Token inesperado: {self.current_token}")
    
    def eat(self, token_type: TokenType):
        """Consume un token del tipo esperado"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def factor(self):
        """
        factor : (PLUS | MINUS) factor 
               | NUMBER 
               | IDENTIFIER
               | LPAREN expr RPAREN
        """
        token = self.current_token
        
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(token, self.factor())
        
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())
        
        elif token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Num(token.value)
        
        elif token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Var(token.value)
        
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        
        else:
            self.error()
    
    def power(self):
        """
        power : factor (POW factor)*
        Asociatividad DERECHA para **
        """
        node = self.factor()
        
        if self.current_token.type == TokenType.POWER:
            token = self.current_token
            self.eat(TokenType.POWER)
            # Recursión a la derecha para asociatividad derecha
            node = BinaryOp(left=node, op=token, right=self.power())
        
        return node
    
    def term(self):
        """
        term : power ((MUL | DIV) power)*
        Asociatividad IZQUIERDA para * y /
        """
        node = self.power()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            
            # Iteración para asociatividad izquierda
            node = BinaryOp(left=node, op=token, right=self.power())
        
        return node
    
    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        Asociatividad IZQUIERDA para + y -
        """
        node = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            
            # Iteración para asociatividad izquierda
            node = BinaryOp(left=node, op=token, right=self.term())
        
        return node
    
    def assignment(self):
        """
        assignment : IDENTIFIER ASSIGN assignment | expr
        Asociatividad DERECHA para =
        """
        node = self.expr()
        
        if (isinstance(node, Var) and 
            self.current_token.type == TokenType.ASSIGN):
            self.eat(TokenType.ASSIGN)
            # Recursión a la derecha para asociatividad derecha
            node = Assign(left=node, right=self.assignment())
        
        return node
    
    def parse(self):
        """Punto de entrada del parser"""
        return self.assignment()


class Interpreter:
    """Intérprete que evalúa el AST"""
    
    def __init__(self):
        self.variables = {}
    
    def visit_BinaryOp(self, node: BinaryOp):
        """Visita nodos de operación binaria"""
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MULTIPLY:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIVIDE:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == TokenType.POWER:
            return self.visit(node.left) ** self.visit(node.right)
    
    def visit_UnaryOp(self, node: UnaryOp):
        """Visita nodos de operación unaria"""
        if node.op.type == TokenType.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == TokenType.MINUS:
            return -self.visit(node.expr)
    
    def visit_Num(self, node: Num):
        """Visita nodos numéricos"""
        return node.value
    
    def visit_Var(self, node: Var):
        """Visita nodos de variable"""
        var_name = node.value
        if var_name in self.variables:
            return self.variables[var_name]
        else:
            raise NameError(f"Variable '{var_name}' no definida")
    
    def visit_Assign(self, node: Assign):
        """Visita nodos de asignación"""
        var_name = node.left.value
        value = self.visit(node.right)
        self.variables[var_name] = value
        return value
    
    def visit(self, node: ASTNode):
        """Método dispatcher para visitar nodos"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, None)
        if visitor is None:
            raise Exception(f'Método {method_name} no encontrado')
        return visitor(node)
    
    def interpret(self, tree: ASTNode):
        """Interpreta el AST"""
        return self.visit(tree)


def demonstrate_associativity():
    """Función principal que demuestra los conceptos de asociatividad"""
    
    print("=" * 60)
    print("DEMOSTRACIÓN DE ASOCIATIVIDAD EN COMPILADORES")
    print("=" * 60)
    
    interpreter = Interpreter()
    
    # Ejemplos de asociatividad izquierda
    print("\n1. ASOCIATIVIDAD IZQUIERDA (-, +, *, /)")
    print("-" * 40)
    
    examples_left = [
        "5 - 3 - 2",      # (5 - 3) - 2 = 0
        "8 / 4 / 2",      # (8 / 4) / 2 = 1
        "2 * 3 * 4",      # (2 * 3) * 4 = 24
        "10 + 5 + 3"      # (10 + 5) + 3 = 18
    ]
    
    for expr in examples_left:
        lexer = Lexer(expr)
        parser = Parser(lexer)
        tree = parser.parse()
        result = interpreter.interpret(tree)
        print(f"{expr:12} = {result:8} (AST: {tree})")
    
    # Ejemplos de asociatividad derecha
    print("\n2. ASOCIATIVIDAD DERECHA (**)")
    print("-" * 40)
    
    examples_right = [
        "2 ** 3 ** 2",    # 2 ** (3 ** 2) = 2 ** 9 = 512
        "3 ** 2 ** 2",    # 3 ** (2 ** 2) = 3 ** 4 = 81
    ]
    
    for expr in examples_right:
        lexer = Lexer(expr)
        parser = Parser(lexer)
        tree = parser.parse()
        result = interpreter.interpret(tree)
        print(f"{expr:12} = {result:8} (AST: {tree})")
    
    # Ejemplos de precedencia mixta
    print("\n3. PRECEDENCIA Y ASOCIATIVIDAD MIXTA")
    print("-" * 40)
    
    examples_mixed = [
        "1 + 2 * 3 ** 2 - 4",     # 1 + 2 * 9 - 4 = 15
        "2 ** 3 * 4 + 5",         # 8 * 4 + 5 = 37
        "-2 ** 2",                # -(2 ** 2) = -4
        "3 + 4 * 2 ** 3 - 1"      # 3 + 4 * 8 - 1 = 34
    ]
    
    for expr in examples_mixed:
        lexer = Lexer(expr)
        parser = Parser(lexer)
        tree = parser.parse()
        result = interpreter.interpret(tree)
        print(f"{expr:20} = {result:8}")
        print(f"{'':20}   AST: {tree}")
        print()
    
    # Ejemplos de asignación (asociatividad derecha)
    print("\n4. ASIGNACIONES (ASOCIATIVIDAD DERECHA)")
    print("-" * 40)
    
    assignment_examples = [
        "a = 5",
        "b = a = 10",      # b = (a = 10)
        "c = b = a = 15"   # c = (b = (a = 15))
    ]
    
    for expr in assignment_examples:
        lexer = Lexer(expr)
        parser = Parser(lexer)
        tree = parser.parse()
        result = interpreter.interpret(tree)
        print(f"{expr:15} -> {result}")
        print(f"Variables: {interpreter.variables}")
        print(f"AST: {tree}")
        print()
    
    # Demostración de la diferencia entre asociatividades
    print("\n5. COMPARACIÓN: IZQUIERDA vs DERECHA")
    print("-" * 40)
    
    print("Si la resta fuera asociativa por la derecha:")
    print("5 - 3 - 2 sería 5 - (3 - 2) = 5 - 1 = 4")
    print("Pero es asociativa por la izquierda:")
    print("5 - 3 - 2 es (5 - 3) - 2 = 2 - 2 = 0")
    
    print("\nSi la potencia fuera asociativa por la izquierda:")
    print("2 ** 3 ** 2 sería (2 ** 3) ** 2 = 8 ** 2 = 64")
    print("Pero es asociativa por la derecha:")
    print("2 ** 3 ** 2 es 2 ** (3 ** 2) = 2 ** 9 = 512")
    
    print("\n6. TABLA DE PRECEDENCIA IMPLEMENTADA")
    print("-" * 40)
    precedence_table = [
        ("Más alta", "**", "Derecha", "Potenciación"),
        ("", "Unario +, -", "Derecha", "Operadores unarios"),
        ("", "*, /", "Izquierda", "Multiplicación, división"),
        ("", "+, -", "Izquierda", "Suma, resta"),
        ("Más baja", "=", "Derecha", "Asignación")
    ]
    
    print(f"{'Precedencia':12} {'Operador':12} {'Asociat.':10} {'Descripción':20}")
    print("-" * 60)
    for prec, op, assoc, desc in precedence_table:
        print(f"{prec:12} {op:12} {assoc:10} {desc:20}")


if __name__ == "__main__":
    demonstrate_associativity()
    
    print("\n" + "=" * 60)
    print("MODO INTERACTIVO")
    print("=" * 60)
    print("Ingresa expresiones para evaluar (escribe 'quit' para salir)")
    print("Ejemplos: 2 ** 3 ** 2, 5 - 3 - 2, a = b = 10")
    
    interpreter = Interpreter()
    
    while True:
        try:
            text = input("\n>>> ").strip()
            if text.lower() in ('quit', 'exit', 'q'):
                break
            if not text:
                continue
            
            lexer = Lexer(text)
            parser = Parser(lexer)
            tree = parser.parse()
            result = interpreter.interpret(tree)
            
            print(f"Resultado: {result}")
            print(f"AST: {tree}")
            if interpreter.variables:
                print(f"Variables: {interpreter.variables}")
                
        except Exception as e:
            print(f"Error: {e}")
