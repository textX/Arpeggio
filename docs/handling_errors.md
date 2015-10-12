# Handling syntax errors in the input

If your grammar is correct but you get input string with syntax error parser
will raise `NoMatch` exception with the information where in the input stream
error has occurred and what the parser expect to see at that location.

By default, if `NoMatch` is not caught you will get detailed explanation of
the error on the console.  The exact location will be reported, the context
(part of the input where the error occurred) and the first rule that was tried
at that location.

Example:

```python
parser = ParserPython(calc)
# 'r' in the following expression can't be recognized by
# calc grammar
input_expr = "23+4/r-89"
parse_tree = parser.parse(input_expr)
```

As there is an error in the `input_expr` string (`r` is not expected) the 
following traceback will be printed:

    Traceback (most recent call last):
      ...
    arpeggio.NoMatch: Expected '+' at position (1, 6) => '23+4/*r-89'.

The place in the input stream is marked by `*` and the position in (row, col) is
given (`(1, 6)`).

If you wish to handle syntax errors gracefully you can catch `NoMatch` in your
code and inspect its attributes.

```python
try:
  parser = ParserPython(calc)
  input_expr = "23+4/r-89"
  parse_tree = parser.parse(input_expr)
except NoMatch as e:
  # Do something with e
```


`NoMatch` class has the following attributes:

- `rule` - A `ParsingExpression` rule that is the source of the exception.
- `position` - A position in the input stream where exception occurred.
- `parser` - A `Parser` instance used for parsing.
- `exp_str` -  What is expected? If not given it is deduced from the rule. Currently
  this is used by [textX](https://github.com/igordejanovic/textX) for nicer
  error reporting.

The `position` is given as the offset from the beginning of the input string.
To convert it to row and column use `pos_to_linecol` method of the parser.

```python
try:
  parser = ParserPython(calc)
  input_expr = "23+4/r-89"
  parse_tree = parser.parse(input_expr)
except NoMatch as e:
  line, col = e.parser.pos_to_linecol(e.position)
  ...
```

Arpeggio is a backtracking parser, which means that it will go back and try
another alternatives when the match does not succeeds but it will nevertheless
report the furthest place in the input where it failed.  Currently Arpeggio will
report the first rule it tried at that location. Future versions could keep the
list of all rules that was tried at reported location.




