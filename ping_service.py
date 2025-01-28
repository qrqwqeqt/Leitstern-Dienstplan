import requests
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ping_service():
    url = "https://your-render-app-url.onrender.com/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"Service pinged successfully at {datetime.utcnow()}")
        else:
            logger.warning(f"Service returned status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error pinging service: {str(e)}")

def main():
    while True:
        ping_service()
        # Пингуем каждые 10 минут
        time.sleep(600)

if __name__ == "__main__":
    main()