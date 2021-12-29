from typing import Optional

from src.pokemon import logger
import graphviz

from src.pokemon.bot.minimax.min_max_node import MinMaxNode


def visualize_tree(root: MinMaxNode) -> graphviz.Digraph:
    dot = graphviz.Digraph('Game Plan')
    _complete_tree(root, dot)
    return dot


def _complete_tree(root: MinMaxNode, dot: graphviz.Digraph, node_id: int = 0) -> int:

    root_id = node_id

    dot.node(f'n{node_id}', _node_to_desc(root))
    for node in root.children:
        node_id += 1
        child_node_desc = _node_to_desc(node)
        dot.node(f'n{node_id}', child_node_desc)
        dot.edge(f'n{root_id}', f'n{node_id}')
        node_id = _complete_tree(node, dot, node_id)

    return node_id + 1


def _node_to_desc(node: MinMaxNode) -> str:
    s = f'{node.own_species}\n{node.enemy_species}\n'
    s += f'{str(node.remaining_hp_team_1)}\n'
    s += f'{str(node.remaining_hp_team_2)}'

    return s
