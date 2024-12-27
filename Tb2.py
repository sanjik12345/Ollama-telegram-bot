import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import ollama


# Создание или подключение к базе данных
def setup_database():
    conn = sqlite3.connect("user_data.db")  # Создаёт файл базы данных, если его нет
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            user_question TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# Функция для сохранения сообщения в базу данных
def save_to_database(user_name, user_question):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_name, user_question) VALUES (?, ?)", (user_name, user_question))
    conn.commit()
    conn.close()


# Функция для получения ответа от вашей модели через Ollama
def get_model_response(user_question: str):
    # Подключение к Ollama с вашей моделью (синхронный вызов)
    response = ollama.chat(model="english_teacher", messages=[{"role": "user", "content": user_question}])

    # Печатаем весь ответ для отладки
    print(response)

    # Извлекаем текст из поля content
    if 'message' in response and 'content' in response['message']:
        return response['message']['content']
    else:
        return "Ответ от модели не найден."


# Функция, которая будет отвечать на все текстовые сообщения
async def answer_question(update: Update, context):
    user_message = update.message.text
    user_name = update.effective_user.first_name  # Получаем имя пользователя

    # Печатаем имя пользователя и его вопрос в консоль
    print(f"Пользователь: {user_name}, Вопрос: {user_message}")
    await update.message.reply_text('Подожди 15 секунд')
    # Сохраняем данные в базу данных
    save_to_database(user_name, user_message)

    # Получаем ответ от вашей модели через Ollama
    model_response = get_model_response(user_message)

    # Отправляем ответ обратно пользователю
    await update.message.reply_text(model_response)


# Функция, которая будет срабатывать на команду /start
async def start(update: Update, context):
    # Приветственное сообщение
    await update.message.reply_text("Привет! Я S.A.R.A ИИ Ассистент Санжара.")


# Основная функция
def main():
    # Настройка базы данных
    setup_database()

    # Ваш API токен, полученный от BotFather
    TOKEN = "Your api key tg"

    # Создаем объект приложения с использованием токена
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики для команд и сообщений
    app.add_handler(CommandHandler("start", start))  # Обработчик для команды /start
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question))  # Обработчик для всех текстовых сообщений

    # Печатаем сообщение о запуске бота
    print("Бот запущен. Нажмите Ctrl+C для остановки.")

    # Запускаем polling, чтобы бот начал получать обновления
    app.run_polling()


# Эта строка обеспечивает запуск main() при выполнении скрипта
if __name__ == "__main__":
    main()
