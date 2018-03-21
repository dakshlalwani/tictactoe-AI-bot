import datetime, random
from copy import deepcopy


class Team55:
    def __init__(self):
        self.startTime = 0
        self.stopTime = False
        self.INF = 10000000000
        self.player_map = {}
        self.winscore = 500
        self.lossscore = -500
        self.blockwin = 50000
        self.blocklose = -50000
        self.dict = {}
        self.hash_board = dict()
        self.timeLimit = datetime.timedelta(seconds=14.9)
        self.zobrist = []
        for i in xrange(16):
            self.zobrist.append([])
            for j in xrange(16):
                self.zobrist[i].append([])
                for k in xrange(2):
                    self.zobrist[i][j].append(random.randint(0, 0x10000000000000000L))
        self.scores = [1000, 80, 5]
        self.points = [[6, 4, 4, 6], [4, 3, 3, 4], [4, 3, 3, 4], [6, 4, 4, 6]]
        self.diamond = [[[0, 1], [1, 0], [1, 2], [2, 1]], [[0, 2], [1, 1], [1, 3], [2, 2]],
                        [[1, 1], [2, 1], [2, 2], [3, 1]], [[1, 2], [2, 1], [2, 3], [3, 2]]]

    def move(self, board, old_move, flag):
        self.stopTime = False
        self.startTime = datetime.datetime.utcnow()
        depth = 3
        if flag == 'x':
            self.player_map[True] = 'x'
            self.player_map[False] = 'o'
        elif flag == 'o':
            self.player_map[True] = 'o'
            self.player_map[False] = 'x'
        retm = self.idfs(board, old_move, self.startTime, depth, flag)
        return retm

    def idfs(self, board, old_move, stime, depth, flag):
        retm = board.find_valid_move_cells(old_move)[0]
        diff_time = datetime.datetime.utcnow() - stime
        while diff_time < self.timeLimit:
            ret0, ret1 = self.ab_minimax(board, old_move, True, depth, True, -self.INF, self.INF)
            if not self.stopTime:
                retm = ret1
            depth += 1
            diff_time = datetime.datetime.utcnow() - stime
        return retm

    def ab_minimax(self, board, old_move, count, depth, my_chance, alpha, beta):
        children = board.find_valid_move_cells(old_move)
        lenchild = len(children)
        bChild = children[random.randrange(lenchild)]
        if my_chance != 0:
            bestVal = -self.INF
            for child in children:
                self.checktime()
                if self.stopTime:
                    break
                board.update(old_move, child, self.player_map[True])
                bt = board.find_terminal_state()
                if bt[1] == '-':
                    if depth > 0:
                        val = self.ab_minimax(board, child, True, depth - 1, False, alpha, beta)[0]
                    else:
                        hash_value = 0
                        for i in xrange(16):
                            for j in xrange(16):
                                if board.board_status[i][j] != '-':
                                    if board.board_status[i][j] == self.player_map[True]:
                                        hash_value = hash_value ^ self.zobrist[i][j][0]
                                    else:
                                        hash_value = hash_value ^ self.zobrist[i][j][1]

                        if hash_value in self.hash_board:
                            val = (self.hash_board[hash_value])
                        else:
                            draw_score = 0  # called_heuristic
                            for i in xrange(4):
                                for j in range(4):
                                    draw_score += (self.eval_block_score(board, i, j))
                            val = (self.eval_board_score(board) * 50)
                            val += draw_score
                            self.hash_board[hash_value] = val
                    if val > bestVal:
                        bestVal, alpha, bChild = self.myalphabeta(val, alpha, child)
                    if beta <= alpha:
                        self.set_child(board, child)
                        break
                elif bt[1] == 'WON' and bt[0] == self.player_map[True]:
                    self.set_child(board, child)
                    return self.INF, child
                elif bt[1] == 'DRAW':
                    val = 0
                    sign = 0
                    for i in xrange(4):
                        for j in xrange(4):
                            if board.block_status[i][j] == self.player_map[True]:
                                sign = 1
                            elif board.block_status[i][j] == self.player_map[False]:
                                sign = -1
                            val += (self.points[i][j] * sign)
                    if val > 0:
                        val *= 100
                        val += 100000
                    else:
                        val *= 100
                        val -= 100000
                    if val > bestVal:
                        bestVal, alpha, bChild = self.myalphabeta(val, alpha, child)
                    if beta <= alpha:
                        self.set_child(board, child)
                        break
                self.set_child(board, child)
        else:
            bestVal = self.INF
            for child in children:
                self.checktime()
                if self.stopTime:
                    break
                board.update(old_move, child, self.player_map[False])
                bt = board.find_terminal_state()
                if bt[1] == '-':
                    if depth <= 0:
                        hash_value = 0
                        for i in xrange(16):
                            for j in xrange(16):
                                if board.board_status[i][j] != '-':
                                    if board.board_status[i][j] == self.player_map[True]:
                                        hash_value = hash_value ^ self.zobrist[i][j][0]
                                    else:
                                        hash_value = hash_value ^ self.zobrist[i][j][1]

                        if hash_value in self.hash_board:
                            val = (self.hash_board[hash_value])
                        else:
                            draw_score = 0
                            for i in xrange(4):
                                for j in range(4):
                                    draw_score += (self.eval_block_score(board, i, j))
                            val = (self.eval_board_score(board) * 50)
                            val += draw_score
                    else:
                        val = self.ab_minimax(board, child, True, depth - 1, True, alpha, beta)[0]
                    if val < bestVal:
                        bestVal, beta, bChild = self.oppalphabeta(val, beta, child)
                    if beta <= alpha:
                        self.set_child(board, child)
                        break
                elif bt[1] == 'WON' and bt[0] == self.player_map[False]:
                    self.set_child(board, child)
                    return -self.INF, child
                elif bt[1] == 'DRAW':
                    val = 0
                    sign = 0
                    for i in xrange(4):
                        for j in xrange(4):
                            if board.block_status[i][j] == self.player_map[True]:
                                sign = 1
                            elif board.block_status[i][j] == self.player_map[False]:
                                sign = -1
                            val += (self.points[i][j] * sign)
                    if val > 0:
                        val *= 100
                        val += 1000000
                    else:
                        val *= 100
                        val -= 1000000
                    if val < bestVal:
                        bestVal, beta, bChild = self.oppalphabeta(val, beta, child)
                    if beta <= alpha:
                        self.set_child(board, child)
                        break
                self.set_child(board, child)
        return bestVal, bChild

    def myalphabeta(self, val, alpha, child):
        bestVal = val
        alpha = max(alpha, bestVal)
        bChild = child
        return bestVal, alpha, bChild

    def oppalphabeta(self, val, beta, child):
        bestVal = val
        beta = min(beta, bestVal)
        bChild = child
        return bestVal, beta, bChild

    def checktime(self):
        if datetime.datetime.utcnow() - self.startTime > self.timeLimit:
            self.stopTime = True
        return

    def set_child(self, board, child):
        board.block_status[child[0] // 4][child[1] // 4] = '-'
        board.board_status[child[0]][child[1]] = '-'

    def calc_blockscore(self, val, blockscore):
        if val == 3:  # 1 attack move
            blockscore += self.scores[0]
        elif val == 2:  # 2 attack move
            blockscore += self.scores[1]
        elif val == 1:  # 3 attack move
            blockscore += self.scores[2]
        return blockscore

    def calc_boardscore(self, val, boardscore):
        if val == 3:  # 1 attack move
            boardscore += self.scores[0]
        elif val == 2:  # 2 attack move
            boardscore += self.scores[1]
        elif val == 1:
            boardscore += self.scores[2]
        return boardscore

    def calc_val(self, board, opp, pct, x, y, m, n):
        a = x * 4 + m
        b = y * 4 + n
        if board.board_status[a][b] == self.player_map[False]:
            opp += 1
        elif board.board_status[a][b] == self.player_map[True]:
            pct += 1
        return opp, pct

    def check_val_board(self, board, opp, pct, dct, m, n):
        if board.block_status[m][n] == self.player_map[False]:
            opp += 1
        elif board.block_status[m][n] == self.player_map[True]:
            pct += 1
        else:
            dct += 1
        return opp, pct, dct

    def eval_block_score(self, board, x, y):
        myBlockScore = 0
        oppBlockScore = 0

        for i in xrange(4):
            pct = opp = 0
            for j in xrange(4):
                opp, pct = self.calc_val(board, opp, pct, x, y, i, j)
            if opp == 0:
                if pct == 4:
                    myBlockScore = self.blockwin
                    oppBlockScore = self.blocklose
                    return myBlockScore - oppBlockScore
                myBlockScore = self.calc_blockscore(pct, myBlockScore)
            elif pct == 0:
                if opp == 4:
                    myBlockScore = self.blocklose
                    oppBlockScore = self.blockwin
                    return myBlockScore - oppBlockScore
                oppBlockScore = self.calc_blockscore(opp, oppBlockScore)

        for i in xrange(4):
            pct = opp = 0
            for j in xrange(4):
                opp, pct = self.calc_val(board, opp, pct, x, y, j, i)
            if opp == 0:
                if pct == 4:
                    myBlockScore = self.blockwin
                    oppBlockScore = self.blocklose
                    return myBlockScore - oppBlockScore
                myBlockScore = self.calc_blockscore(pct, myBlockScore)
            if pct == 0:
                if opp == 4:
                    myBlockScore = self.blocklose
                    oppBlockScore = self.blockwin
                    return myBlockScore - oppBlockScore
                oppBlockScore = self.calc_blockscore(opp, oppBlockScore)

        for di in self.diamond:
            pct = opp = 0
            for cell in di:
                i = cell[0]
                j = cell[1]
                opp, pct = self.calc_val(board, opp, pct, x, y, i, j)
            if opp == 0:
                if pct == 4:
                    myBlockScore = self.blockwin
                    oppBlockScore = self.blocklose
                    return myBlockScore - oppBlockScore
                myBlockScore = self.calc_blockscore(pct, myBlockScore)
            if pct == 0:
                if opp == 4:
                    myBlockScore = self.blocklose
                    oppBlockScore = self.blockwin
                    return myBlockScore - oppBlockScore
                oppBlockScore = self.calc_blockscore(opp, oppBlockScore)

        totalscore = ((myBlockScore - oppBlockScore) * self.points[x][y])
        return totalscore

    def eval_board_score(self, board):
        myBoardScore = 0
        oppBoardScore = 0

        for i in xrange(4):
            pct = opp = dct = 0
            for j in range(0, 4, 1):
                opp, pct, dct = self.check_val_board(board, opp, pct, dct, i, j)
            if opp == 0 and dct == 0:
                if pct == 4:
                    myBlockScore = self.blockwin
                    oppBlockScore = self.blocklose
                    return myBlockScore - oppBlockScore
                myBoardScore = self.calc_boardscore(pct, myBoardScore)
            elif pct == 0 and dct == 0:
                if opp == 4:
                    myBlockScore = self.blocklose
                    oppBlockScore = self.blockwin
                    return myBlockScore - oppBlockScore
                oppBoardScore = self.calc_boardscore(opp, oppBoardScore)

        for i in xrange(4):
            pct = opp = dct = 0
            for j in xrange(4):
                opp, pct, dct = self.check_val_board(board, opp, pct, dct, j, i)
            if opp == 0 and dct == 0:
                if pct == 4:
                    myBlockScore = self.blockwin
                    oppBlockScore = self.blocklose
                    return myBlockScore - oppBlockScore
                myBoardScore = self.calc_boardscore(pct, myBoardScore)
            elif pct == 0 and dct == 0:
                if opp == 4:
                    myBlockScore = self.blocklose
                    oppBlockScore = self.blockwin
                    return myBlockScore - oppBlockScore
                oppBoardScore = self.calc_boardscore(opp, oppBoardScore)

        for di in self.diamond:
            pct = opp = dct = 0
            for cell in di:
                i = cell[0]
                j = cell[1]
                opp, pct, dct = self.check_val_board(board, opp, pct, dct, i, j)
            if opp == 0 and dct == 0:
                if pct == 4:
                    myBlockScore = self.blockwin
                    oppBlockScore = self.blocklose
                    return myBlockScore - oppBlockScore
                myBoardScore = self.calc_boardscore(pct, myBoardScore)
            elif pct == 0 and dct == 0:
                if opp == 4:
                    myBlockScore = self.blocklose
                    oppBlockScore = self.blockwin
                    return myBlockScore - oppBlockScore
                oppBoardScore = self.calc_boardscore(opp, oppBoardScore)
        totalscore = myBoardScore - oppBoardScore
        return totalscore
