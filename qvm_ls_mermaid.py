#!/usr/bin/env python3
"""Generate a DOT graph of Qubes OS VM network/template relationships.

Usage:
    python3 qvm_ls_mermaid.py [options]

Render the output with Graphviz:
    dot -Tsvg qubes.dot -o qubes.svg
"""
from __future__ import annotations

import argparse
import dataclasses
import sys

import qubesadmin
import qubesadmin.exc

KLASS_SHAPES: dict[str, str] = {
    'AdminVM':      'octagon',
    'TemplateVM':   'component',
    'AppVM':        'ellipse',
    'StandaloneVM': 'box',
    'DispVM':       'diamond',
}
DEFAULT_SHAPE = 'ellipse'
DEFAULT_FILL_COLOR = '#cccccc'


@dataclasses.dataclass
class VMNode:
    name: str
    dot_id: str
    fill_color: str
    shape: str
    thick_border: bool


@dataclasses.dataclass
class Edge:
    src_id: str
    dst_id: str
    style: str  # 'network' | 'template'


def _get_property(vm, attr, default=None):
    """Safely read a VM property; return default on error."""
    try:
        return getattr(vm, attr)
    except (qubesadmin.exc.QubesPropertyAccessError, AttributeError):
        return default


def _label_color(vm) -> str:
    """Return '#rrggbb' from vm.label.color, or DEFAULT_FILL_COLOR on failure."""
    try:
        color = vm.label.color
        # color may be '0xrrggbb' or '#rrggbb'
        if color.startswith('0x'):
            return '#' + color[2:]
        if color.startswith('#'):
            return color
        return DEFAULT_FILL_COLOR
    except Exception:  # pylint: disable=broad-except
        return DEFAULT_FILL_COLOR


def _node_shape(vm) -> str:
    """Map vm.klass to DOT shape, defaulting to DEFAULT_SHAPE."""
    klass = _get_property(vm, 'klass', '')
    return KLASS_SHAPES.get(klass, DEFAULT_SHAPE)


def _dot_id(name: str) -> str:
    """Sanitize VM name to a valid DOT identifier."""
    return name.replace('-', '_').replace('.', '_')


def collect_graph_data(
    app: qubesadmin.app.QubesBase,
    show_templates: bool,
) -> tuple[list[VMNode], list[Edge]]:
    """Walk app.domains; build VMNode list and network/template Edge list."""
    nodes: list[VMNode] = []
    edges: list[Edge] = []

    for vm in app.domains:
        provides_network = bool(_get_property(vm, 'provides_network', False))
        node = VMNode(
            name=vm.name,
            dot_id=_dot_id(vm.name),
            fill_color=_label_color(vm),
            shape=_node_shape(vm),
            thick_border=provides_network,
        )
        nodes.append(node)

        # Network edge: vm -> netvm
        netvm = _get_property(vm, 'netvm', None)
        if netvm is not None:
            edges.append(Edge(
                src_id=_dot_id(vm.name),
                dst_id=_dot_id(netvm.name),
                style='network',
            ))

        # Template edge: vm -> template
        if show_templates:
            template = _get_property(vm, 'template', None)
            if template is not None:
                edges.append(Edge(
                    src_id=_dot_id(vm.name),
                    dst_id=_dot_id(template.name),
                    style='template',
                ))

    return nodes, edges


def filter_isolated(
    nodes: list[VMNode],
    edges: list[Edge],
) -> tuple[list[VMNode], list[Edge]]:
    """Remove nodes that appear in no edges."""
    connected: set[str] = set()
    for edge in edges:
        connected.add(edge.src_id)
        connected.add(edge.dst_id)
    nodes = [n for n in nodes if n.dot_id in connected]
    return nodes, edges


def _is_dark(color: str) -> bool:
    """Return True if the hex color is dark enough to warrant white text."""
    try:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        # Standard luminance formula
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 128
    except Exception:  # pylint: disable=broad-except
        return False


def write_dot(nodes: list[VMNode], edges: list[Edge], stream) -> None:
    """Write a DOT digraph to *stream*."""
    stream.write('digraph qubes_network {\n')
    stream.write('    rankdir=LR;\n')
    stream.write('    node [style=filled, fontname="sans-serif"];\n')

    for node in nodes:
        attrs = [
            f'label="{node.name}"',
            f'shape={node.shape}',
            f'fillcolor="{node.fill_color}"',
        ]
        if _is_dark(node.fill_color):
            attrs.append('fontcolor="white"')
        if node.thick_border:
            attrs.append('penwidth=3')
        stream.write(f'    {node.dot_id} [{", ".join(attrs)}];\n')

    for edge in edges:
        if edge.style == 'network':
            attr_str = 'style=bold'
        else:
            attr_str = 'style=dashed, color=gray'
        stream.write(f'    {edge.src_id} -> {edge.dst_id} [{attr_str}];\n')

    stream.write('}\n')


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Generate a DOT graph of Qubes OS VM relationships.',
    )
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='write DOT output to FILE instead of stdout',
    )
    parser.add_argument(
        '-T', '--templates',
        action='store_true',
        default=False,
        help='include template relationships as dashed edges',
    )
    parser.add_argument(
        '-n', '--no-isolated',
        action='store_true',
        default=False,
        dest='no_isolated',
        help='exclude VMs with no connections',
    )
    return parser


def main() -> int:
    app = qubesadmin.Qubes()
    app.cache_enabled = True
    args = get_parser().parse_args()
    nodes, edges = collect_graph_data(app, args.templates)
    if args.no_isolated:
        nodes, edges = filter_isolated(nodes, edges)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            write_dot(nodes, edges, f)
    else:
        write_dot(nodes, edges, sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
