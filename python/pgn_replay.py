import tkinter as tk
from tkinter import filedialog, messagebox

import chess
import chess.pgn
import pygame

from chess_interface import ChessInterface


class PGNReplayApp(ChessInterface):
    def __init__(self, pgn_path: str):
        super().__init__()
        pygame.display.set_caption("Xeque PGN Replay")

        self.pgn_path = pgn_path
        self.game_result = "*"
        self.result_sent = False
        self.moves = self.load_game()
        self.move_index = 0

    def load_game(self):
        with open(self.pgn_path, "r", encoding="utf-8", errors="replace") as pgn_file:
            game = chess.pgn.read_game(pgn_file)

        if game is None:
            raise ValueError("No valid PGN game found in the selected file.")

        self.game_result = game.headers.get("Result", "*")
        return list(game.mainline_moves())

    def step_forward(self):
        if self.move_index >= len(self.moves):
            return

        move = self.moves[self.move_index]

        if move not in self.board.legal_moves:
            print(f"Illegal PGN move at index {self.move_index}: {move}")
            return

        # This sends OSC because it uses your existing handle_move()
        self.handle_move(move)

        self.move_index += 1

        if self.move_index >= len(self.moves):
            self.send_pgn_result()

    def step_backward(self):
        if self.move_index <= 0:
            return

        # Undo board state only. No OSC is sent.
        self.board.pop()
        self.move_index -= 1
        self.result_sent = False

        if self.board.move_stack:
            self.last_move = self.board.move_stack[-1]
        else:
            self.last_move = None

    def send_pgn_result(self):
        if self.result_sent:
            return

        if self.game_result == "1-0":
            # White won
            self.osc.send_end_button(0, 0)

        elif self.game_result == "0-1":
            # Black won
            self.osc.send_end_button(0, 1)

        elif self.game_result == "1/2-1/2":
            # Draw
            self.osc.send_end_button(2, 2)

        self.result_sent = True

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RIGHT:
                            self.step_forward()

                        elif event.key == pygame.K_LEFT:
                            self.step_backward()

                self.draw_board()
                self.draw_pieces()
                pygame.display.flip()

        finally:
            self.analyzer.close()
            pygame.quit()


def choose_pgn_file():
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Choose a PGN file",
        filetypes=[
            ("PGN files", "*.pgn"),
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()
    return path


def main():
    pgn_path = choose_pgn_file()

    if not pgn_path:
        return

    try:
        app = PGNReplayApp(pgn_path)
        app.run()
    except Exception as e:
        messagebox.showerror("Xeque PGN Stepper Error", str(e))


if __name__ == "__main__":
    main()