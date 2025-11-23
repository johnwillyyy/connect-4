import time
import random
from graphviz import Digraph 

class AIAgent:
    
    def __init__(self, computer_player, human_player, depth):
        self.computer_player = computer_player
        self.human_player = human_player
        self.depth = depth
        self.graph_source = "" 
        self._node_counter = 0
        self._best_path_edges = [] 

    def get_best_move(self, board, algorithm):
        """Main entry point for the AI to select a move and generate the graph."""
        self._node_counter = 0
        self._best_path_edges = []
        
        # Define Global Graph Attributes for Elegance (Dark theme base)
        dot = Digraph(comment='Connect Four Search Tree', 
                      graph_attr={'rankdir': 'TB', 'bgcolor': '#282a36', 'fontname': 'Helvetica', 'nodesep': '0.5', 'ranksep': '0.7'},
                      node_attr={'fontname': 'Helvetica', 'fontsize': '10', 'color': '#f8f8f2', 'fontcolor': '#f8f8f2'}, # Default white text
                      edge_attr={'fontname': 'Helvetica', 'fontsize': '9', 'color': '#f8f8f2'})
        
        if not board.get_valid_moves():
            self.graph_source = ""
            return -1
        
        best_col = -1
        root_id = self._get_next_node_id()
        value = 0 

        # Call the corresponding graph-building search function
        if algorithm == "minimax_ab":
            value, best_col, best_path_id = self._minimax_graph(board, self.depth, -float('inf'), float('inf'), True, 'AB', dot, root_id, None, None)
        elif algorithm == "minimax":
            value, best_col, best_path_id = self._minimax_graph(board, self.depth, -float('inf'), float('inf'), True, 'STANDARD', dot, root_id, None, None)
        elif algorithm == "expected_minimax":
            value, best_col, best_path_id = self._expected_minimax_graph(board, self.depth, True, dot, root_id, None, None)
        else:
            valid_moves = board.get_valid_moves()
            return random.choice(valid_moves) if valid_moves else -1

        # --- Highlighting the Best Path ---
        # NOTE: A full recursive path highlight is complex in python-graphviz. 
        # The current implementation highlights the optimal edge leading out of the root.
        if best_path_id is not None:
             self._highlight_path(dot, root_id, best_path_id, best_col)

        # Highlight the final chosen move and score on the root node
        dot.node(root_id, label=f"ROOT (D={self.depth})\n{algorithm.title()}\nFinal Score: {value:.2f}\nChosen Move: Col {best_col}", 
                 style='filled', fillcolor='#50fa7b', shape='box', fontcolor='#282a36') 

        # Store the final graph source
        self.graph_source = dot.source
        
        # Ensure best_col is an integer
        if best_col is None or not isinstance(best_col, int):
            valid_moves = board.get_valid_moves()
            best_col = random.choice(valid_moves) if valid_moves else -1
        
        return best_col

    def get_graphviz_source(self):
        """Returns the Graphviz DOT source string for the GUI to render."""
        return self.graph_source

    def _get_next_node_id(self):
        """Generates a unique ID for each node."""
        self._node_counter += 1
        return f"N{self._node_counter}"

    def _highlight_path(self, dot, parent_id, child_id, move_col):
        """Helper to mark the optimal edge from the root."""
        # This is a simplified direct edge highlight from the root.
        dot.edge(parent_id, child_id, label=f"Col {move_col}", color='#50fa7b', penwidth='3', fontcolor='#50fa7b')
        return

    # --- Standard Game Logic (Unchanged) ---
    def _simulate_move(self, board, col, player):
        for r in range(board.rows):
            if board.board[col][r] == 0:
                board.board[col][r] = player
                return r, col
        return -1, -1 

    def _undo_move(self, board, row, col):
        if row != -1:
            board.board[col][row] = 0

    def _check_terminal(self, board):
        if board.is_board_full():
            return 0 
        return None 
    
    # --- Minimax Search for Graphviz ---
    def _minimax_graph(self, board, depth, alpha, beta, maximizing_player, mode, dot, parent_id, edge_label, parent_is_chance):
        
        terminal_state = self._check_terminal(board)
        is_terminal = terminal_state is not None
        is_heuristic = depth == 0

        player_label = "MAX" if maximizing_player else "MIN"
        current_node_id = parent_id

        # --- Node Styling ---
        if is_terminal:
            score = board.count_connected_fours(self.computer_player) - board.count_connected_fours(self.human_player)
            label = f"TERMINAL (Draw)\nScore Diff: {score}"
            fillcolor = '#bd93f9'
            fontcolor = '#282a36' # Change font to black for contrast
            shape = 'box'
        elif is_heuristic:
            score = board.evaluate_heuristic(self.computer_player)
            label = f"Value: {score:.2f}" 
            fillcolor = '#f1fa8c'
            fontcolor = '#282a36' # Change font to black for contrast
            shape = 'box'
        else:
            score = None
            # Dark colors for internal nodes
            fillcolor = '#ff5555' if maximizing_player else '#ff79c6' # MAX (Red-Pink) vs MIN (Pink)
            fontcolor = '#f8f8f2' # Keep white font for contrast
            shape = 'ellipse'
            
            # Initial label for internal nodes (includes Alpha/Beta if AB mode)
            if mode == 'AB':
                label = f"{player_label} D={depth}\nA: {alpha:.2f}\nB: {beta:.2f}"
            else:
                label = f"{player_label} D={depth}" # Base Minimax

        # 2. Add current node to graph
        dot.node(current_node_id, label=label, style='filled', fillcolor=fillcolor, shape=shape, margin='0.1', fontcolor=fontcolor)
        
        # 3. Connect to parent
        if edge_label is not None:
            dot.edge(edge_label[0], current_node_id, label=edge_label[1], color='#f8f8f2', penwidth='1') 
            
        if is_terminal or is_heuristic:
            # Return score and the ID of this node (critical for path tracing)
            return score, None, current_node_id

        # 4. Search Logic
        valid_moves = board.get_valid_moves()
        best_col = valid_moves[0] if valid_moves else None
        
        value = -float('inf') if maximizing_player else float('inf')
        best_child_id = None
        
        for col in valid_moves:
            child_id = self._get_next_node_id()
            row, played_col = self._simulate_move(board, col, self.computer_player if maximizing_player else self.human_player)
            
            # Recursive call. Pass current alpha/beta bounds.
            score, _, child_path_id = self._minimax_graph(board, depth - 1, alpha, beta, not maximizing_player, mode, dot, child_id, (current_node_id, f"Col {col}"), None)
            
            self._undo_move(board, row, played_col)
            
            # Update value and best_col
            if maximizing_player:
                if score > value:
                    value = score
                    best_col = col
                    best_child_id = child_path_id
                alpha = max(alpha, value)
            else: # Minimizing Player
                if score < value:
                    value = score
                    best_col = col
                    best_child_id = child_path_id
                beta = min(beta, value)

            # Update node label with current best value and bounds
            if not is_terminal and not is_heuristic:
                if mode == 'AB':
                    # MAX: Value + Alpha
                    if maximizing_player:
                        current_label = f"{player_label} D={depth}\nValue: {value:.2f}\nA: {alpha:.2f}\nB: {beta:.2f}"
                    # MIN: Value + Beta
                    else:
                        current_label = f"{player_label} D={depth}\nValue: {value:.2f}\nA: {alpha:.2f}\nB: {beta:.2f}"
                else:
                    current_label = f"{player_label} D={depth}\nValue: {value:.2f}"
                dot.node(current_node_id, label=current_label, style='filled', fillcolor=fillcolor, shape=shape, fontcolor=fontcolor)

            # Pruning check
            if mode == 'AB' and (alpha >= beta):
                # Highlight the pruned edge
                dot.edge(current_node_id, child_id, color='#ff5555', style='dashed', label='PRUNED', penwidth='2')
                break 
        
        # Return the final evaluation, the column that led to it, and the ID of the optimal child node
        return value, best_col, best_child_id
    
    # --- Expected Minimax Search for Graphviz ---
    def _expected_minimax_graph(self, board, depth, maximizing_player, dot, parent_id, edge_label, parent_is_chance):
        
        terminal_state = self._check_terminal(board)
        is_terminal = terminal_state is not None
        is_heuristic = depth == 0
        current_node_id = parent_id

        # --- Node Styling ---
        if is_terminal:
            score = board.count_connected_fours(self.computer_player) - board.count_connected_fours(self.human_player)
            label = f"TERMINAL (Draw)\nScore Diff: {score}"
            fillcolor = '#bd93f9'
            fontcolor = '#282a36' # Change font to black
            shape = 'box'
        elif is_heuristic:
            score = board.evaluate_heuristic(self.computer_player)
            label = f"Value: {score:.2f}" 
            fillcolor = '#f1fa8c'
            fontcolor = '#282a36' # Change font to black
            shape = 'box'
        elif maximizing_player:
            label = f"MAX\nD={depth}"
            fillcolor = '#50fa7b'
            fontcolor = '#282a36' # Change font to black
            shape = 'ellipse'
        else:
            label = f"MIN\nD={depth}"
            fillcolor = '#ff5555'
            fontcolor = '#f8f8f2' # Keep white font
            shape = 'ellipse'

        dot.node(current_node_id, label=label, style='filled', fillcolor=fillcolor, shape=shape, margin='0.1', fontcolor=fontcolor)
        if edge_label is not None:
            dot.edge(edge_label[0], current_node_id, label=edge_label[1], color='#f8f8f2', penwidth='1')

        if is_terminal or is_heuristic:
            return score, None, current_node_id

        valid_moves = board.get_valid_moves()
        best_col = valid_moves[0] if valid_moves else None
        value = -float('inf') if maximizing_player else float('inf')
        best_child_id = None

        if maximizing_player:
            for col in valid_moves:
                # Max node chooses action -> goes to Chance Node
                chance_id = self._get_next_node_id()
                
                # Chance Node Setup
                dot.node(chance_id, label=f"CHANCE\nEV: {0.0:.2f}", style='filled', fillcolor='#8be9fd', shape='diamond', fontcolor='#282a36') # Light blue, black font
                dot.edge(current_node_id, chance_id, label=f"Col {col}", color='#bd93f9', penwidth='2') # Purple edge

                # Calculate Expected Value
                expected_score, _, child_path_id = self._calculate_chance_value(board, depth - 1, col, dot, chance_id)
                score = expected_score
                
                if score > value:
                    value = score
                    best_col = col
                    best_child_id = chance_id

                dot.node(current_node_id, label=f"MAX\nD={depth}\nValue: {value:.2f}", style='filled', fillcolor='#50fa7b', shape='ellipse', fontcolor='#282a36')
            
            return value, best_col, best_child_id

        else: # Minimizing Player
            for col in valid_moves:
                child_id = self._get_next_node_id()
                row, played_col = self._simulate_move(board, col, self.human_player)
                
                score, _, child_path_id = self._expected_minimax_graph(board, depth - 1, True, dot, child_id, (current_node_id, f"Col {col}"), None)
                
                self._undo_move(board, row, played_col)
                
                if score < value:
                    value = score
                    best_child_id = child_path_id

                dot.node(current_node_id, label=f"MIN\nD={depth}\nValue: {value:.2f}", style='filled', fillcolor='#ff5555', shape='ellipse', fontcolor='#f8f8f2')

            return value, None, best_child_id
            
    def _calculate_chance_value(self, board, depth, chosen_col, dot, parent_id):
        """Calculates EV and recursively calls graph generation for child nodes."""
        expected_value = 0
        
        moves = [
            (chosen_col, 0.6, 'P=0.6'),
            (chosen_col - 1, 0.2, 'P=0.2'),
            (chosen_col + 1, 0.2, 'P=0.2')
        ]
        
        best_child_id = None

        for col_idx, prob, label in moves:
            score = 0
            child_id = self._get_next_node_id()
            
            if 0 <= col_idx < board.cols and board.is_valid_move(col_idx):
                row, played_col = self._simulate_move(board, col_idx, self.computer_player)
                score, _, child_path_id = self._expected_minimax_graph(board, depth, False, dot, child_id, (parent_id, label), True)
                self._undo_move(board, row, played_col)
                
            else:
                score = 0 
                dot.node(child_id, label="BLOCKED\nValue: 0.00", style='filled', fillcolor='grey', shape='box', fontcolor='#282a36')
                dot.edge(parent_id, child_id, label=label, color='grey', style='dotted', penwidth='1')
                child_path_id = child_id

            expected_value += prob * score
            
        dot.node(parent_id, label=f"CHANCE\nEV: {expected_value:.2f}", style='filled', fillcolor='#8be9fd', shape='diamond', fontcolor='#282a36')
        
        return expected_value, None, best_child_id