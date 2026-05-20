import chess
import networkx as nx

# Function for computing the interaction graph for a given color, with pawn capturing rules applied
def compute_interactions_for_color(board, color_turn):
    G = nx.DiGraph()
    piece_positions = {square: board.piece_at(square) for square in chess.SQUARES if board.piece_at(square)}
    
    board_copy = board.copy()
    board_copy.turn = color_turn
    
    for square_a, piece_a in piece_positions.items():
        if piece_a.color == color_turn:
            node_a = f"{piece_a.symbol()}_{chess.square_name(square_a)}"  # Include position in node name
            for square_b, piece_b in piece_positions.items():
                if square_a != square_b:
                    node_b = f"{piece_b.symbol()}_{chess.square_name(square_b)}"  # Include position in node name
                    
                    # Defense link (same color)
                    if piece_a.color == piece_b.color:
                        board_copy.remove_piece_at(square_b)
                        if chess.Move(from_square=square_a, to_square=square_b) in board_copy.legal_moves:
                            G.add_edge(node_a, node_b, color='blue' if color_turn == chess.WHITE else 'green')
                        board_copy.set_piece_at(square_b, piece_b)
                    # Attack link (different color)
                    elif piece_a.color != piece_b.color:
                        # Special rule for pawns: can only capture diagonally if an enemy piece is present
                        if piece_a.piece_type == chess.PAWN:
                            if piece_b:  # Ensure that there's an enemy piece to capture
                                if chess.Move(from_square=square_a, to_square=square_b) in board_copy.legal_moves:
                                    G.add_edge(node_a, node_b, color='red')
                        else:  # For non-pawn pieces, follow the usual logic
                            if chess.Move(from_square=square_a, to_square=square_b) in board_copy.legal_moves:
                                G.add_edge(node_a, node_b, color='red')
    return G

# Function to compute the full interaction graph
def compute_full_interaction_graph(board):
    G_white = compute_interactions_for_color(board, chess.WHITE)
    G_black = compute_interactions_for_color(board, chess.BLACK)
    G_full = nx.compose(G_white, G_black)
    return G_full

# Function to check if a piece is under attack
def is_piece_under_attack(board, square, color):
    return bool(list(board.attackers(not color, square)))

# Compute Betweenness Centrality for each piece
def compute_betweenness_centrality(G):
    return nx.betweenness_centrality(G, normalized=True)

# Function to compute fragility score for a given color and determine the key piece under attack
def compute_fragility_score(board, G, color):
    betweenness = compute_betweenness_centrality(G)
    fragility_score = 0
    max_betweenness_under_attack = 0

    # Iterate over pieces and compute fragility score
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            under_attack = is_piece_under_attack(board, square, color)
            piece_symbol = f"{piece.symbol()}_{chess.square_name(square)}"
            if under_attack and betweenness.get(piece_symbol, 0) > max_betweenness_under_attack:
                max_betweenness_under_attack = betweenness[piece_symbol]
            fragility_score += betweenness.get(piece_symbol, 0) * under_attack

    return fragility_score

def compute_fragility(board):
    G = compute_full_interaction_graph(board)
    wfragility = compute_fragility_score(board, G, chess.WHITE)
    bfragility = compute_fragility_score(board, G, chess.BLACK)

    return wfragility + bfragility