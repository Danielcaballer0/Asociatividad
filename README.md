# Asociatividad en Compiladores

---

## 1. Introducción a la Asociatividad

### Definición
La asociatividad determina el orden de evaluación de operadores con el mismo nivel de precedencia en una expresión.

### Contexto en compiladores
- Forma parte del proceso de análisis sintáctico
- Afecta directamente la construcción del árbol sintáctico (AST)
- Determina la semántica de las expresiones del lenguaje

---

## 2. Tipos de Asociatividad

### Asociatividad izquierda
- Evaluación de izquierda a derecha
- Ejemplo: `a - b - c` → `(a - b) - c`
- Operadores comunes: `+`, `-`, `*`, `/`

### Asociatividad derecha
- Evaluación de derecha a izquierda
- Ejemplo: `a = b = c` → `a = (b = c)`
- Operadores comunes: `=`, `**`, operadores unarios

### No asociatividad
- Prohibición de encadenamiento de operadores
- Ejemplo: `a < b < c` (en algunos lenguajes)
- Genera error sintáctico o se interpreta de forma especial

---
#### esto va luego de la tabla
## A destacar:

1. **Variación entre lenguajes**: A modo general, se resalta los operadores de asociatividad, pero está relacionado con python

2. **Casos especiales**:
   - Las comparaciones en Python son no asociativas en el sentido tradicional pero permiten encadenamiento con semántica especial. Por ejemplo, `a < b < c` se interpreta como `a < b and b < c`.
   - El operador walrus (`:=`) introducido en Python 3.8 permite asignación dentro de expresiones.

3. **Diferencias notables en otros lenguajes**:
   - En C/C++, el operador de coma tiene la precedencia más baja.
   - En JavaScript, el operador de asignación tiene precedencia diferente.
   - En algunos lenguajes funcionales, los operadores pueden tener asociatividad personalizable.

4. **Impacto en el parser**:
   - La implementación de esta tabla de precedencia y asociatividad se refleja en la estructura gramatical del parser.
   - Cada nivel de precedencia corresponde típicamente a una función específica en un parser recursivo descendente.

---
## 3. Importancia en los Compiladores

### Corrección semántica
- Garantiza que las expresiones se evalúen según la especificación del lenguaje
- Preserva la intención del programador

### Consistencia
- Mantiene comportamiento predecible del código
- Evita ambigüedades en la evaluación de expresiones

### Optimización
- Permite al compilador reorganizar operaciones preservando semántica
- Facilita optimizaciones como folding y evaluación parcial

---

## 4. Implementación en el Análisis Sintáctico

### Técnicas comunes
1. **Gramáticas con niveles de precedencia**
   - Cada nivel de precedencia tiene su propia producción
   - La estructura de llamadas recursivas implementa asociatividad

2. **Resolución de conflictos**
   - En parsers LR/LALR: resolución de conflictos shift/reduce
   - Tablas de precedencia y asociatividad

3. **Construcción explícita del AST**
   - Organización del árbol según reglas de asociatividad
   - Procesamiento del árbol respetando el orden correcto

---

## 5. Demostración Práctica

### Implementación de un parser para un subconjunto de Python
- Analizador léxico (Lexer)
- Parser descendente recursivo
- Árbol de sintaxis abstracta (AST)
- Intérprete para evaluación

### Estructura gramatical
```
expr   : term ((PLUS | MINUS) term)*
term   : power ((MUL | DIV) power)*
power  : factor (POW factor)*
factor : (PLUS | MINUS) factor | NUM | LPAREN expr RPAREN | variable
```

---

## 6. Casos de Uso y Consideraciones Prácticas

### Diseño de lenguajes
- Elección de asociatividad afecta directamente la usabilidad del lenguaje
- Convenciones comunes entre lenguajes crean expectativas en programadores

### Ejemplos en lenguajes populares
- Python: operador de potencia (`**`) asociativo por la derecha
- C/C++/Java: operadores aritméticos asociativos por la izquierda
- Haskell: permite definir asociatividad personalizada (`infixl`, `infixr`)

### Problemas comunes
- Errores sutiles por malinterpretación de la asociatividad
- Diferencias entre lenguajes que confunden a los programadores

---

## 7. Implementación en Acción: Ejemplos

### Asociatividad izquierda
```python
a = 5
b = 3
c = 2
a - b - c  # = (5 - 3) - 2 = 0
```

### Asociatividad derecha
```python
2 ** 3 ** 2  # = 2 ** (3 ** 2) = 2 ** 9 = 512
```

### Precedencia mixta
```python
1 + 2 * 3 ** 2 - 4 / 2  # = 1 + 2 * 9 - 2 = 1 + 18 - 2 = 17
```

---
# Tabla de Precedencia y Asociatividad de Operadores


| Nivel | Operador | Descripción | Asociatividad | Ejemplo | Evaluación |
|-------|----------|-------------|---------------|---------|------------|
| 1 | `()` | Paréntesis | None | `(a + b) * c` | Primero se evalúa la expresión dentro de paréntesis |
| 2 | `**` | Potencia/Exponenciación | Derecha | `a ** b ** c` | `a ** (b ** c)` |
| 3 | `+x`, `-x`, `~x` | Unarios positivo, negativo, NOT bit a bit | Derecha | `-a ** 2` | `-(a ** 2)` |
| 4 | `*`, `/`, `//`, `%` | Multiplicación, división, división entera, módulo | Izquierda | `a * b / c` | `(a * b) / c` |
| 5 | `+`, `-` | Suma, resta | Izquierda | `a + b - c` | `(a + b) - c` |
| 6 | `<<`, `>>` | Desplazamiento bit a bit | Izquierda | `a << b << c` | `(a << b) << c` |
| 7 | `&` | AND bit a bit | Izquierda | `a & b & c` | `(a & b) & c` |
| 8 | `^` | XOR bit a bit | Izquierda | `a ^ b ^ c` | `(a ^ b) ^ c` |
| 9 | `\|` | OR bit a bit | Izquierda | `a \| b \| c` | `(a \| b) \| c` |
| 10 | `==`, `!=`, `<`, `>`, `<=`, `>=`, `is`, `is not`, `in`, `not in` | Comparaciones, pruebas de identidad, pruebas de pertenencia | No asociativo | `a < b < c` | Especial: `a < b and b < c` |
| 11 | `not` | NOT lógico | Derecha | `not a and b` | `(not a) and b` |
| 12 | `and` | AND lógico | Izquierda | `a and b and c` | `(a and b) and c` |
| 13 | `or` | OR lógico | Izquierda | `a or b or c` | `(a or b) or c` |
| 14 | `if-else` (ternario) | Expresión condicional | Derecha | `a if b else c if d else e` | `a if b else (c if d else e)` |
| 15 | `:=` | Operador de asignación con expresión (walrus) | Derecha | `(a := b) + c` | Asigna y luego usa el valor |
| 16 | `=`, `+=`, `-=`, `*=`, etc. | Asignación y asignación compuesta | Derecha | `a = b = c` | `a = (b = c)` |
| 17 | `,` | Coma (tupla) | Izquierda | `a, b, c` | Crea una tupla `(a, b, c)` |

