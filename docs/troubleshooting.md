# Troubleshooting Guide

Common problems and mistakes

---

## Left recursion and RecursionError

If you get `RecursionError: maximum recursion depth exceeded while calling a
Python object` it is a good indication that you have a [left
recursion](https://en.wikipedia.org/wiki/Left_recursion) in the grammar.

!!! note
    Arpeggio parser will implement a support for detecting and reporting of left
    recursions in the grammar. See [issue
    23](https://github.com/textX/Arpeggio/issues/23)

A left recursion is found if the parser calls the same rule again while no
characters from the input is consumed from the previous call (e.g. we have the
same state). This will lead to the same sequence of events and we have infinite
loop.

For example, lets suppose that we want to match following string:

    b a a a a a a

We could write a grammar like this:

    A = A 'a' / 'b'

But this grammar is left-recursive and the recursive-descent top-down parser
like Arpeggio will try to loop indefinitely trying to match `A` over and over
again in the same spot of the input string.

Although, there are techniques to handle left-recursion in top-down parsers
automatically, Arpeggio does not implements them and a classic approach of
[removing left
recursion](https://en.wikipedia.org/wiki/Left_recursion#Removing_left_recursion)
must be used.

To remove left recursion from the above grammar we do the following:

    A = 'b' 'a'*

Or, get all non-left recursive choices and put them first (`b` in this case) and
than add the zero-or-more repetition of the recursive part without the left
recursive non-terminal (`a` from `A 'a'` in this case).


Another example:

    add = mult / add '+' mult / add '-' mult 

becomes:

    add = mult (('+' mult) / ('-' mult))*

or:

    add = mult (('+' / '-') mult)*


In general:

    A = A a1 / A a2 / ... / A an / b1 / b2 / ... / bm

where uppercase letters represents non-terminals whereas lowercase letters
represent terminals.

Removing left recursion yields:

    A = (b1 / b2 / ... / bm) (a1 / a2 / ... / an)*

!!! danger
    Be aware that the parse tree will not be the same.


## Unrecognized grammar element '...'

This might happen when non-unicode literals are used. Make sure that you use
unicode literals when defining grammars using Python notation.

You might want to include:

```python
from __future__ import unicode_literals
```

This will enable unicode literals in the python < 3.


## Visitor method is not called during semantic analysis

Semantic analysis operates on a parse tree nodes produced by grammar rules.
If you are using a `reduce_tree=True` option in the construction of the parser
all non-terminal nodes with only one child will be suppressed in the parse tree.
Thus, visitor methods for those nodes will not be called.

To resolve issue either disable tree reduction during parser construction (i.e.
`reduce_tree=False`) or do visitor job in some of the calling rules that produce
parse tree node with more than one child.

As a side note, there is implicit reduction of nodes whose grammar rule is a 
sequence with only one child.

```python
def mean():             return number
def number():           return _(r'\d*\.\d*|\d+')
```

Here a node `number` will be suppressed from the parser model and visitor
`visit_number` will not be called. You have to define `visit_mean` or a visitor
for some of the rules calling `mean`.

This implicit reduction can not be disabled at the moment. Please see [issue
24](https://github.com/textX/Arpeggio/issues/24).



