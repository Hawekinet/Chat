# Развертывание Local AI Analyst (Streamlit + Ollama)

## 1) Требования
- ОС: Linux/macOS/Windows (WSL тоже подходит).
- Python 3.10+.
- Установленный Ollama.
- Минимум 8 ГБ RAM (рекомендуется 16+ ГБ для стабильной работы `llama3`).

## 2) Подготовка окружения
```bash
cd ai_analyst
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Установка и запуск Ollama
1. Установите Ollama: https://ollama.com/download
2. Скачайте модель:
```bash
ollama pull llama3
```
3. Убедитесь, что сервис доступен:
```bash
ollama list
```

## 4) Первый запуск приложения
```bash
cd ai_analyst
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

После запуска откройте:
- локально: `http://localhost:8501`
- в LAN: `http://<IP_сервера>:8501`

## 5) Использование
1. Нажмите **"Выберите файлы Word или PDF"**.
2. Загрузите `.pdf` и/или `.docx`.
3. Нажмите **"Проанализировать и обучиться"**.
4. Введите вопрос в чат.

## 6) Хранение данных
- Векторная база сохраняется в `ai_analyst/vector_db_ui`.
- Если нужно «сбросить память» ИИ по документам, удалите эту папку и перезапустите приложение.

## 7) Production-вариант через systemd (Linux)
Создайте сервис `/etc/systemd/system/local-ai-analyst.service`:

```ini
[Unit]
Description=Local AI Analyst Streamlit App
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/opt/local-ai-analyst/ai_analyst
Environment="PATH=/opt/local-ai-analyst/ai_analyst/.venv/bin"
ExecStart=/opt/local-ai-analyst/ai_analyst/.venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable local-ai-analyst
sudo systemctl start local-ai-analyst
sudo systemctl status local-ai-analyst
```

## 8) Типичные проблемы и решения
- `Connection refused to Ollama`: проверьте, что Ollama запущен и модель скачана.
- Медленные ответы: уменьшите `num_ctx` в `ChatOllama` или используйте более лёгкую модель.
- Пустые ответы: заново загрузите документы, убедитесь, что документы содержат текстовый слой.
