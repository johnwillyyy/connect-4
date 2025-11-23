import tkinter as tk
from tkinter import messagebox, ttk
import time

class ConnectFourGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect Four - Human vs Computer")
        self.root.resizable(False, False)
        
        # Game variables (to be set by player choices)
        self.human_color = None
        self.computer_color = None
        self.algorithm = None
        self.difficulty = None
        self.game_board = None
        
        # Response time tracking
        self.computer_response_time = 0
        
        self.setup_welcome_screen()
    
    def setup_welcome_screen(self):
        """Initial screen for color selection"""
        self.clear_screen()
        
        # Title
        title_label = tk.Label(self.root, text="Connect Four", 
                              font=("Arial", 24, "bold"), fg="blue")
        title_label.pack(pady=20)
        
        # Color selection frame
        color_frame = tk.Frame(self.root)
        color_frame.pack(pady=20)
        
        tk.Label(color_frame, text="Choose your color:", 
                font=("Arial", 14)).pack(pady=10)
        
        color_choice_frame = tk.Frame(color_frame)
        color_choice_frame.pack(pady=10)
        
        # Yellow button (goes first)
        yellow_btn = tk.Button(color_choice_frame, text="Yellow (First)", 
                              font=("Arial", 12), bg="yellow", width=12, height=2,
                              command=lambda: self.choose_color("yellow"))
        yellow_btn.pack(side=tk.LEFT, padx=10)
        
        # Red button
        red_btn = tk.Button(color_choice_frame, text="Red", 
                           font=("Arial", 12), bg="red", fg="white", width=12, height=2,
                           command=lambda: self.choose_color("red"))
        red_btn.pack(side=tk.LEFT, padx=10)
    
    def choose_color(self, color):
        """Set player color and proceed to algorithm selection"""
        self.human_color = color
        self.computer_color = "red" if color == "yellow" else "yellow"
        self.setup_algorithm_selection()
    
    def setup_algorithm_selection(self):
        """Screen for algorithm and difficulty selection"""
        self.clear_screen()
        
        # Title
        title_label = tk.Label(self.root, text="Computer Settings", 
                              font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        # Algorithm selection frame
        algo_frame = tk.LabelFrame(self.root, text="Select Algorithm", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        algo_frame.pack(pady=20, padx=20, fill="x")
        
        self.algorithm_var = tk.StringVar(value="minimax_ab")
        
        algorithms = [
            ("Minimax with Alpha-Beta Pruning", "minimax_ab"),
            ("Minimax without Alpha-Beta", "minimax"),
            ("Expected Minimax", "expected_minimax")
        ]
        
        for text, value in algorithms:
            tk.Radiobutton(algo_frame, text=text, variable=self.algorithm_var,
                          value=value, font=("Arial", 10)).pack(anchor="w", pady=5)
        
        # Difficulty selection frame
        diff_frame = tk.LabelFrame(self.root, text="Select Difficulty (1-10)", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        diff_frame.pack(pady=20, padx=20, fill="x")
        
        self.difficulty_var = tk.IntVar(value=5)
        
        difficulty_scale = tk.Scale(diff_frame, from_=1, to=10, 
                                   orient=tk.HORIZONTAL, variable=self.difficulty_var,
                                   font=("Arial", 10), length=300)
        difficulty_scale.pack(pady=10)
        
        # Start game button
        start_btn = tk.Button(self.root, text="Start Game", 
                             font=("Arial", 14, "bold"), bg="green", fg="white",
                             command=self.start_game, width=15, height=2)
        start_btn.pack(pady=20)
    
    def start_game(self):
        """Initialize the game with selected settings"""
        self.algorithm = self.algorithm_var.get()
        self.difficulty = self.difficulty_var.get()
        self.game_board = ConnectFourBoard()
        
        self.setup_game_screen()
    
    def setup_game_screen(self):
        """Main game screen with board and controls"""
        self.clear_screen()
        
        # Top info frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        # Current player display
        self.current_player_label = tk.Label(
            info_frame, 
            text=f"Current: {'Human (Yellow)' if self.game_board.current_player == 1 else 'Computer (Red)'}", 
            font=("Arial", 12, "bold"),
            fg="yellow" if self.game_board.current_player == 1 else "red"
        )
        self.current_player_label.pack(side=tk.LEFT, padx=20)
        
        # Score display
        self.score_label = tk.Label(
            info_frame,
            text="Human: 0 | Computer: 0",
            font=("Arial", 12)
        )
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        # Response time display
        self.time_label = tk.Label(
            info_frame,
            text="Computer time: 0.00s",
            font=("Arial", 10),
            fg="gray"
        )
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        # Game board canvas
        self.canvas = tk.Canvas(self.root, width=700, height=600, bg="blue")
        self.canvas.pack(pady=10)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Display Game Tree button (placeholder)
        tree_btn = tk.Button(control_frame, text="Display Game Tree", 
                            font=("Arial", 10), state="disabled")
        tree_btn.pack(side=tk.LEFT, padx=5)
        
        # Restart button
        restart_btn = tk.Button(control_frame, text="New Game", 
                               font=("Arial", 10), command=self.restart_game)
        restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Draw the initial board
        self.draw_board()
        
        # Bind mouse events for human moves
        self.canvas.bind("<Button-1>", self.human_move)
        
        # If computer goes first, make its move
        if self.game_board.current_player == 2:
            self.root.after(500, self.computer_move)
    
    def draw_board(self):
        """Draw the Connect Four board with round cells"""
        self.canvas.delete("all")
        
        cell_width = 100
        cell_height = 100
        padding = 10
        radius = 40
        
        # Draw board background
        self.canvas.create_rectangle(0, 0, 700, 600, fill="blue", outline="blue")
        
        # Draw cells and pieces
        for col in range(7):
            for row in range(6):
                x1 = col * cell_width + padding
                y1 = (5 - row) * cell_height + padding  # Invert y-axis
                x2 = x1 + cell_width - 2 * padding
                y2 = y1 + cell_height - 2 * padding
                
                # Draw cell (hole)
                self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="blue")
                
                # Draw piece if present
                if self.game_board.board[col][row] != 0:
                    color = "yellow" if self.game_board.board[col][row] == 1 else "red"
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, 
                                          fill=color, outline=color)
    
    def human_move(self, event):
        """Handle human player's move"""
        if self.game_board.game_over or self.game_board.current_player != 1:
            return
            
        col = event.x // 100  # Determine which column was clicked
        
        if 0 <= col < 7 and self.game_board.is_valid_move(col):
            result = self.game_board.play_at_column(col)
            if result:
                self.draw_board()
                self.update_display()
                
                if not self.game_board.game_over:
                    self.root.after(500, self.computer_move)
                else:
                    self.game_finished()
    
    def computer_move(self):
        """Handle computer player's move (placeholder for now)"""
        if self.game_board.game_over or self.game_board.current_player != 2:
            return
            
        start_time = time.time()
        
        # Placeholder - random move for now
        valid_moves = self.game_board.get_valid_moves()
        if valid_moves:
            col = random.choice(valid_moves)
            result = self.game_board.play_at_column(col)
            
            # Calculate response time
            self.computer_response_time = time.time() - start_time
            
            if result:
                self.draw_board()
                self.update_display()
                
                if self.game_board.game_over:
                    self.game_finished()
    
    def update_display(self):
        """Update the game information display"""
        # Update current player
        player_text = "Human (Yellow)" if self.game_board.current_player == 1 else "Computer (Red)"
        player_color = "yellow" if self.game_board.current_player == 1 else "red"
        self.current_player_label.config(text=f"Current: {player_text}", fg=player_color)
        
        # Update scores
        human_score = self.game_board.count_connected_fours(1)
        computer_score = self.game_board.count_connected_fours(2)
        self.score_label.config(text=f"Human: {human_score} | Computer: {computer_score}")
        
        # Update response time
        self.time_label.config(text=f"Computer time: {self.computer_response_time:.2f}s")
    
    def game_finished(self):
        """Handle game completion"""
        human_score = self.game_board.count_connected_fours(1)
        computer_score = self.game_board.count_connected_fours(2)
        
        if human_score > computer_score:
            winner = "Human wins!"
        elif computer_score > human_score:
            winner = "Computer wins!"
        else:
            winner = "It's a tie!"
        
        message = f"Game Over!\n{winner}\n\nFinal Scores:\nHuman: {human_score}\nComputer: {computer_score}"
        
        result = messagebox.askyesno("Game Finished", f"{message}\n\nPlay again?")
        
        if result:
            self.restart_game()
        else:
            self.root.quit()
    
    def restart_game(self):
        """Restart the game with same settings"""
        self.game_board.reset_board()
        self.computer_response_time = 0
        self.draw_board()
        self.update_display()
        
        # If computer goes first, make its move
        if self.game_board.current_player == 2:
            self.root.after(500, self.computer_move)
    
    def clear_screen(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

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

# Example usage and testing
if __name__ == "__main__":
    app = ConnectFourGUI()
    app.run()