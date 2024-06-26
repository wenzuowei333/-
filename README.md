# 项目实现详细介绍

## 目录

- [项目简介](#项目简介)
- [EBNF 的设计](#EBNF-的设计)
  - [EBNF](#EBNF)
  - [词法规则](#词法规则)
  - [语法规则](#语法规则)
  - [非正式语义规则](#非正式语义规则)
  - [源程序示例](#源程序示例)
    - [正确的源程序示例](#正确的源程序示例)
    - [错误的源程序示例](#错误的源程序示例)
- [词法分析](#词法分析)
  - [主要的数据结构](#主要的数据结构)
  - [整体状态图描述](#整体状态图描述)
  - [手工编写词法分析程序的算法流程图概述](#手工编写词法分析程序的算法流程图概述)
- [语法分析](#语法分析)
  - [数据结构](#数据结构)
  - [伪代码](#伪代码)
- [语义分析](#语义分析)
  - [主要数据结构](#主要数据结构)
  - [算法流程](#算法流程)
  - [伪代码](#伪代码)
- [功能演示](#功能演示)
  - [使用 python 编写的绘图解释器功能演示](#使用-python-编写的绘图解释器功能演示)
  - [LEX 和 YACC 词法和语法分析器功能展示](#LEX-和-YACC-词法和语法分析器功能展示)

## 项目简介

本项目为编译原理课设的实现，实现以下需求

1. 使用Python完成一套绘图语言的词法分析、语法分析和语义分析，实现基本的绘图功能
2. 使用LEX+Bison完成词法分析和语法分析

![](https://gitee.com/wenzuowei/warehouse/raw/master/pictures/image_ktPZr3-pq3.png)

## EBNF 的设计

### EBNF

```bash
<program> ::= <statement-list>

<statement-list> ::= <statement> | <statement> <statement-list>

<statement> ::= <draw-statement> | <move-statement> | <color-statement> | <arc-statement>

<draw-statement> ::= "DRAW" <point> <point>

<move-statement> ::= "MOVE" <point>

<color-statement> ::= "COLOR" <color>

<arc-statement> ::= "ARC" <point> <number> <number> <number>

<point> ::= "(" <number> "," <number> ")"

<color> ::= "RED" | "GREEN" | "BLUE" | "YELLOW" | "BLACK"

<number> ::= <digit> | <digit> <number>

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

```

### 词法规则

- Keywords: “DRAW”、“MOVE”、“COLOR”以及颜色名称，例如“RED”、“GREEN”等. 。
- Punctuation: “(”和“)”表示包围点，“,”表示分隔坐标。
- Numbers: 表示点坐标的数字序列。

### 语法规则

- \<program>：由一个语句列表（\<statement-list>）组成，代表整个程序。
- \<statement-list>：可以是单个语句（\<statement>），也可以是一个语句后跟另一个语句列表，即语句可以连续出现。
- \<statement>：可以是四种类型之一：绘制（\<draw-statement>）、移动（\<move-statement>）、更改颜色（\<color-statement>）或画弧（\<arc-statement>）。
- \<draw-statement>：绘制直线，从一个点（\<point>）到另一个点。
- \<move-statement>：移动到某个点（\<point>）。
- \<color-statement>：改变当前绘图颜色为指定颜色（\<color>）。

\<arc-statement>：在给定中心点（\<point>），绘制一个弧，弧的参数包括半径和角度起始点、角度终点。

### 非正式语义规则

- 当执行“DRAW”语句时，它会在两个指定点之间绘制一条线或形状。
- 当执行“MOVE”语句时，它将绘图工具移动到指定点。
- 当执行“COLOR”语句时，它将绘图工具的颜色更改为指定的颜色。
- **ARC**命令以某点为中心绘制一段圆弧，圆弧的大小和方向由给定的角度参数确定。
- 对无效输入的错误处理，例如不正确的关键字、格式错误的点或超出范围的坐标。

### 源程序示例

#### 正确的源程序示例

```sass&#x20;(sass)&#x20;
DRAW (10,20) (30,40)
MOVE (50,60)
COLOR RED
```

#### 错误的源程序示例

```sass&#x20;(sass)&#x20;
DRAW (10,20) 30,40)  // Missing opening parenthesis
MOOVE (50,60)        // Misspelled keyword
COLOR PINK           // Unsupported color
```

## 词法分析

```python
tokens = (
    'DRAW', 'MOVE', 'COLOR',
    'NUMBER', 'LPAREN', 'RPAREN', 'COMMA',
    'COLOR_NAME'
)

t_DRAW = r'DRAW'
t_MOVE = r'MOVE'
t_COLOR = r'COLOR'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_COLOR_NAME = r'RED|GREEN|BLUE|YELLOW|BLACK'
t_ignore = ' \t'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  # Convert string to integer
    return t


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()


def tokenize(code):
    # Build the regular expression
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in tokens.items())
    # Scan through the code and yield tokens as they match the patterns
    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        yield (token_type, token_value)
```

**代码解释：**

1. 定义了一个字典`tokens`，其中包含了各种词法规则的名称（如'DRAW', 'MOVE'等）以及与之对应的正则表达式模式。
2. `tokenize`函数接收源代码字符串作为输入参数`code`。
3. 函数内部首先构建了一个大的正则表达式`token_regex`，它是通过遍历`tokens`字典，为每个词法规则生成一个命名组（使用`(?P<name>pattern)`的形式），然后将这些命名组合并成一个大的正则表达式字符串。这样做的目的是使得正则表达式能够识别并分类不同的词法元素。
4. 接着，使用`re.finditer()`函数和构建的正则表达式在源代码字符串上查找匹配项。对于每个匹配到的词法单元，通过`match.lastgroup`获取匹配成功的分组名（即词法类型），并通过`match.group(token_type)`获取该词法单元的具体值。
5. 最后，通过`yield`语句生成一个个包含词法类型和值的元组，形成一个生成器。这个生成器可以被迭代，用于后续的语法分析或其他处理。

### 主要的数据结构

1. **Token定义** (`tokens`字典): 这是一个字典，键是词法记号的名称（例如 `'DRAW'`, `'MOVE'`, `'NUMBER'` 等），值是与之匹配的正则表达式字符串。这种结构用于定义语言中所有可能的词法元素及其识别模式。
2. **Token生成器** (`tokenize`函数返回值): 生成器产出的是元组 `(token_type, token_value)`，其中 `token_type` 是从 `tokens` 字典中匹配到的键，代表词法记号的类别，而 `token_value` 是实际匹配到的字符串内容。这是一种流式的数据结构，适合逐个处理词法单元。

### 整体状态图描述

- **初始状态 (Start)**: 读取源代码的下一个字符，尝试与`tokens`字典中定义的所有模式进行匹配。
- **匹配状态 (Match)**: 一旦找到匹配项，根据匹配的模式确定当前词法单元的类型，并记录其值。然后返回到初始状态继续处理下一个字符。
- **结束状态 (End-of-Input)**: 如果没有更多字符或无法匹配任何模式，分析结束。

状态之间的转换基于正则表达式的匹配结果，每成功匹配一个模式即完成一个词法单元的识别，并准备识别下一个。

### 手工编写词法分析程序的算法流程图概述

![](https://gitee.com/wenzuowei/warehouse/raw/master/pictures/1715774402148-a749d0c8-523a-420b-9282-c2219cbc1907.png)

## 语法分析

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.position = 0
        self.lookahead = self.tokens[self.position] if self.tokens else None

    def consume(self, token_type):
        if self.lookahead and self.lookahead[0] == token_type:
            current_token = self.lookahead
            self.position += 1
            self.lookahead = self.tokens[self.position] if self.position < len(self.tokens) else None
            return current_token
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.lookahead[0]}")

    def parse_program(self):
        statements = self.parse_statement_list()
        return ('program', statements)

    def parse_statement_list(self):
        statements = [self.parse_statement()]
        while self.lookahead and self.lookahead[0] != 'EOF':
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        if self.lookahead[0] == 'DRAW':
            return self.parse_draw_statement()
        elif self.lookahead[0] == 'MOVE':
            return self.parse_move_statement()
        elif self.lookahead[0] == 'COLOR':
            return self.parse_color_statement()
        else:
            raise SyntaxError("Invalid statement")

    def parse_draw_statement(self):
        self.consume('DRAW')
        self.consume('LPAREN')
        x1 = self.consume('NUMBER')[1]
        self.consume('COMMA')
        y1 = self.consume('NUMBER')[1]
        self.consume('RPAREN')
        self.consume('LPAREN')
        x2 = self.consume('NUMBER')[1]
        self.consume('COMMA')
        y2 = self.consume('NUMBER')[1]
        self.consume('RPAREN')
        return ('draw', (int(x1), int(y1)), (int(x2), int(y2)))

    def parse_move_statement(self):
        self.consume('MOVE')
        self.consume('LPAREN')
        x = self.consume('NUMBER')[1]
        self.consume('COMMA')
        y = self.consume('NUMBER')[1]
        self.consume('RPAREN')
        return ('move', (int(x), int(y)))

    def parse_color_statement(self):
        self.consume('COLOR')
        color = self.consume('COLOR_NAME')[1]
        return ('color', color)
```

### 数据结构

1. **tokens**: 一个列表，存储了输入的标记序列。每个标记是一个元组，例如 `('DRAW',)` 或 `('NUMBER', 5)`，第一个元素是标记类型，第二个元素（如果存在）是该类型的具体值。
2. **position**: 整数，表示当前处理到的标记在 `tokens` 列表中的索引位置。
3. **lookahead**: 当前正在检查的标记，初始化为 `tokens` 中的第一个标记或 `None`（如果列表为空）。这是解析器用来决定下一步操作的关键状态变量

### 伪代码

```python
初始化 Parser 类:
- 输入: tokens（标记列表）
- 初始化 position 为 0
- 初始化 lookahead 为 tokens 的第一个标记或 None

定义 consume 方法:
- 如果 lookahead 匹配给定的 token_type:
  - 保存并返回当前标记
  - 更新 position 和 lookahead
- 否则抛出 SyntaxError

定义 parse_program 方法:
- 调用 parse_statement_list 并将结果作为 'program' 类型的语句返回

定义 parse_statement_list 方法:
- 初始化一个包含当前语句的 statements 列表
- 当 lookahead 不是 'EOF' 时:
  - 添加从 parse_statement 获得的新语句到 statements
- 返回 statements 列表

定义 parse_statement 方法:
- 根据 lookahead 的类型调用相应的解析方法 (parse_draw_statement, parse_move_statement, parse_color_statement)
- 如果没有匹配的类型，则抛出 SyntaxError

定义 parse_draw_statement, parse_move_statement, parse_color_statement 方法:
- 按照语法结构消耗相应的标记（如 'DRAW', 'MOVE', 'COLOR', 数字等）
- 解析并构造对应的图形操作指令
- 返回指令结构，如 ('draw', (x1, y1), (x2, y2))
```

整个解析过程是基于递归下降的，从顶层的 `parse_program` 开始，逐步分解复杂的语言结构为更简单的组成部分，直到基本的语法单元。

## 语义分析

```python
# --- Semantic Analysis ---

def semantic_analysis(node):
    if node[0] == 'program':
        for stmt in node[1]:
            semantic_analysis(stmt)
    elif node[0] == 'draw':
        start, end = node[1], node[2]
        print(f"Drawing from {start} to {end}")
    elif node[0] == 'move':
        position = node[1]
        print(f"Moving to {position}")
    elif node[0] == 'color':
        color = node[1]
        print(f"Setting color to {color}")
    else:
        raise ValueError("Unknown command")
```

### 主要数据结构

- **AST Node**: 抽象语法树（Abstract Syntax Tree）的节点，采用元组形式表示，如 `(类型, 数据1, 数据2,...)`。其中，`类型` 是字符串，标识节点的类别，如 `'program'`, `'draw'`, `'move'`, `'color'`；`数据1`, `数据2`, ... 是与节点类型相关的值。

### 算法流程

1. **开始**
   - 开始执行`semantic_analysis`函数，接收一个AST节点作为输入。
2. **判断节点类型**
   - **如果是 ****`**'program'**`**** 类型**：
     - 遍历 `node[1]` 中的每个子语句。
     - 对每个子语句递归调用 `semantic_analysis` 函数。
     - 继续处理下一个子语句（如果存在）直到遍历结束。
   - **如果是 ****`**'draw'**`**** 类型**：
     - 解包 `node[1]` 和 `node[2]` 分别为起始点 `start` 和终点 `end`。
     - 打印消息：“Drawing from {start} to {end}”。
     - 结束当前节点处理，返回上一层或继续处理下一个兄弟节点。
   - **如果是 ****`**'move'**`**** 类型**：
     - 解包 `node[1]` 为位置 `position`。
     - 打印消息：“Moving to {position}”。
     - 结束当前节点处理，返回上一层或继续处理下一个兄弟节点。
   - **如果是 ****`**'color'**`**** 类型**：
     - 解包 `node[1]` 为颜色 `color`。
     - 打印消息：“Setting color to {color}”。
     - 结束当前节点处理，返回上一层或继续处理下一个兄弟节点。
   - **其他类型**：
     - 抛出 `ValueError` 异常，消息为 “Unknown command”。
3. **结束**
   - 所有节点处理完毕，函数结束。

### 伪代码

```python
function semantic_analysis(node):
    begin
        if node[0] == 'program':
            for each child_node in node[1]:
                semantic_analysis(child_node)  # 递归处理子节点
        else if node[0] == 'draw':
            start, end = node[1], node[2]
            print("Drawing from", start, "to", end)
        else if node[0] == 'move':
            position = node[1]
            print("Moving to", position)
        else if node[0] == 'color':
            color = node[1]
            print("Setting color to", color)
        else:
            raise ValueError("Unknown command")
    end
```

## 功能演示

### 使用 python 编写的绘图解释器功能演示

**国旗绘制****绘图代码：**

```python
COLOR RED
MOVE (20, 20)
DRAW (20, 20) (20, 80)
MOVE (20, 80)
DRAW (20, 80) (100, 80)
MOVE (100, 80)
DRAW (100, 80) (100, 20)
MOVE (100, 20)
DRAW (100, 20) (20, 20)
COLOR YELLOW
MOVE (26, 68)
DRAW (26, 68) (33, 68)
MOVE (33, 68)
DRAW (33, 68) (35, 74)
MOVE (35, 74)
DRAW (35, 74) (37, 68)
MOVE (37, 68)
DRAW (37, 68) (44, 68)
MOVE (44, 68)
DRAW (44, 68) (38, 64)
MOVE (38, 64)
DRAW (38, 64) (40, 58)
MOVE (40, 58)
DRAW (40, 58) (35, 61)
MOVE (35, 61)
DRAW (35, 61) (30, 58)
MOVE (30, 58)
DRAW (30, 58) (32, 64)
MOVE (32, 64)
DRAW (32, 64) (26, 68)
```

**绘制效果：**

![image.png](https://gitee.com/wenzuowei/warehouse/raw/master/pictures/1715775349225-aebddbbd-9126-406e-839f-f19bc3538c55.png "image.png")

**太阳绘制****绘图代码：**

```python
COLOR YELLOW
MOVE (150, 150)
ARC (150, 150, 40, 0, 360)
MOVE (130, 150)
DRAW (110, 150) (70, 150)
MOVE (170, 150)
DRAW (190, 150) (230, 150)
MOVE (150, 130)
DRAW (150, 110) (150, 70)
MOVE (150, 170)
DRAW (150, 190) (150, 230)
MOVE (135, 135)
DRAW (120, 120) (90, 90)
MOVE (165, 165)
DRAW (180, 180) (210, 210)
MOVE (165, 135)
DRAW (180, 120) (210, 90)
MOVE (135, 165)
DRAW (120, 180) (90, 210)
COLOR YELLOW
```

**绘制效果：**

![image.png](https://gitee.com/wenzuowei/warehouse/raw/master/pictures/1715775504554-b80fb518-e205-42b7-99f7-856fd411374b.png "image.png")

### LEX 和 YACC 词法和语法分析器功能展示

![](https://gitee.com/wenzuowei/warehouse/raw/master/pictures/1715775579037-43bcfa59-e543-4e3f-a4ae-f714b1700246.png)

```python
Enter your commands:
COLOR RED
Change color to Red
MOVE (20, 20)
Move to (20,20)
DRAW (20, 20) (20, 80)
Draw from (20,20) to (20,80)
MOVE (20, 80)
Move to (20,80)
DRAW (20, 80) (100, 80)
Draw from (20,80) to (100,80)
MOVE (100, 80)
Move to (100,80)
DRAW (100, 80) (100, 20)
Draw from (100,80) to (100,20)
MOVE (100, 20)
Move to (100,20)
DRAW (100, 20) (20, 20)
Draw from (100,20) to (20,20)
COLOR YELLOW
Change color to Yellow
MOVE (26, 68)
Move to (26,68)
DRAW (26, 68) (33, 68)
Draw from (26,68) to (33,68)
MOVE (33, 68)
Move to (33,68)
DRAW (33, 68) (35, 74)
Draw from (33,68) to (35,74)
MOVE (35, 74)
```
