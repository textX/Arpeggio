#######################################################################
# Name: textx.py
# Purpose: Demonstration of textX meta-language.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from arpeggio.textx import get_parser

def main(debug=False):

    # Load textX description of the language
    with open('pyflies.tx', 'r') as f:
        language_def = f.read()

    # Create parser for the new lanuage
    parser = get_parser(language_def, debug=debug)

    # Parse pyflies example
    with open('experiment.pf') as f:
        pyflies_input = f.read()
    parse_tree = parser.parse(pyflies_input)

    # Construct model from the parse_tree
    model = parser.get_model()
    print(model)


if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

