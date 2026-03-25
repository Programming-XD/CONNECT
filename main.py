from pyrogram import Client, filters
import random
import math
import asyncio

api_id = 20008394
api_hash = "44c0df39906e03ff01682b80ddcda4a3"
session_string = "BQFHY-cAJu3TTTq3jqctLdhAI__Q0lDEm7q-XTiPRB1ZCwuzpASy_kgx6RihNiD2vidk_puN6FtB3MSHjHaNpHRYR9KZnnBScDzjHMynpWAKD9A_TOHKcRBqxlIehclTMPHpiUEl05KSxrzPvk35q7w9FEkakbjbN3m6iZ-3P43iJpBeUOxk70Kb1mdA7o6hEDK9jsEepm4W8Nh-7h0Z4RQtdtEEulMFVrDuIopukHPLSqI9CSf4XPhJWmL-wW-qpgHBwoU--vMgTp-5XIPlyh8oIKTJWYgXrPC418-7sFvWOh2UH7pilPWW2y2E_Rg45GnxwjBwE9CMuKFM0vuIcCmtW9YNDAAAAAGLVDWlAA"

app = Client("userbot", api_id=api_id, api_hash=api_hash, session_string=session_string)

ROWS = 6
COLS = 7
PLAYER = "🔴"
BOT = "🟡"

ACTIVE_CHATS = set()

def parse_board(text):
    lines = text.split("\n")
    board = []
    for line in lines:
        if any(x in line for x in ["🔴","🟡","⚪"]):
            board.append(list(line.strip()))
    return board

def valid_moves(board):
    return [c for c in range(COLS) if board[0][c] == "⚪"]

def drop(board, col, piece):
    temp = [row[:] for row in board]
    for r in range(ROWS-1, -1, -1):
        if temp[r][col] == "⚪":
            temp[r][col] = piece
            return temp
    return None

def win(board, piece):
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    for r in range(ROWS-3):
        for c in range(COLS):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False

def score_window(window, piece):
    score = 0
    opp = BOT if piece == PLAYER else PLAYER
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count("⚪") == 1:
        score += 10
    elif window.count(piece) == 2 and window.count("⚪") == 2:
        score += 4
    if window.count(opp) == 3 and window.count("⚪") == 1:
        score -= 8
    return score

def evaluate(board, piece):
    score = 0
    center = [board[r][COLS//2] for r in range(ROWS)]
    score += center.count(piece) * 6

    for r in range(ROWS):
        row = board[r]
        for c in range(COLS-3):
            score += score_window(row[c:c+4], piece)

    for c in range(COLS):
        col = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS-3):
            score += score_window(col[r:r+4], piece)

    for r in range(ROWS-3):
        for c in range(COLS-3):
            score += score_window([board[r+i][c+i] for i in range(4)], piece)

    for r in range(3, ROWS):
        for c in range(COLS-3):
            score += score_window([board[r-i][c+i] for i in range(4)], piece)

    return score

def order_moves(board, moves):
    return sorted(moves, key=lambda c: abs(3-c))

def minimax(board, depth, alpha, beta, maximizing):
    valid = valid_moves(board)
    terminal = win(board, PLAYER) or win(board, BOT) or len(valid) == 0

    if depth == 0 or terminal:
        if win(board, PLAYER):
            return None, 1000000
        elif win(board, BOT):
            return None, -1000000
        return None, evaluate(board, PLAYER)

    valid = order_moves(board, valid)

    if maximizing:
        value = -math.inf
        best = valid[0]
        for col in valid:
            new_board = drop(board, col, PLAYER)
            score = minimax(new_board, depth-1, alpha, beta, False)[1]
            if score > value:
                value = score
                best = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best, value
    else:
        value = math.inf
        best = valid[0]
        for col in valid:
            new_board = drop(board, col, BOT)
            score = minimax(new_board, depth-1, alpha, beta, True)[1]
            if score < value:
                value = score
                best = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best, value

@app.on_message(filters.command("auto_on"))
async def enable(_, m):
    ACTIVE_CHATS.add(m.chat.id)
    await m.reply("AUTO ON")

@app.on_message(filters.command("auto_off"))
async def disable(_, m):
    ACTIVE_CHATS.discard(m.chat.id)
    await m.reply("AUTO OFF")

@app.on_message(filters.text)
async def auto(client, message):
    if message.chat.id not in ACTIVE_CHATS:
        return

    text = message.text or ""

    if "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣" not in text:
        return

    if "WON" in text:
        return

    me = await client.get_me()

    if me.first_name not in text and (me.username and me.username not in text):
        return

    board = parse_board(text)

    if len(board) != 6:
        return

    col, _ = minimax(board, 6, -math.inf, math.inf, True)

    if col is None:
        return

    await asyncio.sleep(random.uniform(1,2.5))

    try:
        await message.click(col)
    except:
        pass

app.run()
