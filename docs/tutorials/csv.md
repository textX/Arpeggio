# Comma-Separated Values (CSV) parser tutorial

In this tutorial we will see how to make a parser for a simple data interchange
format - [CSV]() (Comma-Separated Values).
CSV is a textual format for tabular data interchange. It is described by
[RFC 4180](https://tools.ietf.org/html/rfc4180).


[Here](https://en.wikipedia.org/wiki/Comma-separated_values) is an example of
CSV file:

```csv
Year,Make,Model,Length
1997,Ford,E350,2.34
2000,Mercury,Cougar,2.38
```

Although, there is [csv module](https://docs.python.org/3/library/csv.html) in
the standard Python library this example has been made as the CSV is ubiquitous
and easy to understand so it it a good starter for learning Arpeggio.

## The grammar

Let's define CSV grammar.

- CSV file consists of one or more records separated by a newline.

        def csvfile():    return OneOrMore([record, '\n']), EOF

- Each record consists of fields separated with commas.

        def record():     return field, ZeroOrMore(",", field) 

- Each field may be quoted or not.

        def field():      return [quoted_field, field_content]

- Field content is everything until newline or comma.

        def field_content():            return _(r'([^,\n])+')

      We use regular expression to match everything that is not comma or
      newline.

- Quoted field starts and ends with double quotes.

        def quoted_field():             return '"', field_content_quoted, '"'

- Quoted field content is defined as 

        def field_content_quoted():     return _(r'(("")|([^"]))+')

      Quoted field content is defined with regular expression that will match
      everything until the closing double-quote. Double quote inside data must
      be escaped by doubling it (`""`).


The whole grammar is

    def record():                   return field, ZeroOrMore(",", field)
    def field():                    return [quoted_field, field_content]
    def quoted_field():             return '"', field_content_quoted, '"'
    def field_content():            return _(r'([^,\n])+')
    def field_content_quoted():     return _(r'(("")|([^"]))+')
    def csvfile():                  return OneOrMore([record, '\n']), EOF


## The parser

Let's instantiate parser. In order to catch newlines in `csvfile` rule we must
disable newlines as whitespace so that Arpeggio does not skip over them. Thus,
we will be able to handle them explicitly as we do in csvfile rule. To do so we
will use `ws` parameter in parser construction to redefine what is considered as
whitespace.  You can find more information
[here](../configuration.md#white-space-handling).

    parser = ParserPython(csvfile, ws='\t ')

So, whitespace will be a tab char or space. Newline will be treated as regular
character.  We give grammar root rule to the `ParserPython`. In this example it
is `csvfile` function.

`parser` now refers to the parser object capable of parsing CSV inputs.


## Parsing

Let's parse some CSV example string:

```python
test_data = '''
Unquoted test, "Quoted test", 23234, One Two Three, "343456.45"

Unquoted test 2, "Quoted test with ""inner"" quotes", 23234, One Two Three, "343456.45"
Unquoted test 3, "Quoted test 3", 23234, One Two Three, "343456.45"
'''

parse_tree = parser.parse(test_data)

```

`parse_tree` is a reference to [parse tree](../parse_trees.md) of the `test_data`
example string.

This parse tree is [visualized](../debugging.md#grammar-visualization) below:


![CSV parse tree](img/csvfile_parse_tree.dot.png)


## Defining grammar using PEG notation

Let's now define the same grammar but using [textual PEG
notation](../grammars.md#grammars-written-in-peg-notations).

We shall repeat the process above but we shall encode rules in PEG.
We shall use clean PEG variant (`arpeggio.cleanpeg` module)

- CSV file consists of one or more records separated by a newline.

        csvfile = (record / '\n')+ EOF

- Each record consists of fields separated with commas.

        record = field ("," field)*

- Each field may be quoted or not.

        field = quoted_field / field_content

- Field content is everything until newline or comma.

        field_content = r'([^,\n])+' 

      We use regular expression to match everything that is not comma or
      newline.

- Quoted field starts and ends with double quotes.

        quoted_field = '"' field_content_quoted '"'

- Quoted field content is defined as 

        field_content_quoted = r'(("")|([^"]))+'

      Quoted field content is defined with regular expression that will match
      everything until the closing double-quote. Double quote inside data must
      be escaped by doubling it (`""`).


The whole grammar is:

      csvfile = (record / r'\n')+ EOF
      record = field ("," field)*
      field = quoted_field / field_content
      field_content = r'([^,\n])+'
      quoted_field = '"' field_content_quoted '"'
      field_content_quoted = r'(("")|([^"]))+'

If we put the parser in debug mode and generate parse tree image we can 
verify that we are getting the same parse tree regardless of the grammar
specification approach we use.

## Extract data

Our aim is to extract data from the `csv` file.

First lets define our target data structure we want to get.

Since `csv` consists of list of records where each record consists of fields
we shall construct python list of lists:

      [
        [field1, field2, field3, ...],  # First row
        [field1, field2, field3,...],   # Second row
        [...],  # ...
        ...
      ]

To construct this list of list we may process parse tree by navigating its
nodes and building the required target data structure.
But, it is easier to use Arpeggio's support for [semantic analysis - Visitor
Pattern](../semantics.md).

Let's make a Visitor for CSV that will build our list of lists.

```python
class CSVVisitor(PTNodeVisitor):
    def visit_record(self, node, children):
        # record is a list of fields. The children nodes are fields so just
        # transform it to python list.
        return list(children)

    def visit_csvfile(self, node, children):
        # We are not interested in empty lines so we will filter them.
        return [x for x in children if x!='\n']
```

and apply this visitor to the parse tree:

```python
csv_content = visit_parse_tree(parse_tree, CSVVisitor())
```

Now if we print `csv_content` we can see that it is exactly what we wanted:

```python
[[u'Unquoted test', u'Quoted test', u'23234', u'One Two Three', u'343456.45'], [u'Unquoted test 2', u'Quoted test with ""inner"" quotes', u'23234', u'One Two Three', u'34312.7'], [u'Unquoted test 3', u'Quoted test 3', u'23234', u'One Two Three', u'343486.12']]
```

But, there is more we can do. If we look at our data we can see that some fields
are of numeric type but they end up as strings in our target structure. Let's
convert them to Python floats or ints.  To do this conversion we will introduce
`visit_field` method in our `CSVVisitor` class.

```python
class CSVVisitor(PTNodeVisitor):
  ...
  def visit_field(self, node, children):
      value = children[0]
      try:
          return float(value)
      except:
          pass
      try:
          return int(value)
      except:
          return value
  ...
```

If we print `csv_content` now we can see that numeric values are not strings
anymore but a proper Python types.

```python
[[u'Unquoted test', u'Quoted test', 23234.0, u'One Two Three', 343456.45], [u'Unquoted test 2', u'Quoted test with ""inner"" quotes', 23234.0, u'One Two Three', 34312.7], [u'Unquoted test 3', u'Quoted test 3', 23234.0, u'One Two Three', 343486.12]]
```



