# Calculator tutorial

A tutorial for parsing of arithmetic expressions.

---

!!! note "TODO"
    This tutorial will be based on [Calc example](https://github.com/igordejanovic/Arpeggio/tree/master/examples/calc).

In this tutorial we will make a parser and evaluator for simple arithmetic expression
(numbers and operations - addition, substraction, multiplication and division).
The parser will be able to recognize following expressions:

    2+7-3.6
    3/(3-1)+45*2.17+8
    4*12+5-4*(2-8)
    ...

Evaluation will be done using [support for semantic analysis](../semantics.md)


Let's start with grammar definition first. Expression parsing has additional


