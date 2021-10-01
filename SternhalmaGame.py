from Game import Game
import numpy as np

class SternhalmaGame(Game):
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """
    def __init__(self, whatever):
        triangle_dimension = 2
        self.empty_board = np.zeros((triangle_dimension*2+1, triangle_dimension*2+1))
        self.dim_tri = triangle_dimension
        # FIXME extend for multiple players?
        # self.num_players = players
        # FIXME pieces per player is the triangle number of self.dim_tri
        self.pieces_per_player = 3

        self.directions = np.array([
          [1, 0],
          [0, 1],
          [-1, 0],
          [0, -1],
          [1, -1],
          [-1, 1]
        ])

    def getInitBoard(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        # for p in range(self.num_players):
          # FIXME: to allow larger board dimensions this should be more complicated;
          # the below is the end point but it also includes all other combinations
          # self.board[self.dim_tri*self.directions] = p
        # Player 1 has positive-valued pieces and player -1 has negative-valued pieces
        # This would have to change to generalize to more players
        board = np.copy(self.empty_board)
        board[-2, -2] = 1
        board[-2, -1] = 1
        board[-1, -2] = 1
        board[2, 2] = -1
        board[2, 1] = -1
        board[1, 2] = -1

        # np.ravel(board)?
        return board

    def getBoardSize(self):
        """
        Returns:
            (x,y): a tuple of board dimensions
        """
        # TODO how to deal with something that can be either
        # 1d or 3d, but not 2d?
        return (self.dim_tri*2+1, self.dim_tri*2+1)

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        # FIXME will be more complicated when extended for multi-jumps
        # TODO does this include blocked states? Yeees...? but it's actions not states
        # Actions are: go forward two spaces or back, two spaces or one space,
        # in any of the 3 directions, FOR EACH PIECE.
        return self.pieces_per_player*2*2*3

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        board = self.getCanonicalForm(board, player)
        # print('player', player)
        # print('canonical\n', self.stringRepresentation(board))
        orig_player = player
        player = 1
        if action < 0:
            return self.getCanonicalForm(board, -1*orig_player), -1*orig_player
        board = np.copy(board)
        # Figure out what piece this action corresponds to
        piece = action // 12
        # Find this piece on the board
        pos_positions, neg_positions = self._getPiecePositions(board)
        piece_location = pos_positions[piece]
        if action%2 == 0:
            new_pos = piece_location + 2*self.directions[(action//2)%6]
        else:
            new_pos = piece_location + self.directions[(action//2)%6]
        if not self._onBoard(new_pos):
          print(pos_positions)
          print('old pos:', piece_location)
          print('new pos:', new_pos)
          print(self.stringRepresentation(board))
          print('action', action)
          print('direction', (action//2) % 6)
          print('NOT A VALID POSITION')
          raise Exception()
        # Make its old location zero and set it at new location
        board[piece_location[0]][piece_location[1]] = 0
        board[new_pos[0]][new_pos[1]] = 1
        # print('canonical after moving\n', self.stringRepresentation(board))
        board = self.getCanonicalForm(board, orig_player)
        # print('uncanonical\n', self.stringRepresentation(board))
        return board, -1*orig_player

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        canonicalBoard = board
        moves = np.zeros(self.pieces_per_player*12)
        our_pieces, other_pieces = self._getPiecePositions(canonicalBoard)
        piece_idx = 0
        for p in our_pieces:
            # We are using the canonical form, so we look at the positive pieces.
            # Index into action array in this manner so that the first piece's moves are 0-5,
            # second piece's moves are 6-11, third piece's moves are 12-17.
            moves[piece_idx:piece_idx+12] = self._checkAdjacent(canonicalBoard, p)
            piece_idx += 12
        return moves

    def _checkAdjacent(self, board, pos):
        """ You can move into the specified adjacent spot if that spot is empty and
            the spot between you and that spot is occupied.
        """
        valid = np.zeros((12))
        for i, direction in enumerate(self.directions):
            move_to2 = pos + direction*2
            between = pos + direction
            # TODO numpy has a better way of indexing into an array with an array
            # that generalizes to larger boards, but I don't know how yet
            if self._onBoard(move_to2) and board[move_to2[0]][move_to2[1]] == 0 \
                and board[between[0]][between[1]] != 0:
                valid[i*2] = 1
            move_to1 = pos + direction
            if self._onBoard(move_to1) and board[move_to1[0]][move_to1[1]] == 0:
                valid[i*2+1] = 1
        return valid

    def _onBoard(self, pos):
        # return np.all(pos >= 0) and np.all(pos <= self.dim_tri * 2)
        return np.all(pos >= -self.dim_tri) and np.all(pos <= self.dim_tri)

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """
        # FIXME more complicated for variable dim / num players
        if board[2, 2] > 0 and board[2, 1] > 0 and board[1, 2] > 0:
            if player == 1:
                # print('win')
                return 1
            if player == -1:
                # print('loss')
                return -1
        if board[-2, -2] < 0 and board[-2, -1] < 0 and board[-1, -2] < 0:
            if player == 1:
                # print('loss')
                return -1
            if player == -1:
                # print('win')
                return 1
        return 0

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        if player == -1:
          rolled = np.roll(board, 2, [0, 1])
          rot = np.rot90(rolled, 2)
          unrolled = np.roll(rot, -2, [0, 1])
          return unrolled*-1
        else:
            return board

    def getSymmetries(self, board, pi):
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        l = []
        board = np.roll(board, 2, [0, 1])
        for i in [True, False]:
            for j in [True, False]:
                newPi = np.copy(pi)
                if i:
                    newB = np.rot90(board, 2)
                    newPi = self._rotPi(newPi)
                if j:
                    newB = np.transpose(newB)
                    try:
                        newPi = self._flipPi(newPi)
                    except Exception as e:
                      print(pi.shape)
                      print(newPi)
                      raise e
                newB = np.roll(board, -2, [0, 1])
                l += [(newB, newPi)]
        return l
        # Comment above and uncomment below if you don't feel confident symmetries are correct
        # return [(board, pi)]

    def _flipPi(self, pi):
        newPi = pi[:]
        for i in range(len(newPi)):
            if (i//2)%6 == 0 or (i//2)%6 == 2 or (i//2)%6 == 4:
                newPi[i] = pi[i+2]
            if (i//2)%6 == 1 or (i//2)%6 == 3 or (i//2)%6 == 5:
                newPi[i] = pi[i-2]
        return newPi

    def _rotPi(self, pi):
        newPi = pi[:]
        for i in range(len(newPi)):
            if (i//2)%6 == 0 or (i//2)%6 == 1:
                newPi[i] = pi[i+2]
            if (i//2)%6 == 2 or (i//2)%6 == 3:
                newPi[i] = pi[i-2]
            if (i//2)%6 == 4:
                newPi[i] = pi[i+2]
            if (i//2)%6 == 5:
                newPi[i] = pi[i-2]
        return newPi

    def _getPiecePositions(self, board):
        pos_pieces, neg_pieces = [], []
        for x in range(-self.dim_tri, self.dim_tri+1):
            for y in range(-self.dim_tri, self.dim_tri+1):
                if board[x, y] == 1:
                    pos_pieces.append(np.array([x, y]))
                elif board[x, y] == -1:
                    neg_pieces.append(np.array([x, y]))
        return pos_pieces, neg_pieces

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        string_rep = []
        for i in range(-self.dim_tri, self.dim_tri+1):
            for j in range(-self.dim_tri, self.dim_tri+1):
                string_rep.append(str(int(board[i][j])).rjust(3))
            string_rep.append('\n')

        return ''.join(string_rep)
