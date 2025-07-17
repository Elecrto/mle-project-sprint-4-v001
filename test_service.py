import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="new_api_test.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

def log_response(resp):
    if resp.status_code == 200:
        logging.info(f"Response: {resp.json()}")
        return resp.json()
    else:
        logging.error(f"Error {resp.status_code}: {resp.text}")
        return None

# Базовый URL API
BASE_URL = "http://127.0.0.1:8000"

# Тест 1: Получение рекомендаций для существующего пользователя
logging.info("=== TEST 1: Get suggestions for existing user ===")
response = requests.post(
    f"{BASE_URL}/suggestions", 
    params={"user_id": 47, "limit": 5}
)
result = log_response(response)
print("Test 1 Results:", result)

# Тест 2: Получение рекомендаций для несуществующего пользователя
logging.info("\n=== TEST 2: Get suggestions for unknown user ===")
response = requests.post(
    f"{BASE_URL}/suggestions", 
    params={"user_id": 6666666, "limit": 3}
)
result = log_response(response)
print("Test 2 Results:", result)

# Тест 3: Обновление кэша рекомендаций
logging.info("\n=== TEST 3: Refresh recommendations cache ===")
response = requests.get(
    f"{BASE_URL}/refresh_suggestions", 
    params={"rec_type": "general"}
)
print("Refresh status:", response.status_code)

# Тест 4: Получение метрик системы
logging.info("\n=== TEST 4: Get system metrics ===")
response = requests.get(f"{BASE_URL}/system_metrics")
metrics = log_response(response)
print("System Metrics:", metrics)

# Тест 5: Логирование действий пользователя
logging.info("\n=== TEST 5: Log user actions ===")
for i, track_id in enumerate([679699, 630670, 646516, 19152669, 38646012]):
    response = requests.post(
        f"{BASE_URL}/log_action", 
        params={"user_id": 69, "item_id": track_id}
    )
    print(f"Logged action {i+1}: {response.status_code}")

# Тест 6: Получение истории действий
logging.info("\n=== TEST 6: Get user history ===")
response = requests.post(
    f"{BASE_URL}/user_actions", 
    params={"user_id": 69, "count": 10}
)
history = log_response(response)
print("User History:", history)

# Тест 7: Генерация онлайн-рекомендаций
logging.info("\n=== TEST 7: Generate real-time suggestions ===")
response = requests.post(
    f"{BASE_URL}/realtime_suggestions", 
    params={"user_id": 69, "limit": 5}
)
online_recs = log_response(response)
print("Online Recommendations:", online_recs)

# Тест 8: Комбинированные рекомендации
logging.info("\n=== TEST 8: Get combined suggestions ===")
response = requests.post(
    f"{BASE_URL}/suggestions", 
    params={"user_id": 69, "limit": 10}
)
combined_recs = log_response(response)
print("Combined Recommendations:", combined_recs)