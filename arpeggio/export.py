# -*- coding: utf-8 -*-
#######################################################################
# Name: export.py
# Purpose: Export support for arpeggio
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import StringIO
from arpeggio import Terminal

class Export(object):
    '''
    Base class for all Exporters.
    '''
                      
    def __init__(self):
        super(Export, self).__init__()
        
        # Export initialization
        self._render_set = set()        # Used in rendering to prevent rendering 
                                        # of the same node multiple times
                                        
        self._adapter_map = {}          # Used as a registry of adapters to ensure 
                                        # ensure that the same adapter is
                                        # returned for the same adaptee object

                                        
    def export(self, obj):
        '''Export of obj to a string.'''
        self._outf = StringIO()
        self._export(obj)
        return self._outf.getvalue()
    
    def exportFile(self, obj, file_name):
        '''Export of obj to a file.'''
        self._outf = open(file_name, "w")
        self._export(obj)
        self._outf.close()
        
    def _export(self, obj):
        self._outf.write(self._start())
        self._render_node(obj)
        self._outf.write(self._end())
            
    def _start(self):
        '''
        Overide this to specify the begining of the graph representation.
        '''
        return ""
    
    def _end(self):
        '''
        Overide this to specify the end of the graph representation.
        '''
        return ""

class ExportAdapter(object):
    '''
    Base adapter class for the export support.
    Adapter should be defined for every graph type.
    '''
    def __init__(self, node, export):
        '''
        @param node - node to adapt
        @param export - export object used as a context of the export.
        '''
        self.adaptee = node     # adaptee is adapted graph node
        self.export = export
        
        
# -------------------------------------------------------------------------
# Support for DOT language

class DOTExportAdapter(ExportAdapter):
    '''
    Base adapter class for the DOT export support.
    '''    
    @property
    def id(self):
        '''Graph node unique identification.'''
        raise NotImplementedError()
    
    @property
    def desc(self):
        '''Graph node textual description.'''
        raise NotImplementedError()
    
    @property
    def children(self):
        '''Children of the graph node.'''
        raise NotImplementedError()


class PMDOTExportAdapter(DOTExportAdapter):
    '''
    Adapter for ParsingExpression graph types (parser model).
    '''    
    @property
    def id(self):
        return id(self.adaptee)
    
    @property
    def desc(self):
        return self.adaptee.desc
    
    @property
    def children(self):
        if not hasattr(self, "_children"):
            self._children = []
            adapter_map = self.export._adapter_map    # Registry of adapters used in this export
            for c,n in enumerate(self.adaptee.nodes):
                if isinstance(n, PMDOTExportAdapter): # if child node is already adapted use that adapter
                    self._children.append((str(c+1), n))
                elif adapter_map.has_key(id(n)): # current node is adaptee -> there is registered adapter
                    self._children.append((str(c+1), adapter_map[id(n)]))
                else:
                    adapter = PMDOTExportAdapter(n, self.export)
                    self._children.append((str(c+1), adapter))
                    adapter_map[adapter.id] = adapter
        return self._children
    
class PTDOTExportAdapter(PMDOTExportAdapter):
    '''
    Adapter for ParseTreeNode graph types.
    '''    
    @property
    def children(self):
        if isinstance(self.adaptee, Terminal):
            return []
        else:
            if not hasattr(self, "_children"):
                self._children = []
                for c,n in enumerate(self.adaptee.nodes):
                    adapter = PTDOTExportAdapter(n, self.export)
                    self._children.append((str(c+1), adapter))
            return self._children

class DOTExport(Export):
    '''
    Export to DOT language (part of GraphViz, see http://www.graphviz.org/)
    '''
    def _render_node(self, node):
        if not node in self._render_set:
            self._render_set.add(node)
            self._outf.write('\n%s [label="%s"];' % (node.id, self._dot_label_esc(node.desc)))
            #TODO Comment handling
#            if hasattr(node, "comments") and root.comments:
#                retval += self.node(root.comments)
#                retval += '\n%s->%s [label="comment"]' % (id(root), id(root.comments))
            for name, n in node.children:
                self._outf.write('\n%s->%s [label="%s"]' % (node.id, n.id, name))
                self._outf.write('\n')
                self._render_node(n)    
    
    def _start(self):
        return "digraph arpeggio_graph {"
        
    def _end(self):
        return "\n}"
    
    def _dot_label_esc(self, to_esc):
        to_esc = to_esc.replace("\\", "\\\\")
        to_esc = to_esc.replace('\"', '\\"')
        to_esc = to_esc.replace('\n', '\\n')
        return to_esc


class PMDOTExport(DOTExport):
    '''
    Convenience DOTExport extension that uses ParserExpressionDOTExportAdapter
    '''    
    def export(self, obj):
        return super(PMDOTExport, self).\
            export(PMDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PMDOTExport, self).\
            exportFile(PMDOTExportAdapter(obj, self), file_name)


class PTDOTExport(DOTExport):
    '''
    Convenience DOTExport extension that uses PTDOTExportAdapter
    '''    
    def export(self, obj):
        return super(PTDOTExport, self).\
            export(PTDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PTDOTExport, self).\
            exportFile(PTDOTExportAdapter(obj, self), file_name)
    