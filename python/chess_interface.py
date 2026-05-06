import pygame
import chess
import time

from config import (
    WIDTH, HEIGHT, SQ_SIZE,
    WHITE, BLACK, HIGHLIGHT, LAST_MOVE, PIECE_DIR,
    load_piece_images
)
from osc_sender import OscSender
from board_analysis import BoardAnalyzer


class ChessInterface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

        self.board = chess.Board()
        self.selected_square = None
        self.last_move = None
        self.running = True
        self.redo_stack = []
        self.move_history_san = []
        self.redo_san_stack = []
        self.font = pygame.font.SysFont("Arial", 24)

        self.piece_images = load_piece_images(PIECE_DIR, SQ_SIZE)

        self.buttons = {
            "draw": pygame.Rect(WIDTH - 140, HEIGHT - 120, 130, 35),
            "white_resign": pygame.Rect(WIDTH - 140, HEIGHT - 80, 130, 35),
            "black_resign": pygame.Rect(WIDTH - 140, HEIGHT - 40, 130, 35),
        }

        self.game_result = None

        self.osc = OscSender()
        self.analyzer = BoardAnalyzer()

        self.last_move_time = time.time()

    def get_square_from_mouse(self, pos):
        x, y = pos
        file = x // SQ_SIZE
        rank = 7 - (y // SQ_SIZE)
        return chess.square(file, rank)

    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                color = WHITE if (rank + file) % 2 == 0 else BLACK
                rect = pygame.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(self.screen, color, rect)

                square = chess.square(file, 7 - rank)

                if self.last_move and square in [self.last_move.from_square, self.last_move.to_square]:
                    pygame.draw.rect(self.screen, LAST_MOVE, rect, 5)

                if self.selected_square == square:
                    pygame.draw.rect(self.screen, HIGHLIGHT, rect, 5)

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is None:
                continue

            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square)
            img = self.piece_images[piece.symbol()]
            self.screen.blit(img, (file * SQ_SIZE, rank * SQ_SIZE))

    def draw_buttons(self):
        for name, rect in self.buttons.items():
            pygame.draw.rect(self.screen, WHITE, rect, border_radius=6)
            pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=6)

            label = {
                "draw": "Draw",
                "white_resign": "White resigns",
                "black_resign": "Black resigns",
            }[name]

            text = self.font.render(label, True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)


    def handle_button_click(self, pos):
        if self.buttons["draw"].collidepoint(pos):
            self.osc.send_end_button(2,2)
            self.game_result = "1/2-1/2"
            print("Game drawn")

        elif self.buttons["white_resign"].collidepoint(pos):
            self.osc.send_end_button(0,1)
            self.game_result = "0-1"
            print("White resigned")

        elif self.buttons["black_resign"].collidepoint(pos):
            self.osc.send_end_button(0,0)
            self.game_result = "1-0"
            print("Black resigned")

    def format_move_history(self):
        lines = []

        for i in range(0, len(self.move_history_san), 2):
            move_number = i // 2 + 1
            white_move = self.move_history_san[i]
            black_move = self.move_history_san[i + 1] if i + 1 < len(self.move_history_san) else ""

            lines.append(f"{move_number}. {white_move} {black_move}".strip())

        return lines
    
    def draw_move_history(self):
        history_rect = pygame.Rect(WIDTH - 150, 0, 150, HEIGHT)
        pygame.draw.rect(self.screen, BLACK, history_rect)

        x = WIDTH - 140
        y = 20
        line_height = 30

        title = self.font.render("Moves", True, WHITE)
        self.screen.blit(title, (x, y))

        y += 40

        for line in self.format_move_history():
            text_surface = self.font.render(line, True, WHITE)
            self.screen.blit(text_surface, (x, y))
            y += line_height

    def handle_move(self, move: chess.Move):
        if move not in self.board.legal_moves:
            return
        
        now = time.time()
        delta_time = now - self.last_move_time
        self.last_move_time = now

        delta_ms = int(delta_time * 1000)

        board_before = self.board.copy()
        san_move = self.board.san(move)
        self.board.push(move)

        self.move_history_san.append(san_move)

        self.osc.send_move(move, board_before, self.board)

        evaluation = self.analyzer.get_evaluation(self.board)
        self.osc.send_evaluation(evaluation)

        fragility = self.analyzer.get_fragility(self.board)
        self.osc.send_fragility(fragility)

        self.osc.send_move_time(delta_ms)

        self.last_move = move
        self.redo_stack.clear()
        self.redo_san_stack.clear()

        if chess.Board.is_checkmate(self.board):
            self.osc.send_end_cm(move, self.board)

    def handle_mouse_click(self):
        square = self.get_square_from_mouse(pygame.mouse.get_pos())

        if self.selected_square is None:
            self.selected_square = square
            return
        
        self.handle_button_click(pygame.mouse.get_pos())

        move = chess.Move(self.selected_square, square)
        self.handle_move(move)
        self.selected_square = None
    
    def undo_move(self):
        if not self.board.move_stack:
            return

        undone_move = self.board.pop()
        self.redo_stack.append(undone_move)

        if self.move_history_san:
            undone_san = self.move_history_san.pop()
            self.redo_san_stack.append(undone_san)

        self.selected_square = None
        self.last_move = self.board.peek() if self.board.move_stack else None
    
    def redo_move(self):
        if not self.redo_stack:
            return

        old_move = self.redo_stack.pop()
        self.board.push(old_move)

        if self.redo_san_stack:
            san_move = self.redo_san_stack.pop()
            self.move_history_san.append(san_move)

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_u:
                            self.undo_move()
                        elif event.key == pygame.K_BACKSPACE:
                            self.undo_move()
                        elif event.key == pygame.K_LEFT:
                            self.undo_move()
                        elif event.key == pygame.K_RIGHT:
                            self.redo_move()
                        elif event.key == pygame.K_ESCAPE:
                            self.selected_square = None
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_mouse_click()

                self.draw_board()
                self.draw_pieces()
                self.draw_move_history()
                self.draw_buttons()
                pygame.display.flip()
        finally:
            self.analyzer.close()
            pygame.quit()

if __name__ == "__main__":
    app = ChessInterface()
    app.run()