from telethon import TelegramClient, events
from telethon.sessions import StringSession
import random, math, asyncio

api_id = 20008394
api_hash = "44c0df39906e03ff01682b80ddcda4a3"
session_string = "1BZWaqwUAUKk5fB8deRsrC7j1hPNov39lGS81Js-e_BD2XiCFXQDDIOK0tjnR0xhetnZeJL7mOd9LVVf-f_JTeN_q2Ur6mVEnpRBuAiWDMm3GwSTYw8u4uAIfw81uF9BeulWF5GAuB544_Cpmh5iRtexFR3pbll2ufKlIT1KMLLXoNH78wnBjwLyn5IUgNPcGOq_0in4lRTNxbH4--fbIEcm5t5woSj6RR3sXNAXIK_gVxlF6CU4VFRKKS6b_U7ceLiLIjvv0EU3bLF_VGxhBKvdZj00kAjQWrJOCzGz3Vdq369sbgc1QTT3f04t4klcCPSwXc1JdTW6AxQVzshV74P-tlAle_lQ="

client = TelegramClient(StringSession(session_string), api_id, api_hash)

ROWS, COLS = 6, 7
PLAYER, BOT = "🔴", "🟡"
CACHE = {}

TARGET_BOT_ID = 5416991774


def norm(x):
    return "".join(c for c in x if c.isalnum()).lower()


def parse_board(t):
    b=[]
    for l in t.split("\n"):
        if any(x in l for x in ["🔴","🟡","⚪"]):
            b.append(list(l.strip()))
    return b[-6:]


def valid(b):
    return [c for c in range(COLS) if b[0][c]=="⚪"]


def drop(b,c,p):
    nb=[r[:] for r in b]
    for r in range(ROWS-1,-1,-1):
        if nb[r][c]=="⚪":
            nb[r][c]=p
            return nb
    return None


def win(b,p):
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(b[r][c+i]==p for i in range(4)): return True
    for r in range(ROWS-3):
        for c in range(COLS):
            if all(b[r+i][c]==p for i in range(4)): return True
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(b[r+i][c+i]==p for i in range(4)): return True
    for r in range(3,ROWS):
        for c in range(COLS-3):
            if all(b[r-i][c+i]==p for i in range(4)): return True
    return False


def fast(b):
    v=valid(b)
    for c in v:
        if win(drop(b,c,PLAYER),PLAYER): return c
    for c in v:
        if win(drop(b,c,BOT),BOT): return c
    return None


def score(w,p):
    s=0;o=BOT if p==PLAYER else PLAYER
    if w.count(p)==4: s+=100
    elif w.count(p)==3 and w.count("⚪")==1: s+=15
    elif w.count(p)==2 and w.count("⚪")==2: s+=6
    if w.count(o)==3 and w.count("⚪")==1: s-=12
    return s


def evaluate(b,p):
    s=0
    center=[b[r][COLS//2] for r in range(ROWS)]
    s+=center.count(p)*10
    for r in range(ROWS):
        for c in range(COLS-3):
            s+=score(b[r][c:c+4],p)
    for c in range(COLS):
        col=[b[r][c] for r in range(ROWS)]
        for r in range(ROWS-3):
            s+=score(col[r:r+4],p)
    for r in range(ROWS-3):
        for c in range(COLS-3):
            s+=score([b[r+i][c+i] for i in range(4)],p)
    for r in range(3,ROWS):
        for c in range(COLS-3):
            s+=score([b[r-i][c+i] for i in range(4)],p)
    return s


def key(b): return tuple(tuple(r) for r in b)
def order(m): return sorted(m, key=lambda c: abs(3-c))


def minimax(b,d,a,beta,maxi):
    k=(key(b),d,maxi)
    if k in CACHE: return CACHE[k]

    v=valid(b)
    term=win(b,PLAYER) or win(b,BOT) or not v

    if d==0 or term:
        if win(b,PLAYER): return None, 1e9
        if win(b,BOT): return None, -1e9
        return None, evaluate(b,PLAYER)

    v=order(v)

    if maxi:
        val=-math.inf; best=v[0]
        for c in v:
            nb=drop(b,c,PLAYER)
            sc=minimax(nb,d-1,a,beta,False)[1]
            if sc>val: val,best=sc,c
            a=max(a,val)
            if a>=beta: break
    else:
        val=math.inf; best=v[0]
        for c in v:
            nb=drop(b,c,BOT)
            sc=minimax(nb,d-1,a,beta,True)[1]
            if sc<val: val,best=sc,c
            beta=min(beta,val)
            if a>=beta: break

    CACHE[k]=(best,val)
    return best,val


@client.on(events.NewMessage)
@client.on(events.MessageEdited)
async def auto(event):
    if TARGET_BOT_ID and event.sender_id != TARGET_BOT_ID:
        return

    t = event.raw_text or ""

    if "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣" not in t:
        return
    if "WON" in t:
        return

    turn = [l for l in t.split("\n") if "Turn:" in l]
    if not turn:
        return

    me = await client.get_me()
    me_name = norm((me.first_name or "") + (me.last_name or "") + (me.username or ""))

    if me_name not in norm(turn[0]):
        return

    b = parse_board(t)
    if len(b) < 6:
        return

    mv = fast(b)

    if mv is None:
        empties = sum(r.count("⚪") for r in b)
        depth = 7 if empties > 20 else 6
        mv,_ = minimax(b, depth, -math.inf, math.inf, True)

    if mv is None:
        return

    await asyncio.sleep(random.uniform(0.4, 1.0))

    if event.buttons:
        try:
            await event.buttons[0][mv].click()
            return
        except Exception as e:
            print("button click error:", e)

    try:
        await event.click(0, mv)
    except Exception as e:
        print("fallback click error:", e)


client.start()
client.run_until_disconnected()
