import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes



#подкл.
logging.basicConfig(level=logging.INFO)



#создат таблицу для того что бы не вылетало при перезапуске бота
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (user_id INTEGER, task TEXT, done INTEGER)''')
conn.commit()




#привет андрей
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я deVISE. Команды:\n/add - добавить задачу\n/view - посмотреть задачи\n/complete - отметить выполненной\n/delete - удалить задачу")




#добовлять команды
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_text = ' '.join(context.args)
    if not task_text:
        await update.message.reply_text("Напиши задачу после команды: /add прибратся дома")
        return
    c.execute("INSERT INTO tasks (user_id, task, done) VALUES (?, ?, 0)", (user_id, task_text))
    conn.commit()
    await update.message.reply_text(f"добавлено: {task_text}")



    
#логика чек листа задач 
async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    c.execute("SELECT rowid, task, done FROM tasks WHERE user_id = ?", (user_id,))
    user_tasks = c.fetchall()
    if not user_tasks:
        await update.message.reply_text(" Нет задач. Добавь через /add")
        return
    text = " Твои задачи:\n"
    for task_id, task_text, done in user_tasks:
        status = "✅" if done else "❌"
        text += f"{task_id}. {status} {task_text}\n"
    await update.message.reply_text(text)





    
#логика выполнения задачи
async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        task_id = int(context.args[0])
        c.execute("UPDATE tasks SET done = 1 WHERE user_id = ? AND rowid = ?", (user_id, task_id))
        conn.commit()
        if c.rowcount > 0:
            await update.message.reply_text(f"поздровляю задача {task_id} выполнена!")
        else:
            await update.message.reply_text(" Задача не найдена")
    except:
        await update.message.reply_text("Использование: /complete 1")




#логика удаления задач
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        task_id = int(context.args[0])
        c.execute("DELETE FROM tasks WHERE user_id = ? AND rowid = ?", (user_id, task_id))
        conn.commit()
        if c.rowcount > 0:
            await update.message.reply_text(f"️ Задача {task_id} удалена!")
        else:
            await update.message.reply_text(" Задача не найдена")
    except:
        await update.message.reply_text("Использование: /delete 1")


        
#код. слова
def main():
    app = Application.builder().token("8433217743:AAHd8WqL2qjJh2l2AhYPysdrh7jE0dncy8c").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("view", view_tasks))
    app.add_handler(CommandHandler("complete", complete_task))
    app.add_handler(CommandHandler("delete", delete_task))
    app.run_polling()

if __name__ == "__main__":
    main()
