#######################################################################
# Name: test_examples
# Purpose: Test that examples run without errors.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
import os
import sys
import glob
import importlib
import importlib.util


def test_examples():

    add_arpeggio_folder_to_syspath()

    examples_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   '..', '..', 'examples')
    if not os.path.exists(examples_folder):
        print('Warning: Examples not found. Skipping tests.')
        return

    examples_pat = os.path.join(examples_folder, '*', '*.py')

    # Filter out __init__.py
    examples = [f for f in glob.glob(examples_pat) if f != '__init__.py']
    for e in examples:
        example_dir = os.path.dirname(e)
        sys.path.insert(0, example_dir)
        (module_name, _) = os.path.splitext(os.path.basename(e))
        mod_spec = importlib.util.spec_from_file_location(module_name, e)
        mod = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(mod)

        if hasattr(mod, 'main'):
            mod.main(debug=False)


def add_arpeggio_folder_to_syspath() -> None:
    """ add the path to arpeggio in the syspath, if it is not installed for local development testing
        so arpeggio.py will be importable
    """
    arpeggio_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   '..', '..', '..', 'Arpeggio')
    if arpeggio_folder not in sys.path:
        sys.path.append(arpeggio_folder)
