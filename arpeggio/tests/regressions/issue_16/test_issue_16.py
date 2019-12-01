# stdlib
from typing import Any, List

# proj
try:
    # imports for local pytest
    from ....arpeggio import ParseTreeNode  # type: ignore # pragma: no cover
    from ....parser_peg_clean import ParserPEG      # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import ParseTreeNode      # type: ignore # pragma: no cover
    from parser_peg_clean import ParserPEG          # type: ignore # pragma: no cover


parser_input = """\
<?php
class Enum {
    protected $self = array();
    public function __construct( $fun ) {
        $args = func_get_args();
        for( $i=0, $n=count($args); $i<$n; $i++ )
            $this->add($args[$i]);
    }

    public function __get(  $name = null ) {
        return $this->self[$name];
    }

    public function add(  $name = null,  $enum = null ) {
        if( isset($enum) )
            $this->self[$name] = $enum;
        else
            $this->self[$name] = end($this->self) + 1;
    }


"""

grammar = """

calc = test

test = visibility ws* function_keyword ws* word ws* arguments* ws*
function = visibility "function" word arguments block
block = "{" ws* r'[^}]*' ws* "}"
arguments = "(" ws* argument* ws* ")"

// $types = array("cappuccino")
// arguments end with optional comma
argument = ( byvalue / byreference ) ("=" value )* ","*
byreference = "&" byvalue
byvalue = variable

// value may be variable or array or string or any php type
value = variable

visibility = "public" / "protected" / "private"
function_keyword = "function"

variable = "$" literal r'[a-zA-Z0-9_]*'
word = r'[a-zA-Z0-9_]+'
literal = r'[a-zA-Z]+'

comment = r'("//.*")|("/\*.*\*/")'
symbol = r'[\W]+'

anyword = r'[\w]*' ws*
ws = r'[\s]+'


"""     # noqa


def argument(parser: ParserPEG, node: ParseTreeNode, children: List[Any]) -> Any:
    """
    Removes parenthesis if exists and returns what was contained inside.
    """
    print(children)

    if len(children) == 1:
        print(children[0])
        return children[0]

    sign = -1 if children[0] == '-' else 1

    return sign * children[-1]


# Rules are mapped to semantic actions
sem_actions = {"argument": argument}


def test_issue_16() -> None:
    """
    >>> test_issue_16()

    """

    parser = ParserPEG(grammar, "calc", skipws=False)

    input_expr = """public function __construct( )"""
    parse_tree = parser.parse(input_expr)

    # Do semantic analysis. Do not use default actions.
    asg = parser.getASG(sem_actions=sem_actions, defaults=False)
    assert asg
