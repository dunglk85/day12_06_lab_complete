import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting AI Agent in {settings.environment} mode...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
