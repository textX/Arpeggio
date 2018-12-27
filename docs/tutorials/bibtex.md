# BibTeX tutorial

A tutorial for parsing well known format for bibliographic references.

---

The word [BibTeX](http://www.BibTeX.org/) stands for a tool and a file format
which are used to describe and process lists of references, mostly in
conjunction with LaTeX documents.

An example of BibTeX entry is given below.

```BibTeX
@article{DejanovicADomain-SpecificLanguageforDefiningStaticStructureofDatabaseApplications2010,
    author = "Igor Dejanovi\'{c} and Gordana Milosavljevi\'{c} and Branko Peri\v{s}i\'{c} and Maja Tumbas",
    title = "A {D}omain-Specific Language for Defining Static Structure of Database Applications",
    journal = "Computer Science and Information Systems",
    year = "2010",
    volume = "7",
    pages = "409--440",
    number = "3",
    month = "June",
    issn = "1820-0214",
    doi = "10.2298/CSIS090203002D",
    url = "http://www.comsis.org/ComSIS/Vol7No3/RegularPapers/paper2.htm",
    type = "M23"
}
```

Each BibTeX entry starts with `@` and a keyword denoting entry type (`article`)
in this example. After the entry type is the body of the reference inside curly
braces. The body of the reference consists of elements separated by a comma.
The first element is the key of the entry. It should be unique.
The rest of the entries are fields in the format:

    <field_name> = <field_value>

# The grammar

Let's start with the grammar.
Create file `bibtex.py`, and import `arpeggio`.

```python
from arpeggio import *
from arpeggio import RegExMatch as _
```

Then create grammar rules:

- BibTeX file consists of zero or more BibTeX entries.
```python
def bibfile():    return ZeroOrMore(bibentry), EOF
```
- Now we define the structure of BibTeX entry.
```python
def bibentry():  return bibtype, "{", bibkey, ",", field, ZeroOrMore(",", field), "}"
```
- Each field is given as field name, equals char (`=`), and the field value.
```python
def field():     return fieldname, "=", fieldvalue
```
- Field value can be specified inside braces or quotes.
```python
def fieldvalue():               return [fieldvalue_braces, fieldvalue_quotes]
def fieldvalue_braces():        return "{", fieldvalue_braced_content, "}"
def fieldvalue_quotes():        return '"', fieldvalue_quoted_content, '"'
```
- Now, let's define field name, BibTeX type and the key. We use regular
  expression match for this (`RegExMatch` class).
```python
def fieldname():                return _(r'[-\w]+')
def bibtype():                  return _(r'@\w+')
def bibkey():                   return _(r'[^\s,]+')
```
  Field name is defined as hyphen or alphanumeric one or more times.
  BibTeX entry type is `@` char after which must be one or more alphanumeric.
  BibTeX key is everything until the first space or comma.

- Field value can be quoted and braced. Let's match the content.
```python
def fieldvalue_quoted_content():    return _(r'((\\")|[^"])*')
def fieldvalue_braced_content():    return Combine(ZeroOrMore(Optional(And("{"), fieldvalue_inner),\
                                                  fieldvalue_part))
def fieldvalue_part():          return _(r'((\\")|[^{}])+')
def fieldvalue_inner():         return "{", fieldvalue_braced_content, "}"
```
!!! note "Combine decorator"
    We use `Combine` decorator to specify braced content. This decorator
    produces a [Terminal](../parse_trees.md#terminal-nodes) node in [the parse
    tree](../parse_trees.md).
    

# The parser

To instantiate the parser we are using `ParserPython` Arpeggio's class.

```python
parser = ParserPython(bibfile)
```

Now, we have our parser. Let's parse some input:

- First load some BibTeX data from a file.
```python
file_name = os.path.join(os.path.dirname(__file__), 'bibtex_example.bib')
with codecs.open(file_name, "r", encoding="utf-8") as bibtexfile:
    bibtexfile_content = bibtexfile.read()
```
We are using `codecs` module to load the file using `utf-8` encoding.
`bibtexfile_content` is now a string with the content of the file.

- Parse the input string
```pyhton
parse_tree = parser.parse(bibtexfile_content)
```

The parse tree is produced. 


# Extracting data from the parse tree

Let's suppose that we want our BibTeX file to be transformed to a list of
Python dictionaries where each field is keyed by its name and the value is 
the field value cleaned up from the BibTeX cruft.

Like this:

```python
{   'author': 'Igor Dejanović and Gordana Milosavljević and Branko Perišić and Maja Tumbas',
    'bibkey': 'DejanovicADomain-SpecificLanguageforDefiningStaticStructureofDatabaseApplications2010',
    'bibtype': '@article',
    'doi': '10.2298/CSIS090203002D',
    'issn': '1820-0214',
    'journal': 'Computer Science and Information Systems',
    'month': 'June',
    'number': '3',
    'pages': '409--440',
    'title': 'A Domain-Specific Language for Defining Static Structure of Database Applications',
    'type': 'M23',
    'url': 'http://www.comsis.org/ComSIS/Vol7No3/RegularPapers/paper2.htm',
    'volume': '7',
    'year': '2010'}
```

The key is stored under a dict key `bibkey` while the entry type is stored 
under the dict key `bibtype`.


After calling the `parse` method on the parser our textual data will be parsed
and stored in [the parse tree](../parse_trees.md). We could navigate the tree 
to extract the data and build the python list of dictionaries but a lot easier
is to use [Arpeggio's visitor support](../semantics.md).

In this case we shall create `BibTeXVisitor` class with `visit_*` methods for
each grammar rule whose parse tree node we want to process.

```python
class BibTeXVisitor(PTNodeVisitor):

    def visit_bibfile(self, node, children):
        """
        Just returns list of child nodes (bibentries).
        """
        # Return only dict nodes
        return [x for x in children if type(x) is dict]

    def visit_bibentry(self, node, children):
        """
        Constructs a map where key is bibentry field name.
        Key is returned under 'bibkey' key. Type is returned under 'bibtype'.
        """
        bib_entry_map = {
            'bibtype': children[0],
            'bibkey': children[1]
        }
        for field in children[2:]:
            bib_entry_map[field[0]] = field[1]
        return bib_entry_map

    def visit_field(self, node, children):
        """
        Constructs a tuple (fieldname, fieldvalue).
        """
        field = (children[0], children[1])
        return field
```

Now, apply the visitor to the parse tree.

```python
ast = visit_parse_tree(parse_tree, BibTeXVisitor())
```

`ast` is now a Python list of dictionaries in the desired format from above.

A full source code for this example can be found in [the source
code repository](https://github.com/textX/Arpeggio/tree/master/examples/bibtex).  

!!! note
    Example in the repository is actually a fully working parser with the
    support for BibTeX comments and comment entries. This is out of scope
    for this tutorial. You can find the details in the source code.
