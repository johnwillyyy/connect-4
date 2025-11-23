import tkinter as tk
from tkinter import messagebox, ttk
import time
import random
import io 
from GameBoard import ConnectFourBoard
from AIAgent import AIAgent 
# Dependencies for Graphic Visualization
from graphviz import Source 
from PIL import Image, ImageTk 

class ConnectFourGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect Four - Human vs Computer")
        self.root.resizable(False, False)
        
        # Game variables
        self.human_color = None
        self.computer_color = None
        self.algorithm = None
        self.difficulty = None
        self.game_board = None
        self.computer_player = None
        self.human_player = None
        self.agent = None
        
        self.computer_response_time = 0
        
        # Variable to store the Graphviz DOT source string for rendering
        self.last_graph_source = "" 
        
        self.setup_welcome_screen()
    
    def setup_welcome_screen(self):
        """Initial screen for color selection"""
        self.clear_screen()
        
        title_label = tk.Label(self.root, text="Connect Four", 
                              font=("Arial", 24, "bold"), fg="blue")
        title_label.pack(pady=20)
        
        color_frame = tk.Frame(self.root)
        color_frame.pack(pady=20)
        
        tk.Label(color_frame, text="Choose your color:", 
                font=("Arial", 14)).pack(pady=10)
        
        color_choice_frame = tk.Frame(color_frame)
        color_choice_frame.pack(pady=10)
        
        yellow_btn = tk.Button(color_choice_frame, text="Yellow (First)", 
                              font=("Arial", 12), bg="yellow", width=12, height=2,
                              command=lambda: self.choose_color("yellow"))
        yellow_btn.pack(side=tk.LEFT, padx=10)
        
        red_btn = tk.Button(color_choice_frame, text="Red", 
                           font=("Arial", 12), bg="red", fg="white", width=12, height=2,
                           command=lambda: self.choose_color("red"))
        red_btn.pack(side=tk.LEFT, padx=10)
    
    def choose_color(self, color):
        """Set player color and proceed to algorithm selection"""
        self.human_color = color
        self.computer_color = "red" if color == "yellow" else "yellow"
        self.computer_player = 2 if color == "yellow" else 1
        self.human_player = 3 - self.computer_player
        self.setup_algorithm_selection()
    
    def setup_algorithm_selection(self):
        """Screen for algorithm and difficulty (search depth K) selection"""
        self.clear_screen()
        
        title_label = tk.Label(self.root, text="Computer Settings (Search Depth K)", 
                              font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
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
        
        diff_frame = tk.LabelFrame(self.root, text="Select Search Depth (K: 1-10)", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        diff_frame.pack(pady=20, padx=20, fill="x")
        
        self.difficulty_var = tk.IntVar(value=5)
        
        difficulty_scale = tk.Scale(diff_frame, from_=1, to=10, 
                                   orient=tk.HORIZONTAL, variable=self.difficulty_var,
                                   font=("Arial", 10), length=300)
        difficulty_scale.pack(pady=10)
        
        start_btn = tk.Button(self.root, text="Start Game", 
                             font=("Arial", 14, "bold"), bg="green", fg="white",
                             command=self.start_game, width=15, height=2)
        start_btn.pack(pady=20)
    
    def start_game(self):
        """Initialize the game with selected settings"""
        self.algorithm = self.algorithm_var.get()
        self.difficulty = self.difficulty_var.get()
        self.game_board = ConnectFourBoard()
        
        self.agent = AIAgent(self.computer_player, self.human_player, self.difficulty)

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
            text=f"Current: {'You' if self.game_board.current_player == self.human_player else 'Computer'}", 
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
        
        # Display Game Tree button (Now functional as a graphic pop-up trigger)
        self.tree_btn = tk.Button(control_frame, text="Show Search Tree (Graphic)", 
                            font=("Arial", 10), command=self.show_search_tree_popup, state="disabled")
        self.tree_btn.pack(side=tk.LEFT, padx=5)
        
        # Restart button
        restart_btn = tk.Button(control_frame, text="New Game", 
                               font=("Arial", 10), command=self.restart_game)
        restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Draw the initial board
        self.draw_board()
        
        # Bind mouse events for human moves
        self.canvas.bind("<Button-1>", self.human_move)
        
        # If computer goes first, make its move
        if self.game_board.current_player == self.computer_player:
            self.root.after(500, self.computer_move)
            
    def show_search_tree_popup(self):
        """Renders the Graphviz source and displays it as an image in a pop-up window."""
        if not self.last_graph_source:
            messagebox.showinfo("Search Tree", "The computer has not made a move yet.")
            return

        try:
            # 1. Render DOT source to PNG data in memory
            # Graphviz is used to render the graph definition created in AIAgent.py
            dot = Source(self.last_graph_source)
            png_bytes = dot.pipe(format='png')
            
            # 2. Load PNG data into PIL Image object
            image_data = io.BytesIO(png_bytes)
            pil_image = Image.open(image_data)
            
            # 3. Create Tkinter Toplevel window
            popup = tk.Toplevel(self.root)
            popup.title("AI Minimax Tree (Depth K={})".format(self.difficulty))
            popup.grab_set() 

            # 4. Create scrollable canvas for the potentially large image
            canvas_frame = tk.Frame(popup)
            canvas_frame.pack(expand=True, fill=tk.BOTH)

            tree_canvas = tk.Canvas(canvas_frame, bg='white')
            
            # Scrollbars
            v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=tree_canvas.yview)
            h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=tree_canvas.xview)
            tree_canvas.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            tree_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            # 5. Convert PIL image to Tkinter PhotoImage and display
            tk_image = ImageTk.PhotoImage(pil_image)
            tree_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            
            # CRITICAL: Configure scroll region and keep a reference
            tree_canvas.config(scrollregion=(0, 0, pil_image.width, pil_image.height))
            tree_canvas.image = tk_image 

            # Set popup size (maximized to screen size if necessary)
            max_width = self.root.winfo_screenwidth() * 0.9
            max_height = self.root.winfo_screenheight() * 0.9
            w = min(pil_image.width, int(max_width))
            h = min(pil_image.height, int(max_height))
            
            popup.geometry(f"{w}x{h}")
            
        except Exception as e:
            # This robust error handling guides the user to fix the required installations.
            messagebox.showerror("Visualization Error", 
                                 f"Failed to render graphic tree. Check required installations:\n1. Graphviz system tool\n2. Python packages (pip install graphviz pillow)\n\nDetailed Error: {e}")
            print(f"Graphviz rendering error: {e}")
    
    def draw_board(self):
        """Draw the Connect Four board with round cells"""
        self.canvas.delete("all")
        
        cell_width = 100
        cell_height = 100
        padding = 10
        
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
        if self.game_board.game_over or self.game_board.current_player == self.computer_player:
            return
            
        col = event.x // 100
        
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
        """Handle computer player's move using the selected AI algorithm"""
        if self.game_board.game_over or self.game_board.current_player == self.human_player:
            return
            
        start_time = time.time()
        
        col = self.agent.get_best_move(self.game_board, self.algorithm)

        # 1. Store the Graphviz DOT source string
        self.last_graph_source = self.agent.get_graphviz_source()
        
        # 2. Enable the Show Search Tree button
        if hasattr(self, 'tree_btn'):
            self.tree_btn.config(state="normal")
        
        # Proceed with the move
        if col != -1 and self.game_board.is_valid_move(col):
            result = self.game_board.play_at_column(col)
            
            self.computer_response_time = time.time() - start_time
            
            if result:
                self.draw_board()
                self.update_display()
                
                if self.game_board.game_over:
                    self.game_finished()
        else:
            self.game_finished()
    
    def update_display(self):
        """Update the game information display"""
        # Update current player
        player_text = "Human" if self.game_board.current_player == self.human_player else "Computer"
        player_color = "yellow" if self.game_board.current_player == 1 else "red"
        self.current_player_label.config(text=f"Current: {player_text}", fg=player_color)
        
        # Update scores
        human_score = self.game_board.count_connected_fours(self.human_player)
        computer_score = self.game_board.count_connected_fours(self.computer_player)
        self.score_label.config(text=f"Human: {human_score} | Computer: {computer_score}")
        
        # Update response time
        self.time_label.config(text=f"Computer time: {self.computer_response_time:.2f}s")
    
    def game_finished(self):
        """Handle game completion"""
        human_score = self.game_board.count_connected_fours(self.human_player)
        computer_score = self.game_board.count_connected_fours(self.computer_player)
        
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
        self.last_graph_source = "" 
        self.setup_welcome_screen()
    
    def clear_screen(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Example usage and testing
if __name__ == "__main__":
    app = ConnectFourGUI()
    app.run()