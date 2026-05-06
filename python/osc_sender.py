import chess
from pythonosc.udp_client import SimpleUDPClient

from config import OSC_IP, OSC_PORT, piece_to_int


class OscSender:
    def __init__(self, ip: str = OSC_IP, port: int = OSC_PORT):
        self.client = SimpleUDPClient(ip, port)

    def send_move(self, move: chess.Move, board_before: chess.Board, board_after: chess.Board) -> None:
        
        piece = board_before.piece_at(move.from_square)
        piece_id = piece_to_int(piece)

        capture = 1 if board_before.is_capture(move) else 0
        check = 1 if board_after.is_check() else 0
        color = 1 if piece.color == chess.WHITE else 0
        # print([piece_id, capture, check, color])

        self.client.send_message("/move", [piece_id, capture, check, color])

    def send_evaluation(self, evaluation: float) -> None:
        self.client.send_message("/evaluation", evaluation)

    # def send_fragility(self, value1: float, value2: float) -> None:
    #     self.client.send_message("/fragility", [value1, value2])
    def send_fragility(self, value1: float) -> None:
        self.client.send_message("/fragility", value1)

    def send_end_button(self, type: int, color: int) -> None:
        """
        Sends end message if button was selected from ui
        """
        self.client.send_message("/end", [type, color])
        print([type, color])
    
    def send_end_cm(self, move: chess.Move, board: chess.Board) -> None:
        """
        Sends message with checkmate information
        """
        piece = board.piece_at(move.to_square)
        
        color = 1 if piece.color == chess.WHITE else 0
        
        self.client.send_message("/end", [1, color])
        print([1, color])


    def send_move_time(self, ms: int) -> None:
        self.client.send_message("/move_time", ms)

    def send_piece_state(self, board: chess.Board) -> None:
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue

            x = chess.square_file(square)
            y = chess.square_rank(square)
            pitch = 48 + y * 2
            color = 1 if piece.color == chess.WHITE else 0

            self.client.send_message(
                "/piece",
                [piece_to_int(piece), x, y, pitch, color]
            )

        self.client.send_message("/update_done", 1)