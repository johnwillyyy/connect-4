class ConnectFourBoard:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(rows)] for _ in range(cols)]
        self.current_player = 1 
        self.game_over = False
        
    
    def reset_board(self):
        self.board = [[0 for _ in range(self.rows)] for _ in range(self.cols)]
        self.current_player = 1
        self.game_over = False
    
    def switch_turns(self):
        self.current_player = 3 - self.current_player  # Switches between 1 and 2

    def play_at_column(self, col):
        if not self.is_valid_move(col):
            return None
         
        for row in range(self.rows):
            if self.board[col][row] == 0:
                self.board[col][row] = self.current_player                
                if self.is_board_full():
                    self.game_over = True                
                else:
                    self.switch_turns()
                
                return (row, col)
        
        return None  # Column is full
    
    def is_valid_move(self, col):
        if col < 0 or col >= self.cols:
            return False
        return self.board[col][self.rows - 1] == 0  # Check if top cell is empty
    
    def get_valid_moves(self):
        return [col for col in range(self.cols) if self.is_valid_move(col)]
    
    def is_board_full(self):
        for col in range(self.cols):
            if self.is_valid_move(col):
                return False
        return True
    
    def count_connected_fours(self, player):
        count = 0
        
        # Check horizontal
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if all(self.board[col + i][row] == player for i in range(4)):
                    count += 1
        
        # Check vertical
        for col in range(self.cols):
            for row in range(self.rows - 3):
                if all(self.board[col][row + i] == player for i in range(4)):
                    count += 1
        
        # Check diagonal (top-left to bottom-right)
        for col in range(self.cols - 3):
            for row in range(self.rows - 3):
                if all(self.board[col + i][row + i] == player for i in range(4)):
                    count += 1
        
        # Check diagonal (top-right to bottom-left)
        for col in range(3, self.cols):
            for row in range(self.rows - 3):
                if all(self.board[col - i][row + i] == player for i in range(4)):
                    count += 1
        
        return count
    
    def evaluate_heuristic(self, player):
        """
        Evaluate board heuristic for the given player
        Returns: score where positive favors the player, negative favors opponent
        """
        weights = {4: 1000, 3: 100, 2: 10, 1: 1} 

        def evaluate_window(window, player):
            """Evaluate a 4-cell window"""
            opponent = 3 - player
            player_count = 0
            opponent_count = 0
            
            for cell in window:
                if cell == player:
                    player_count += 1
                elif cell == opponent:
                    opponent_count += 1
            
            # If both players have pieces, window is blocked (worth 0)
            if player_count > 0 and opponent_count > 0:
                return 0
            
            # Return weighted score for the player who controls this window
            if player_count > 0:
                return weights[player_count]
            elif opponent_count > 0:
                return -weights[opponent_count]
            else:
                return 0  # Empty window
        
        total_score = 0
        
        # Check all horizontal windows
        for row in range(self.rows):
            for col in range(self.cols - 3):
                window = [self.board[col + i][row] for i in range(4)]
                total_score += evaluate_window(window, player)
        
        # Check all vertical windows  
        for col in range(self.cols):
            for row in range(self.rows - 3):
                window = [self.board[col][row + i] for i in range(4)]
                total_score += evaluate_window(window, player)
        
        # Check diagonal (top-left to bottom-right)
        for col in range(self.cols - 3):
            for row in range(self.rows - 3):
                window = [self.board[col + i][row + i] for i in range(4)]
                total_score += evaluate_window(window, player)
        
        # Check diagonal (top-right to bottom-left)
        for col in range(3, self.cols):
            for row in range(self.rows - 3):
                window = [self.board[col - i][row + i] for i in range(4)]
                total_score += evaluate_window(window, player)
        
        return total_score
    
    def get_board_state(self):
        return [col[:] for col in self.board]  # Return a copy
    
    def print_board(self):
        """Print the board to console (for debugging)."""
        print("Current Board:")
        for row in range(self.rows - 1, -1, -1):  # Print from top to bottom
            row_str = "|"
            for col in range(self.cols):
                cell = self.board[col][row]
                if cell == 0:
                    row_str += " |"
                elif cell == 1:
                    row_str += "X|"
                else:
                    row_str += "O|"
            print(row_str)
        print("-" * (self.cols * 2 + 1))
        print(" " + " ".join(str(i) for i in range(self.cols)))

