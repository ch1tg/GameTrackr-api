# run.py
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from a2wsgi import WSGIMiddleware

flask_app = create_app()
app = WSGIMiddleware(flask_app)

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        log_level="info",
        reload=True
    )