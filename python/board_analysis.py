import chess
import chess.engine
import frag
from config import STOCKFISH_PATH, ENGINE_TIME_LIMIT


class BoardAnalyzer:
    def __init__(self, engine_path: str = STOCKFISH_PATH):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def get_evaluation(self, board: chess.Board) -> float:
        info = self.engine.analyse(board, chess.engine.Limit(time=ENGINE_TIME_LIMIT))
        score = info["score"].white()

        if score.is_mate():
            mate = score.mate()
            if mate is None:
                return 0.0
            return 10.0 if mate > 0 else -10.0

        cp = score.score()
        return 0.0 if cp is None else cp / 100.0

    def get_fragility(self, board: chess.Board) -> float:
        return frag.compute_fragility(board)

    def close(self) -> None:
        self.engine.quit()