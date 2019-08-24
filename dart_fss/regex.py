# -*- coding: utf-8 -*-
import re


def is_operator(item):
    """  연산자 여부 검색

    Parameters
    ----------
    item : str
        단어

    Returns
    -------
    bool
        True: 연산자 / False: 일단단어

    """
    if item in ['AND', 'OR']:
        return True
    return False


def precedence(symbol):
    """ 연산자 우선수위

    Parameters
    ----------
    symbol: str
        연산자

    Returns
    -------
    int
        연산자 순위

    """
    if symbol in ['AND', 'OR']:
        return 1
    return 0


def infix_to_postfix(infix):
    """ infix를 postfix로 변환하는 함수

    Parameters
    ----------
    infix: str
        infix 형태로 표현된 문장

    Returns
    -------
    str
        postfix로 변횐된 문장
    """
    stack = []
    results = []
    parenthesis = 0
    for item in infix:
        if item == '(':
            parenthesis = parenthesis + 1
            stack.append(item)
        elif item == ')':
            parenthesis = parenthesis - 1
            if parenthesis < 0:
                raise SyntaxError('Missing left parentheses.')
            while stack[-1] != '(':
                v = stack.pop()
                results.append(v)
            stack.pop()
        elif is_operator(item):
            if len(stack) > 0:
                if precedence(stack[-1]) < precedence(item):
                    stack.append(item)
                else:
                    v = stack.pop()
                    stack.append(item)
                    results.append(v)
            else:
                stack.append(item)
        else:
            results.append(item)
    while len(stack) > 0:
        results.append(stack.pop())

    if parenthesis > 0:
        raise SyntaxError('Missing right parentheses.')

    return results


def str_to_regex(query):
    """ regular expression

    Parameters
    ----------
    query: str
        검색 문구

    Returns
    -------
    Pattern
        regular expression pattern
    """
    return re.compile(str_to_pattern(query))


def str_to_pattern(query):
    """ AND OR 등 연산자를 regular expression 표현으로 변경

    Parameters
    ----------
    query: str
        검색 문구

    Returns
    -------
    str
        검색 pattern
    """
    query = query.replace('(', ' ( ').replace(')', ' ) ').split()
    postfix = infix_to_postfix(query)

    stack = []
    for item in postfix:
        if is_operator(item):
            if item == 'AND':
                operand1 = stack.pop()
                operand2 = stack.pop()
                pattern = r'(?=.*{0})(?=.*{1})'.format(operand2, operand1)
            elif item == 'OR':
                operand1 = stack.pop()
                operand2 = stack.pop()
                pattern = r'({0}|{1})'.format(operand2, operand1)
            stack.append(pattern)
        else:
            stack.append(item)
    return stack.pop()
