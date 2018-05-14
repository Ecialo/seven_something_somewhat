import operator
from yaml import (
    SequenceNode,
    ScalarNode,
)
from collections import deque

from .property import (
    Property,
    Const,
    Oper,
)
from .funcs import (
    func_constructor,
    FUNC_TAG,
)


class ExpressionError(Exception):
    pass


class Expression(Property):

    OPERATORS = {
        '*': (operator.mul, 4),
        '+': (operator.add, 3),
        '-': (operator.sub, 3),
        '==': (operator.eq, 2),
        '!=': (operator.ne, 2),
        '>': (operator.gt, 2),
        '<': (operator.lt, 2),
        '>=': (operator.ge, 2),
        '<=': (operator.le, 2),
        'in': (lambda a, b: a in b, 2),
        'not in': (lambda a, b: a not in b, 2),
        'and': (operator.and_, 1),
        'or': (operator.or_, 1)
    }

    UTILITY = {'(', ')'} | set(OPERATORS.keys())

    def __init__(self, expression):
        self.raw_expression = expression
        self.expression = self.make_tree(self.inf_2_post(expression))

    def __repr__(self):
        return " ".join([str(token) for token in self.raw_expression])

    def get(self, context):
        return self.expression.get(context)

    def inf_2_post(self, expression):
        OPERATORS = self.OPERATORS
        UTILITY = self.UTILITY

        stack = deque()
        output = deque()
        for token in expression:
            if token in UTILITY:
                if token == '(':
                    stack.append(token)
                elif token == ')':
                    for i in range(1000):
                        if stack[-1] == '(':
                            break
                        output.append(stack.pop())
                    else:
                        raise ExpressionError()
                    stack.pop()
                else:
                    while stack and stack[-1] in OPERATORS and OPERATORS[token][-1] <= OPERATORS[stack[-1]][-1]:
                        output.append(stack.pop())
                    stack.append(token)
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
        return list(output)

    def make_tree(self, post_tokens):
        OPERATORS = self.OPERATORS
        UTILITY = self.UTILITY

        stack = deque()

        for token in post_tokens:
            if token not in UTILITY:
                # print(token, type(token), isinstance(token, Property))
                if isinstance(token, Property):
                    stack.append(token)
                else:
                    stack.append(Const(token))
            else:
                right = stack.pop()
                left = stack.pop()
                stack.append(Oper(OPERATORS[token][0], left, right))
        return stack.pop()


def expression_constructor(loader, node):
    # print(node)
    # expression = loader.construct_sequence(node)
    expression = []
    for child in node.value:
        if isinstance(child, SequenceNode) and child.tag == FUNC_TAG:
            # print(child)
            func = func_constructor(loader, child)
            # print(func)
            expression.append(func)
        elif isinstance(child, SequenceNode):
            # print(child)
            expression.extend(loader.construct_sequence(child))
        elif isinstance(child, ScalarNode):
            expression.append(loader.construct_object(child))
        # else:
        #     expression.append(loader.construct_object(child))
            # raise ExpressionError
    #     print("ololo")
    #     print(child)
    #     expression.extend(loader.construct_object(child))
    #     print(loader.construct_object(child))
    #     print(loader.construct_sequence(child))
    # expression = loader.construct_object(node)
    # print(expression)
    # result_expression = []
    # for part in expression:
    #     if isinstance(part, list):
    #         result_expression.extend(part)
    #     else:
    #         result_expression.append(part)
    # print(result_expression)
    # print(expression)
    return Expression(expression)

EXPRESSION_TAG = "!expr"

if __name__ == '__main__':
    a = [3, '+', 4, '*', '(', 2, '-', 1, ')']
    q = Expression(None)
    z = q.inf_2_post(a)
    print(q.make_tree(z).get(None))
