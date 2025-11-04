
import os
from dotenv import load_dotenv


load_dotenv()


from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        debug=True,  # Включить режим отладки (автоперезагрузка)
        host="0.0.0.0", # Слушать на всех IP (чтобы Docker мог подключиться)
        port=int(os.environ.get("PORT", 5000)) # Берем порт из .env или 5000
    )