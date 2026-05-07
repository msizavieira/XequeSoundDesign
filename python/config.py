import os
import sys
import chess
import pygame

OSC_IP = "127.0.0.1"
OSC_PORT = 8000

ENGINE_TIME_LIMIT = 0.1

WIDTH = 950
HEIGHT = 800
SQ_SIZE = 800 // 8

PIECE_DIR = "./Pieces"

WHITE = "#f0d9b5"
BLACK = "#b58863"
HIGHLIGHT = "#64c864"
LAST_MOVE = "#c8c832"

def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


PIECE_DIR = resource_path("Pieces")

if sys.platform.startswith("win"):
    STOCKFISH_PATH = resource_path(
        os.path.join("stockfish", "stockfish.exe")
    )
else:
    STOCKFISH_PATH = resource_path(
        os.path.join("stockfish", "stockfish")
    )

def piece_to_int(piece: chess.Piece | None) -> int:
    if piece is None:
        return 0

    mapping = {
        chess.PAWN: 1,
        chess.KNIGHT: 2,
        chess.BISHOP: 3,
        chess.ROOK: 4,
        chess.QUEEN: 5,
        chess.KING: 6,
    }
    return mapping.get(piece.piece_type, 0)



def load_and_scale(path: str, square_size: int):
    return pygame.transform.scale(
        pygame.image.load(path).convert_alpha(),
        (square_size, square_size),
    )


def load_piece_images(piece_dir: str, square_size: int):
    files = {
        "P": "wp.png",
        "N": "wn.png",
        "B": "wb.png",
        "R": "wr.png",
        "Q": "wq.png",
        "K": "wk.png",
        "p": "bp.png",
        "n": "bn.png",
        "b": "bb.png",
        "r": "br.png",
        "q": "bq.png",
        "k": "bk.png",
    }

    return {
        symbol: load_and_scale(os.path.join(piece_dir, filename), square_size)
        for symbol, filename in files.items()
    }