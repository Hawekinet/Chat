# LAN Internal Chat (Flutter + FastAPI)

Приложение внутреннего чата для локальной сети с:
- отправкой текстов, изображений, видео и файлов;
- хранением истории переписки в SQLite;
- созданием локальных учетных записей администратором;
- разделением прав (admin/user);
- развёртыванием сервера внутри LAN.

## Архитектура
- `server/` — FastAPI backend + SQLite + загрузка файлов.
- `client/` — Flutter-клиент для пользователей и администраторов.

## Запуск backend (локальный сервер)
```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

По умолчанию создаётся админ:
- login: `admin`
- password: `admin123`

## Запуск Flutter клиента
1. Откройте `client/lib/main.dart` и укажите IP локального сервера в `baseUrl`.
2. Запуск:
```bash
cd client
flutter pub get
flutter run
```

## API (основное)
- `POST /auth/token` — авторизация.
- `GET /messages` — чтение истории сообщений.
- `POST /messages` — отправка текста/медиа/файлов.
- `POST /admin/users` — создание пользователей (только admin).

---

## Новый проект: Local AI Analyst (RAG на Streamlit + Ollama)

Добавлен отдельный проект в папке `ai_analyst/`:
- `app.py` — веб-интерфейс аналитика с загрузкой PDF/DOCX и чатом по документам.
- `requirements.txt` — зависимости Python.
- `DEPLOYMENT.md` — детальная пошаговая инструкция по развертыванию и запуску.

Быстрый старт:
```bash
cd ai_analyst
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3
streamlit run app.py
```
