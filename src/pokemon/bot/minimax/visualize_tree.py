from typing import Optional

from src.pokemon import logger
import graphviz

from src.pokemon.bot.minimax.min_max_node import MinMaxNode


def visualize_tree(root: MinMaxNode) -> graphviz.Digraph:
    dot = graphviz.Digraph('Game Plan', directory='src/data/graphs')
    _complete_tree(root, dot)
    return dot


def _complete_tree(root: MinMaxNode, dot: graphviz.Digraph, node_id: int = 0) -> int:

    root_id = node_id

    dot.node(f'n{node_id}', _node_to_desc(root), color='green' if root.is_min_node else 'red')
    for key, value in root.children.items():
        node_id += 1
        child_node_desc = _node_to_desc(value)
        dot.node(f'n{node_id}', child_node_desc, color='green' if value.is_min_node else 'red')
        dot.edge(f'n{root_id}', f'n{node_id}', label=key)
        node_id = _complete_tree(value, dot, node_id)

    return node_id + 1


def _node_to_desc(node: MinMaxNode) -> str:

    s = '<'
    s += f'{node.own_species}' if node.remaining_hp_team_1[node.own_species] > 0 else f'<u>{node.own_species}</u>'
    s += ' vs '
    s += f'{node.enemy_species}' if node.remaining_hp_team_2[node.enemy_species] > 0 else f'<u>{node.enemy_species}</u>'
    s += f'<BR/>'
    s += f'{str(node.remaining_hp_team_1)}'
    s += f'<BR/>'
    s += f'{str(node.remaining_hp_team_2)}'
    s += '>'

    return s
