# -*- coding: utf-8 -*-
#######################################################################
# Name: test_examples
# Purpose: Test that examples run without errors.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
import pytest
import os, sys
import imp

def test_examples():

    examples_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
           '../../examples/')
    if not examples_dir in sys.path:
        sys.path.insert(0, examples_dir)

    examples = [f for f in os.listdir(examples_dir) if f != '__init__.py' 
            and f.endswith('.py')]
    for e in examples:
        (module_name, _) = os.path.splitext(e)
        (module_file, module_path, desc) = imp.find_module(module_name, [examples_dir])

        m = imp.load_module(module_name, module_file, module_path, desc)

        if hasattr(m, 'main'):
            m.main(debug=False)

