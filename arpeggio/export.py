# -*- coding: utf-8 -*-
#######################################################################
# Name: export.py
# Purpose: Export support for arpeggio
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import io
from . import Terminal


class Exporter(object):
    """
    Base class for all Exporters.
    """

    def __init__(self):
        super(Exporter, self).__init__()

        # Export initialization
        self._render_set = set()        # Used in rendering to prevent
                                        # rendering
                                        # of the same node multiple times

        self._adapter_map = {}          # Used as a registry of adapters to
                                        # ensure that the same adapter is
                                        # returned for the same adaptee object

    def export(self, obj):
        """
        Export of an obj to a string.
        """
        self._outf = io.StringIO()
        self._export(obj)
        content = self._outf.getvalue()
        self._outf.close()
        return content

    def exportFile(self, obj, file_name):
        """
        Export of obj to a file.
        """
        self._outf = io.open(file_name, "w", encoding="utf-8")
        self._export(obj)
        self._outf.close()

    def _export(self, obj):
        self._outf.write(self._start())
        self._render_node(obj)
        self._outf.write(self._end())

    def _start(self):
        """
        Override this to specify the beginning of the graph representation.
        """
        return ""

    def _end(self):
        """
        Override this to specify the end of the graph representation.
        """
        return ""


class ExportAdapter(object):
    """
    Base adapter class for the export support.
    Adapter should be defined for every export and graph type.

    Attributes:
        adaptee: A node to adapt.
        export: An export object used as a context of the export.
    """
    def __init__(self, node, export):
        self.adaptee = node     # adaptee is adapted graph node
        self.export = export


# -------------------------------------------------------------------------
# Support for DOT language


class DOTExportAdapter(ExportAdapter):
    """
    Base adapter class for the DOT export support.
    """
    @property
    def id(self):
        """
        Graph node unique identification.
        """
        raise NotImplementedError()

    @property
    def desc(self):
        """
        Graph node textual description.
        """
        raise NotImplementedError()

    @property
    def neighbours(self):
        """
        A set of adjacent graph nodes.
        """
        raise NotImplementedError()


class PMDOTExportAdapter(DOTExportAdapter):
    """
    Adapter for ParsingExpression graph types (parser model).
    """
    @property
    def id(self):
        return id(self.adaptee)

    @property
    def desc(self):
        return self.adaptee.desc

    @property
    def neighbours(self):
        if not hasattr(self, "_neighbours"):
            self._neighbours= []

            # Registry of adapters used in this export
            adapter_map = self.export._adapter_map

            for c, n in enumerate(self.adaptee.nodes):
                if isinstance(n, PMDOTExportAdapter):
                    # if the neighbour node is already adapted use that adapter
                    self._neighbours.append((str(c + 1), n))
                elif id(n) in adapter_map:
                    # current node is adaptee -> there is registered adapter
                    self._neighbours.append((str(c + 1), adapter_map[id(n)]))
                else:
                    # Create new adapter
                    adapter = PMDOTExportAdapter(n, self.export)
                    self._neighbours.append((str(c + 1), adapter))
                    adapter_map[adapter.id] = adapter

        return self._neighbours


class PTDOTExportAdapter(PMDOTExportAdapter):
    """
    Adapter for ParseTreeNode graph types.
    """
    @property
    def neighbours(self):
        if isinstance(self.adaptee, Terminal):
            return []
        else:
            if not hasattr(self, "_neighbours"):
                self._neighbours = []
                for c, n in enumerate(self.adaptee):
                    adapter = PTDOTExportAdapter(n, self.export)
                    self._neighbours.append((str(c + 1), adapter))
            return self._neighbours


class DOTExporter(Exporter):
    """
    Export to DOT language (part of GraphViz, see http://www.graphviz.org/)
    """
    def _render_node(self, node):
        if not node in self._render_set:
            self._render_set.add(node)
            self._outf.write('\n%s [label="%s"];' %
                             (node.id, self._dot_label_esc(node.desc)))
            #TODO Comment handling
#            if hasattr(node, "comments") and root.comments:
#                retval += self.node(root.comments)
#                retval += '\n%s->%s [label="comment"]' % \
                            #(id(root), id(root.comments))
            for name, n in node.neighbours:
                self._outf.write('\n%s->%s [label="%s"]' %
                                 (node.id, n.id, name))
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


class PMDOTExporter(DOTExporter):
    """
    A convenience DOTExport extension that uses ParserExpressionDOTExportAdapter
    """
    def export(self, obj):
        return super(PMDOTExporter, self).\
            export(PMDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PMDOTExporter, self).\
            exportFile(PMDOTExportAdapter(obj, self), file_name)


class PTDOTExporter(DOTExporter):
    """
    A convenience DOTExport extension that uses PTDOTExportAdapter
    """
    def export(self, obj):
        return super(PTDOTExporter, self).\
            export(PTDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PTDOTExporter, self).\
            exportFile(PTDOTExportAdapter(obj, self), file_name)
