import chess
import networkx as nx


def compute_interactions_for_color(board, color_turn):
    """
    Based directly on the original notebook.
    Builds a directed graph of attacks and defenses for one side.
    """
    G = nx.DiGraph()
    piece_positions = {
        square: board.piece_at(square)
        for square in chess.SQUARES
        if board.piece_at(square)
    }

    board_copy = board.copy()
    board_copy.turn = color_turn

    for square_a, piece_a in piece_positions.items():
        if piece_a.color != color_turn:
            continue

        node_a = f"{piece_a.symbol()}_{chess.square_name(square_a)}"
        G.add_node(node_a)

        for square_b, piece_b in piece_positions.items():
            if square_a == square_b:
                continue

            node_b = f"{piece_b.symbol()}_{chess.square_name(square_b)}"
            G.add_node(node_b)

            # Defense link
            if piece_a.color == piece_b.color:
                board_copy.remove_piece_at(square_b)

                if chess.Move(square_a, square_b) in board_copy.legal_moves:
                    G.add_edge(node_a, node_b)

                board_copy.set_piece_at(square_b, piece_b)

            # Attack link
            else:
                if piece_a.piece_type == chess.PAWN:
                    # keep original pawn logic
                    if piece_b and chess.Move(square_a, square_b) in board_copy.legal_moves:
                        G.add_edge(node_a, node_b)
                else:
                    if chess.Move(square_a, square_b) in board_copy.legal_moves:
                        G.add_edge(node_a, node_b)

    return G


def compute_full_interaction_graph(board):
    """
    Combine white and black interaction graphs.
    """
    G_white = compute_interactions_for_color(board, chess.WHITE)
    G_black = compute_interactions_for_color(board, chess.BLACK)
    return nx.compose(G_white, G_black)


def is_piece_under_attack(board, square, color):
    """
    Original logic: a piece is under attack if opponent attacks its square.
    """
    return bool(list(board.attackers(not color, square)))


def compute_fragility(board):
    """
    Main simplified function:
    returns total fragility for the current board position.
    """
    G = compute_full_interaction_graph(board)
    betweenness = nx.betweenness_centrality(G, normalized=True)

    fragility_score = 0.0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        if is_piece_under_attack(board, square, piece.color):
            piece_id = f"{piece.symbol()}_{chess.square_name(square)}"
            fragility_score += betweenness.get(piece_id, 0.0)

    return fragility_score