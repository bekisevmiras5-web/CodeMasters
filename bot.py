import os, sqlite3, time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

t = os.getenv("TOKEN") or input("TOKEN: 8433217743:AAHd8WqL2qjJh2l2AhYPysdrh7jE0dncy8c").strip()
b = Bot(token = 8433217743:AAHd8WqL2qjJh2l2AhYPysdrh7jE0dncy8c)
d = Dispatcher(b)

db = sqlite3.connect("study.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, txt TEXT, done INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS stats(uid INTEGER, day INTEGER, cnt INTEGER)")
db.commit()

def add(u,txt):
    cur.execute("INSERT INTO tasks(uid,txt,done) VALUES(?,?,0)", (u,txt))
    db.commit()

def ls(u):
    return cur.execute("SELECT id,txt,done FROM tasks WHERE uid=? ORDER BY id", (u,)).fetchall()

def mark(u,i):
    cur.execute("UPDATE tasks SET done=1 WHERE uid=? AND id=?", (u,i))
    db.commit()

def clear(u):
    cur.execute("DELETE FROM tasks WHERE uid=?", (u,))
    db.commit()

def inc(u):
    d0 = int(time.time()//86400)
    r = cur.execute("SELECT cnt FROM stats WHERE uid=? AND day=?", (u,d0)).fetchone()
    if r:
        cur.execute("UPDATE stats SET cnt=cnt+1 WHERE uid=? AND day=?", (u,d0))
    else:
        cur.execute("INSERT INTO stats(uid,day,cnt) VALUES(?,?,1)", (u,d0))
    db.commit()

def getcnt(u):
    d0 = int(time.time()//86400)
    r = cur.execute("SELECT cnt FROM stats WHERE uid=? AND day=?", (u,d0)).fetchone()
    return r[0] if r else 0

@d.message_handler(commands=["start"])
async def f(m: types.Message):
    await m.reply("StudyTracker. /add текст | /list | /done id | /clear | /stats")

@d.message_handler(commands=["add"])
async def f1(m: types.Message):
    u = m.from_user.id
    txt = m.text.replace("/add","",1).strip()
    if not txt:
        await m.reply("Напиши задачу после /add")
        return
    add(u, txt)
    await m.reply("Добавлено")

@d.message_handler(commands=["list"])
async def f2(m: types.Message):
    u = m.from_user.id
    r = ls(u)
    if not r:
        await m.reply("Список пуст")
        return
    lines = []
    for row in r:
        s = "✅" if row[2] else "❌"
        lines.append(f"{row[0]}. {row[1]} {s}")
    await m.reply("\n".join(lines))

@d.message_handler(commands=["done"])
async def f3(m: types.Message):
    u = m.from_user.id
    try:
        i = int(m.text.split()[1])
    except:
        await m.reply("Использование: /done <id>")
        return
    mark(u,i)
    inc(u)
    await m.reply("Отмечено")

@d.message_handler(commands=["clear"])
async def f4(m: types.Message):
    u = m.from_user.id
    clear(u)
    await m.reply("Очищено")

@d.message_handler(commands=["stats"])
async def f5(m: types.Message):
    u = m.from_user.id
    n = getcnt(u)
    await m.reply(f"Сегодня выполнено: {n}")

if __name__ == "__main__":
    executor.start_polling(d, skip_updates=True)

