import sys
import os

print("--- 1. ПЕРЕВІРКА ПАПОК ---")
cwd = os.getcwd()
print(f"Робоча папка: {cwd}")

paths_to_check = [
    "app",
    "app/__init__.py",
    "app/api",
    "app/api/__init__.py",
    "app/api/v1",
    "app/api/v1/__init__.py"
]

for path in paths_to_check:
    full_path = os.path.join(cwd, path)
    exists = os.path.exists(full_path)
    status = "✅ Є" if exists else "❌ НЕМАЄ"
    print(f"{status}: {path}")

print("\n--- 2. ВМІСТ ПАПКИ app/api/v1 ---")
try:
    files = os.listdir(os.path.join(cwd, "app/api/v1"))
    print(files)
except Exception as e:
    print(f"Помилка читання папки: {e}")

print("\n--- 3. СПРОБА ІМПОРТУ ---")
# Додаємо поточну папку в шляхи пошуку (як це робить uvicorn)
sys.path.insert(0, cwd)

try:
    print("Імпортуємо app.api.v1...")
    import app.api.v1
    print(f"Модуль знайдено! Шлях файлу: {getattr(app.api.v1, '__file__', 'UNKNOWN (Namespace Package?)')}")
    
    print("Шукаємо api_router...")
    from app.api.v1 import api_router
    print("✅ УСПІХ! api_router успішно імпортовано.")
except ImportError as e:
    print(f"❌ ПОМИЛКА ІМПОРТУ: {e}")
except AttributeError as e:
    print(f"❌ ПОМИЛКА АТРИБУТУ (змінна не знайдена): {e}")
except Exception as e:
    print(f"❌ ІНША ПОМИЛКА: {e}")