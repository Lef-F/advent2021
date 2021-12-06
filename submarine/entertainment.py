from typing import Union

import numpy as np

from submarine.inputs import ReadBingo


class BingoBoard:
    def __init__(self, board: Union[np.array, list]) -> None:
        if isinstance(board, list):
            board = np.array(board)
        elif isinstance(board, np.array):
            pass
        else:
            raise TypeError(
                "Expected board to be numpy array or list but got " + type(board)
            )
        if board.shape != (5, 5):
            raise ValueError("Input shape is not 5x5 but " + str(board.shape))

        self.board = board.astype(int)
        self.shape = self.board.shape
        self.marked = []
        self.unmarked = list(self.board.reshape(5 * 5))
        self._row_scores = {r: 0 for r in range(self.shape[0])}
        self._col_scores = {c: 0 for c in range(self.shape[1])}
        self.winner = {}
        self.score = None

    def check_number(self, num: Union[int, str]):
        if isinstance(num, str):
            num = int(num)
        results = np.where(self.board == num)
        if len(results[0]) + len(results[1]) == 0:
            return False
        if not num in self.marked:
            self.marked.append(num)
            self.unmarked.remove(num)
            for row in results[0]:
                self._row_scores[row] += 1
            for col in results[1]:
                self._col_scores[col] += 1
            self.check_win()
            return True

    def reset(self):
        self.__init__(self.board)

    def check_win(self):
        if self.winner != {}:
            return True

        for row, score in self._row_scores.items():
            if score == self.shape[1]:
                self.winner["row"] = row
                self._calculate_score()
                return True
        for col, score in self._col_scores.items():
            if score == self.shape[1]:
                self.winner["col"] = col
                self._calculate_score()
                return True
        return False

    def _calculate_score(self):
        if self.check_win():
            self.score = np.sum(self.unmarked) * self.marked[-1]


class BingoSolver(ReadBingo):
    def __init__(self, input: str) -> None:
        ReadBingo.__init__(self, input=input)

        self._convert_boards()
        self._solve()

        print(
            f"First board to win is #{self.board_scores[0][0]} and scored {self.board_scores[0][1]} points"
        )
        print(
            f"Last board to win is #{self.board_scores[-1][0]} and scored {self.board_scores[-1][1]} points"
        )

    def _convert_boards(self):
        self.boards = []
        for board in self.raw_boards:
            self.boards.append(BingoBoard(board))

    def _solve(self):
        self.board_scores = []
        for draw in self.drawn_numbers:
            board_num = 1
            for board in self.boards:
                prev_score_state = board.score
                board.check_number(draw)
                if board.score != prev_score_state:
                    self.board_scores.append([board_num, board.score])
                board_num += 1
