import re

# 首先，定义了各种记号的正则表达式模式
tokens = {
    'DRAW': r'DRAW',
    'MOVE': r'MOVE',
    'COLOR': r'COLOR',
    'ARC': r'ARC',  # New token for the ARC command
    'NUMBER': r'\d+',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'COMMA': r',',
    'COLOR_NAME': r'RED|GREEN|BLUE|YELLOW|BLACK'
}


def tokenize(code):
    # 接着，生成一个包含所有记号模式的正则表达式：
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in tokens.items())
    # 然后，re.finditer(token_regex, code) 用于找到所有匹配的记号，并生成它们的类型、值和位置：
    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        token_pos = match.start()
        yield (token_type, token_value, token_pos)



class Parser:
    # 初始化解析器，接收一个记号列表 tokens 并设置初始位置和预读记号
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.position = 0
        self.lookahead = self.tokens[self.position] if self.tokens else None

    # 消费一个记号，如果当前记号类型匹配预期类型，则移动到下一个记号；否则抛出语法错误。
    def consume(self, token_type):
        if self.lookahead and self.lookahead[0] == token_type:
            current_token = self.lookahead
            self.position += 1
            self.lookahead = self.tokens[self.position] if self.position < len(self.tokens) else None
            return current_token
        else:
            error_message = f"Expected {token_type}, got {self.lookahead[0]} at position {self.lookahead[2]}"
            raise SyntaxError(error_message)

    # 解析整个程序，调用 parse_statement_list 方法，返回一个包含所有语句的程序节点
    def parse_program(self):
        statements = self.parse_statement_list()
        return ('program', statements)

    # 解析语句列表，循环调用 parse_statement 方法，直到没有更多记号
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
        elif self.lookahead[0] == 'ARC':  # Handle the ARC command
            return self.parse_arc_statement()
        else:
            raise SyntaxError("Invalid statement")

    def parse_draw_statement(self):
        try:
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
        except SyntaxError as e:
            print(f"Error in DRAW statement: {str(e)}")
            raise

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

    def parse_arc_statement(self):
        self.consume('ARC')
        self.consume('LPAREN')
        x = self.consume('NUMBER')[1]
        self.consume('COMMA')
        y = self.consume('NUMBER')[1]
        self.consume('COMMA')
        radius = self.consume('NUMBER')[1]
        self.consume('COMMA')
        start_angle = self.consume('NUMBER')[1]
        self.consume('COMMA')
        end_angle = self.consume('NUMBER')[1]
        self.consume('RPAREN')
        return ('arc', (int(x), int(y)), int(radius), int(start_angle), int(end_angle))

# --- Semantic Analysis ---
# 对抽象语法树进行处理，执行绘制命令
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


# Usage
source_code = '''
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
'''
# tokens = list(tokenize(source_code))  # 将生成器转换为列表
# parser = Parser(tokens)
# parsed_program = parser.parse_program()
# semantic_analysis(parsed_program)


import matplotlib.pyplot as plt

# Initialize a figure
fig, ax = plt.subplots()

# Starting position and color
current_position = (0, 0)
current_color = 'black'

import matplotlib.patches as patches

def semantic_analysis(node):
    global current_position, current_color
    if node[0] == 'program':
        for stmt in node[1]:
            semantic_analysis(stmt)
    elif node[0] == 'draw':
        start, end = node[1], node[2]
        plt.plot([start[0], end[0]], [start[1], end[1]], color=current_color)
    elif node[0] == 'move':
        position = node[1]
        current_position = position
    elif node[0] == 'color':
        color = node[1].lower()
        current_color = color
    elif node[0] == 'arc':
        center, radius, start_angle, end_angle = node[1], node[2], node[3], node[4]
        arc = patches.Arc(center, 2*radius, 2*radius, angle=0, theta1=start_angle, theta2=end_angle, color=current_color)
        ax.add_patch(arc)
        print(f"Drawing arc at {center} with radius {radius}, from {start_angle}° to {end_angle}° in {current_color}")
    else:
        raise ValueError("Unknown command")

# Usage example as before
tokens = list(tokenize(source_code))
parser = Parser(tokens)
parsed_program = parser.parse_program()
semantic_analysis(parsed_program)

# Show the plot
plt.axis('equal')
plt.show()
