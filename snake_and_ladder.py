import tkinter as tk
from tkinter import messagebox, ttk
import random
from collections import deque
import math

# ------------------- Board and Player Classes ------------------- #

class Board:
    def __init__(self, snakes, ladders):
        self.snakes = snakes
        self.ladders = ladders
        self.size = 100

    def get_final_position(self, start_pos):
        """Return the final position after snakes or ladders"""
        current_pos = start_pos
        while True:
            if current_pos in self.ladders and self.ladders[current_pos] > current_pos:
                current_pos = self.ladders[current_pos]
                continue
            if current_pos in self.snakes and self.snakes[current_pos] < current_pos:
                current_pos = self.snakes[current_pos]
                continue
            break
        return current_pos

class Player:
    def __init__(self, name, color, player_id):
        self.name = name
        self.color = color
        self.position = 0
        self.player_id = player_id
        self.has_won = False
        self.token_id = None
        self.text_id = None
        self.shadow_id = None
        self.canvas_x = 0
        self.canvas_y = 0

    def move(self, dice_roll, board):
        if self.has_won:
            return self.position
        new_position = self.position + dice_roll
        if new_position > 100:
            return self.position
        self.position = board.get_final_position(new_position)
        if self.position == 100:
            self.has_won = True
        return self.position

# ------------------- Game Logic ------------------- #

class SnakeLadderGame:
    def __init__(self, num_players=2):
        # Snakes (head->tail) and ladders (bottom->top)
        self.snakes = {99: 54, 70: 55, 52: 42, 25: 2, 95: 72}
        self.ladders = {3: 22, 5: 8, 11: 26, 44: 77, 66: 86}

        self.board = Board(self.snakes, self.ladders)
        self.num_players = num_players
        self.players = []
        self.current_player_index = 0
        self.game_started = False
        self.game_over = False

        colors = ["red", "blue", "green", "yellow"]
        names = ["Player 1", "Player 2", "Player 3", "Player 4"]
        for i in range(num_players):
            self.players.append(Player(names[i], colors[i], i))

    def roll_dice(self):
        return random.randint(1, 6)

    def play_turn(self):
        if self.game_over:
            return None, None, False
        current_player = self.players[self.current_player_index]
        dice_roll = self.roll_dice()
        old_pos = current_player.position
        new_pos = current_player.move(dice_roll, self.board)
        extra_turn = False
        if current_player.has_won:
            self.game_over = True
            return dice_roll, (old_pos, new_pos), True
        if dice_roll == 6:
            extra_turn = True
        else:
            self.current_player_index = (self.current_player_index + 1) % self.num_players
        return dice_roll, (old_pos, new_pos), extra_turn

    def determine_starting_player(self):
        rolls = [self.roll_dice() for _ in self.players]
        max_roll = max(rolls)
        starting_index = rolls.index(max_roll)
        self.current_player_index = starting_index
        return rolls, starting_index

    def restart(self):
        self.__init__(self.num_players)
        self.game_started = True

# ------------------- BFS Analysis ------------------- #

def bfs_min_moves_with_path(snakes, ladders, N=100):
    """BFS that returns both minimum moves and the optimal path"""
    visited = [False] * (N + 1)
    parent = [-1] * (N + 1)  # To track the path
    dice_rolls = [0] * (N + 1)  # To track dice rolls used
    queue = deque([(1, 0)])
    visited[1] = True
    parent[1] = 0  # Start node
    
    while queue:
        cell, dist = queue.popleft()
        if cell == N:
            # Reconstruct the path
            path = []
            current = cell
            while current != 0:
                path.append(current)
                current = parent[current]
            path.reverse()
            return dist, path
        
        for dice in range(1, 7):
            next_cell = cell + dice
            if next_cell <= N:
                # Apply snakes and ladders
                final_cell = next_cell
                if next_cell in ladders:
                    final_cell = ladders[next_cell]
                elif next_cell in snakes:
                    final_cell = snakes[next_cell]
                
                if not visited[final_cell]:
                    visited[final_cell] = True
                    parent[final_cell] = cell
                    dice_rolls[final_cell] = dice
                    queue.append((final_cell, dist + 1))
    
    return -1, []

def bfs_min_moves(snakes, ladders, N=100):
    min_moves, _ = bfs_min_moves_with_path(snakes, ladders, N)
    return min_moves

# ------------------- GUI ------------------- #

class SnakeLadderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake and Ladder Game - Enhanced Edition")
        self.root.geometry("1000x800")  # Increased width for BFS visualization
        self.root.resizable(True, True)

        self.game = SnakeLadderGame(2)
        self.dice_animation_id = None
        self.move_animation_id = None
        self.cell_size = 50
        self.padding = 50
        self.show_bfs_path = False
        self.bfs_path = []

        self.setup_gui()
        self.update_bfs_info()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(main_frame, width=300)  # Increased width
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        # Main game canvas
        self.canvas = tk.Canvas(left_frame, width=700, height=600, bg='light blue')  # Increased width
        self.canvas.pack(pady=10)
        
        # BFS Visualization canvas (below main board)
        self.bfs_canvas = tk.Canvas(left_frame, width=700, height=150, bg='white', relief='solid', bd=1)
        self.bfs_canvas.pack(pady=5)
        
        # BFS canvas title
        self.bfs_canvas.create_text(350, 15, text="Optimal Path Visualization (BFS)", 
                                   font=('Arial', 12, 'bold'), fill='darkblue')

        self.dice_canvas = tk.Canvas(left_frame, width=100, height=100, bg='white', relief='raised', bd=2)
        self.dice_canvas.pack(pady=5)

        # Controls
        controls_frame = ttk.LabelFrame(right_frame, text="Game Controls")
        controls_frame.pack(fill=tk.X, pady=5)

        self.start_button = ttk.Button(controls_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(fill=tk.X, pady=2)
        self.roll_button = ttk.Button(controls_frame, text="Roll Dice", command=self.roll_dice, state=tk.DISABLED)
        self.roll_button.pack(fill=tk.X, pady=2)
        self.restart_button = ttk.Button(controls_frame, text="Restart Game", command=self.restart_game)
        self.restart_button.pack(fill=tk.X, pady=2)
        
        # BFS Controls
        bfs_controls_frame = ttk.LabelFrame(right_frame, text="BFS Visualization")
        bfs_controls_frame.pack(fill=tk.X, pady=5)
        
        self.show_bfs_button = ttk.Button(bfs_controls_frame, text="Show Optimal Path", 
                                         command=self.toggle_bfs_path)
        self.show_bfs_button.pack(fill=tk.X, pady=2)
        
        self.hide_bfs_button = ttk.Button(bfs_controls_frame, text="Hide Optimal Path", 
                                         command=self.hide_bfs_path)
        self.hide_bfs_button.pack(fill=tk.X, pady=2)

        # Game info
        info_frame = ttk.LabelFrame(right_frame, text="Game Information")
        info_frame.pack(fill=tk.X, pady=5)
        self.turn_label = ttk.Label(info_frame, text="Game not started", wraplength=280)
        self.turn_label.pack(pady=5)
        self.dice_label = ttk.Label(info_frame, text="Dice: -", font=('Arial', 14, 'bold'))
        self.dice_label.pack(pady=5)

        # BFS info
        bfs_frame = ttk.LabelFrame(right_frame, text="BFS Analysis")
        bfs_frame.pack(fill=tk.X, pady=5)
        self.bfs_label = ttk.Label(bfs_frame, text="Calculating...", wraplength=280)
        self.bfs_label.pack(pady=5)

        self.position_frame = ttk.LabelFrame(right_frame, text="Player Positions")
        self.position_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.draw_board()
        self.draw_dice(1)
        self.update_position_display()

    # ------------------- BFS Visualization ------------------- #

    def toggle_bfs_path(self):
        """Toggle BFS path visualization"""
        self.show_bfs_path = True
        self.draw_bfs_visualization()

    def hide_bfs_path(self):
        """Hide BFS path visualization"""
        self.show_bfs_path = False
        self.bfs_canvas.delete("all")
        self.bfs_canvas.create_text(350, 15, text="Optimal Path Visualization (BFS)", 
                                   font=('Arial', 12, 'bold'), fill='darkblue')

    def draw_bfs_visualization(self):
        """Draw the BFS optimal path visualization"""
        self.bfs_canvas.delete("all")
        
        # Title
        self.bfs_canvas.create_text(350, 15, text="Optimal Path Visualization (BFS)", 
                                   font=('Arial', 12, 'bold'), fill='darkblue')
        
        # Get BFS path
        min_moves, path = bfs_min_moves_with_path(self.game.snakes, self.game.ladders)
        
        if min_moves == -1 or len(path) == 0:
            self.bfs_canvas.create_text(350, 75, text="No path found to reach 100!", 
                                       font=('Arial', 10), fill='red')
            return
        
        # Draw path visualization
        cell_width = 600 / len(path)  # Dynamic width based on path length
        current_x = 50
        
        for i, cell in enumerate(path):
            # Draw cell rectangle
            color = '#90EE90' if i < len(path) - 1 else '#FF6B6B'  # Green for path, red for final
            self.bfs_canvas.create_rectangle(
                current_x, 40, current_x + cell_width - 10, 90,
                fill=color, outline='black', width=1
            )
            
            # Cell number
            self.bfs_canvas.create_text(
                current_x + (cell_width - 10) / 2, 65,
                text=str(cell), font=('Arial', 8, 'bold')
            )
            
            # Draw arrow to next cell (except for last cell)
            if i < len(path) - 1:
                arrow_start = current_x + cell_width - 10
                arrow_end = current_x + cell_width
                self.bfs_canvas.create_line(
                    arrow_start, 65, arrow_end, 65,
                    arrow=tk.LAST, fill='blue', width=2
                )
                
                # Dice roll info
                dice_roll = path[i+1] - cell
                if dice_roll < 1 or dice_roll > 6:  # Snake or ladder used
                    dice_roll = "S/L"
                
                self.bfs_canvas.create_text(
                    arrow_start - 5, 50,
                    text=str(dice_roll), font=('Arial', 7), fill='darkblue'
                )
            
            current_x += cell_width
        
        # Path summary
        summary_text = f"Optimal Path: {min_moves} moves | Path: {' → '.join(map(str, path))}"
        if len(summary_text) > 80:  # Truncate if too long
            summary_text = summary_text[:77] + "..."
        
        self.bfs_canvas.create_text(350, 120, text=summary_text, 
                                   font=('Arial', 9), fill='darkgreen')

    # ------------------- Board Drawing ------------------- #

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(10):
            for col in range(10):
                if row % 2 == 0:
                    cell_num = 100 - (row * 10 + col)
                else:
                    cell_num = 100 - (row * 10 + (9 - col))
                x1 = self.padding + col * self.cell_size
                y1 = self.padding + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cell_color = '#F0F0F0' if (row + col) % 2 == 0 else '#E8E8E8'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cell_color, outline="black", width=1)
                self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                        text=str(cell_num), font=('Arial', 8, 'bold'))

        self.draw_snakes_and_ladders()
        self.draw_all_players()
        
        # Highlight BFS path on main board if shown
        if self.show_bfs_path:
            self.highlight_bfs_path_on_board()

    def highlight_bfs_path_on_board(self):
        """Highlight the BFS path on the main game board"""
        min_moves, path = bfs_min_moves_with_path(self.game.snakes, self.game.ladders)
        
        if min_moves == -1 or len(path) == 0:
            return
        
        for i, cell in enumerate(path):
            if cell <= 100:  # Only highlight valid cells
                x, y = self.get_cell_coordinates(cell)
                
                # Draw a colored circle on the path cells
                color = '#90EE90' if i < len(path) - 1 else '#FF6B6B'  # Green for path, red for final
                self.canvas.create_oval(
                    x - 8, y - 8, x + 8, y + 8,
                    fill=color, outline='darkgreen', width=1, tags="bfs_highlight"
                )
                
                # Add step number
                self.canvas.create_text(
                    x, y, text=str(i+1), 
                    font=('Arial', 6, 'bold'), fill='black', tags="bfs_highlight"
                )

    def draw_snakes_and_ladders(self):
        """Draw ladders and snakes"""
        # Ladders
        for bottom, top in self.game.ladders.items():
            x1, y1 = self.get_cell_coordinates(bottom)
            x2, y2 = self.get_cell_coordinates(top)
            self.draw_ladder(x1, y1, x2, y2)

        # Snakes (with offset to avoid overlap)
        offsets = [-15, 15, -10, 10, 0]
        for i, (head, tail) in enumerate(self.game.snakes.items()):
            if head > tail:
                x_head, y_head = self.get_cell_coordinates(head)
                x_tail, y_tail = self.get_cell_coordinates(tail)
                # Offset snakes horizontally to prevent overlap
                self.draw_snake(x_head + offsets[i % len(offsets)], y_head,
                                x_tail + offsets[i % len(offsets)], y_tail)

    def draw_ladder(self, x_bottom, y_bottom, x_top, y_top):
        color = "#8B4513"
        dx = x_top - x_bottom
        dy = y_top - y_bottom
        length = math.hypot(dx, dy)
        if length == 0: return
        dx /= length
        dy /= length
        perp_dx = -dy * 8
        perp_dy = dx * 8
        self.canvas.create_line(x_bottom - perp_dx, y_bottom - perp_dy,
                                x_top - perp_dx, y_top - perp_dy, fill=color, width=6)
        self.canvas.create_line(x_bottom + perp_dx, y_bottom + perp_dy,
                                x_top + perp_dx, y_top + perp_dy, fill=color, width=6)
        rung_count = max(3, int(length / 25))
        for i in range(1, rung_count):
            t = i / rung_count
            rung_start_x = x_bottom - perp_dx + dx * length * t
            rung_start_y = y_bottom - perp_dy + dy * length * t
            rung_end_x = x_bottom + perp_dx + dx * length * t
            rung_end_y = y_bottom + perp_dy + dy * length * t
            self.canvas.create_line(rung_start_x, rung_start_y, rung_end_x, rung_end_y,
                                    fill=color, width=4)

    def draw_snake(self, x_head, y_head, x_tail, y_tail):
        points = []
        num_segments = 12
        for i in range(num_segments + 1):
            t = i / num_segments
            x = x_head + (x_tail - x_head) * t + math.sin(t * math.pi * 4) * 10
            y = y_head + (y_tail - y_head) * t
            points.extend([x, y])
        self.canvas.create_line(points, fill="#006400", width=8, smooth=True)
        triangle_size = 12
        self.canvas.create_polygon(
            x_head, y_head - triangle_size,
            x_head - triangle_size, y_head + triangle_size,
            x_head + triangle_size, y_head + triangle_size,
            fill="red", outline="black"
        )
        self.canvas.create_oval(x_tail - 10, y_tail - 10, x_tail + 10, y_tail + 10,
                                fill="darkgreen", outline="black")

    # ------------------- Player Drawing ------------------- #

    def get_cell_coordinates(self, cell_num):
        row = 9 - (cell_num - 1) // 10
        if row % 2 == 0:
            col = 9 - (cell_num - 1) % 10
        else:
            col = (cell_num - 1) % 10
        x = self.padding + col * self.cell_size + self.cell_size / 2
        y = self.padding + row * self.cell_size + self.cell_size / 2
        return x, y

    def draw_all_players(self):
        self.canvas.delete("player_token")
        self.canvas.delete("player_shadow")
        self.canvas.delete("player_text")
        for player in self.game.players:
            if player.position > 0 and player.position <= 100:
                x, y = self.get_cell_coordinates(player.position)
                offset_x = (player.player_id % 2) * 18 - 9
                offset_y = (player.player_id // 2) * 18 - 9
                token_x = x + offset_x
                token_y = y + offset_y
                player.shadow_id = self.canvas.create_oval(
                    token_x - 12 + 3, token_y - 12 + 3,
                    token_x + 12 + 3, token_y + 12 + 3,
                    fill='black', outline="", tags="player_shadow"
                )
                player.token_id = self.canvas.create_oval(
                    token_x - 12, token_y - 12,
                    token_x + 12, token_y + 12,
                    fill=player.color, outline="black", width=2,
                    tags="player_token"
                )
                player.text_id = self.canvas.create_text(
                    token_x, token_y, text=str(player.player_id + 1),
                    fill='white', font=('Arial', 9, 'bold'), tags="player_text"
                )
                player.canvas_x = token_x
                player.canvas_y = token_y

    # ------------------- Dice and Game Controls ------------------- #

    def draw_dice(self, value, size=80):
        self.dice_canvas.delete("all")
        padding = 10
        self.dice_canvas.create_rectangle(padding, padding, size+padding, size+padding, 
                                          fill='white', outline='black', width=2)
        dot_positions = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
            6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]
        }
        center_x = size/2 + padding
        center_y = size/2 + padding
        dot_radius = 5
        dot_spacing = 15
        for dx, dy in dot_positions[value]:
            x = center_x + dx * dot_spacing
            y = center_y + dy * dot_spacing
            self.dice_canvas.create_oval(x-dot_radius, y-dot_radius, x+dot_radius, y+dot_radius, fill='black')

    def update_position_display(self):
        for widget in self.position_frame.winfo_children():
            widget.destroy()
        for player in self.game.players:
            pos_text = f"{player.name}: Position {player.position}"
            if player.has_won:
                pos_text += " - WINNER!"
            label = ttk.Label(self.position_frame, text=pos_text, foreground=player.color,
                              font=('Arial', 9, 'bold'))
            label.pack(anchor=tk.W, pady=2)

    def update_bfs_info(self):
        min_moves, path = bfs_min_moves_with_path(self.game.snakes, self.game.ladders)
        if min_moves != -1:
            self.bfs_label.config(text=f"Minimum dice throws to win: {min_moves}\nOptimal path length: {len(path)} cells")
        else:
            self.bfs_label.config(text="Cannot reach the end!")

    def start_game(self):
        num_players = 2
        self.game = SnakeLadderGame(num_players)
        rolls, starting_player = self.game.determine_starting_player()
        roll_text = "Starting rolls:\n" + "\n".join(f"{p.name}: {r}" for p, r in zip(self.game.players, rolls))
        roll_text += f"\n\n{self.game.players[starting_player].name} starts first!"
        self.turn_label.config(text=roll_text)
        self.roll_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.draw_board()
        self.update_position_display()
        self.update_bfs_info()

    def roll_dice(self):
        if self.game.game_over:
            return
        dice_roll, positions, extra_turn = self.game.play_turn()
        current_player = self.game.players[self.game.current_player_index]
        self.dice_label.config(text=f"Dice: {dice_roll}")
        old_pos, new_pos = positions
        self.draw_board()
        self.update_position_display()
        if self.game.game_over:
            messagebox.showinfo("Game Over", f"{current_player.name} wins the game!")
            self.roll_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)

    def restart_game(self):
        self.game.restart()
        self.turn_label.config(text="Game not started")
        self.dice_label.config(text="Dice: -")
        self.roll_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.draw_board()
        self.update_position_display()
        self.update_bfs_info()
        if self.show_bfs_path:
            self.draw_bfs_visualization()

    def run(self):
        self.root.mainloop()

# ------------------- Run the Game ------------------- #
if __name__ == "__main__":
    app = SnakeLadderGUI()
    app.run()