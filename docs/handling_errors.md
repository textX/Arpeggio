# Handling syntax errors in the input

This section explains how to handle parsing errors.

---

If your grammar is correct but you get input string with syntax error parser
will raise `NoMatch` exception with the information where in the input stream
error has occurred and what the parser expect to see at that location.

By default, if `NoMatch` is not caught you will get detailed explanation of
the error at the console.  The exact location will be reported, the context
(part of the input where the error occurred) and all the rules that were tried
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
    arpeggio.NoMatch: Expected '+' or '-' or 'number' or 
      '(' at position (1, 6) => '23+4/*r-89'.

The place in the input stream is marked by `*` and the position in (line,
column) is given (`(1, 6)`).

If you wish to handle syntax errors gracefully you can catch `NoMatch` in your
code and inspect its attributes.

```python
try:
  parser = ParserPython(calc)
  input_expr = "23+4/r-89"
  parse_tree = parser.parse(input_expr)
except NoMatch as e:
  # Do something with e
  # Call e.eval_attrs() if you want to create a custom message
  # call str(e) for the default message
```


`NoMatch` class has the following attributes:

- `rules` - A list of `ParsingExpression` rules that are the sources of the
  exception.
- `position` - A position in the input stream where exception occurred.
- `parser` - A `Parser` instance used for parsing.

After `eval_attrs()` method is called on the exception (happens automatically if
`__str__` is called) these additional attributes are available:

- `message` - An error message.
- `context` - A context (part of the input) in which error occurred.
- `line`, `col` - A line and column in the input stream where exception
  occurred.

Arpeggio is a backtracking parser, which means that it will go back and try
another alternatives when the match does not succeeds. Nevertheless, it will 
report the furthest place in the input where it failed. Arpeggio will
report all `Match` rules that failed at that position.



