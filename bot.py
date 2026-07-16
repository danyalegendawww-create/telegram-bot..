import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router
from database import db


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("🚀 Запуск бота...")
    
    # Инициализация БД
    await db.init_db()
    logging.info("✅ База данных инициализирована")
    
    # Инициализация бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    # Инициализация диспетчера с хранилищем
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем роутеры
    dp.include_router(router)
    
    # Запуск бота
    try:
        logging.info("✅ Бот успешно запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        raise
    finally:
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"❌ Непредвиденная ошибка: {e}")
        sys.exit(1)
