#######################################################################
# Name: export.py
# Purpose: Export support for arpeggio
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from arpeggio import Terminal

from arpeggio import Terminal


class Exporter:
    """
    Base class for all Exporters.
    """

    def __init__(self) -> None:
        super().__init__()

        # Export initialization. Used in rendering to prevent rendering of the
        # same node multiple times
        self._render_set: set[int] = set()

        # Used as a registry of adapters to ensure that the same adapter is
        # returned for the same adaptee object
        self._adapter_map: dict[int, DOTExportAdapter] = {}

        # Output file-like object (StringIO or real file)
        self._outf: Any = None

    def export(self, obj: Any) -> str:
        """
        Export of an obj to a string.
        """
        self._outf = io.StringIO()
        self._export(obj)
        content = self._outf.getvalue()
        self._outf.close()
        return content  # type: ignore[no-any-return]

    def exportFile(self, obj: Any, file_name: str) -> None:
        """
        Export of obj to a file.
        """
        with open(file_name, "w", encoding="utf-8") as f:
            self._outf = f
            self._export(obj)

    def _export(self, obj: Any) -> None:
        self._outf.write(self._start())
        self._render_node(obj)
        self._outf.write(self._end())

    def _start(self) -> str:
        """
        Override this to specify the beginning of the graph representation.
        """
        return ""

    def _end(self) -> str:
        """
        Override this to specify the end of the graph representation.
        """
        return ""

    def _render_node(self, node: Any) -> None:
        raise NotImplementedError


class ExportAdapter:
    """
    Base adapter class for the export support.
    Adapter should be defined for every export and graph type.

    Attributes:
        adaptee: A node to adapt.
        export: An export object used as a context of the export.
    """

    def __init__(self, node: Any, export: Exporter) -> None:
        self.adaptee = node  # adaptee is adapted graph node
        self.export = export


# -------------------------------------------------------------------------
# Support for DOT language


class DOTExportAdapter(ExportAdapter):
    """
    Base adapter class for the DOT export support.
    """

    @property
    def id(self) -> int:
        """
        Graph node unique identification.
        """
        raise NotImplementedError()

    @property
    def desc(self) -> str:
        """
        Graph node textual description.
        """
        raise NotImplementedError()

    @property
    def neighbours(self) -> list[tuple[str, DOTExportAdapter]]:
        """
        A set of adjacent graph nodes.
        """
        raise NotImplementedError()


class PMDOTExportAdapter(DOTExportAdapter):
    """
    Adapter for ParsingExpression graph types (parser model).
    """

    @property
    def id(self) -> int:
        return id(self.adaptee)

    @property
    def desc(self) -> str:
        return self.adaptee.desc  # type: ignore[no-any-return]

    @property
    def neighbours(self) -> list[tuple[str, DOTExportAdapter]]:
        if not hasattr(self, "_neighbours"):
            self._neighbours: list[tuple[str, DOTExportAdapter]] = []

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
    def neighbours(self) -> list[tuple[str, DOTExportAdapter]]:
        if isinstance(self.adaptee, Terminal):
            return []
        else:
            if not hasattr(self, "_neighbours"):
                self._neighbours: list[tuple[str, DOTExportAdapter]] = []
                for c, n in enumerate(self.adaptee):  # type: ignore[arg-type]
                    adapter = PTDOTExportAdapter(n, self.export)
                    self._neighbours.append((str(c + 1), adapter))
            return self._neighbours


class DOTExporter(Exporter):
    """
    Export to DOT language (part of GraphViz, see http://www.graphviz.org/)
    """

    def _render_node(self, node: DOTExportAdapter) -> None:
        if node.id not in self._render_set:
            self._render_set.add(node.id)
            self._outf.write(f'\n{node.id} [label="{self._dot_label_esc(node.desc)}"];')
            # TODO Comment handling
            for name, n in node.neighbours:
                self._outf.write(f'\n{node.id}->{n.id} [label="{name}"]')
                self._outf.write("\n")
                self._render_node(n)

    def _start(self) -> str:
        return "digraph arpeggio_graph {"

    def _end(self) -> str:
        return "\n}"

    def _dot_label_esc(self, to_esc: str) -> str:
        to_esc = to_esc.replace("\\", "\\\\")
        to_esc = to_esc.replace('"', '\\"')
        to_esc = to_esc.replace("\n", "\\n")
        return to_esc


class PMDOTExporter(DOTExporter):
    """
    A convenience DOTExport extension that uses ParserExpressionDOTExportAdapter
    """

    def export(self, obj: Any) -> str:
        return super().export(PMDOTExportAdapter(obj, self))

    def exportFile(self, obj: Any, file_name: str) -> None:
        return super().exportFile(PMDOTExportAdapter(obj, self), file_name)


class PTDOTExporter(DOTExporter):
    """
    A convenience DOTExport extension that uses PTDOTExportAdapter
    """

    def export(self, obj: Any) -> str:
        return super().export(PTDOTExportAdapter(obj, self))

    def exportFile(self, obj: Any, file_name: str) -> None:
        return super().exportFile(PTDOTExportAdapter(obj, self), file_name)
