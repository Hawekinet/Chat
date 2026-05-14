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

## Отдельное Windows-приложение: прыгающая картошка
Файл: `bouncing_potato_app.py`

Что делает:
- запускает окно с анимацией прыгающей картошки;
- при клике на картошку создаются ещё **две** картошки;
- закрытие приложения — горячей клавишей **Shift + Y**.

Запуск:
```bash
python bouncing_potato_app.py
```


### Как собрать `.exe` (Windows)
Самый простой способ — через **PyInstaller**.

1) Установите Python 3.10+ и откройте `cmd`/PowerShell в папке проекта.
2) (Рекомендуется) создайте виртуальное окружение:
```bash
python -m venv .venv
.venv\Scripts\activate
```
3) Установите PyInstaller:
```bash
pip install pyinstaller
```
4) Соберите один исполняемый файл:
```bash
pyinstaller --onefile --windowed --name BouncingPotato bouncing_potato_app.py
```
5) Готовый файл будет здесь:
- `dist/BouncingPotato.exe`

Если хотите добавить свою иконку:
```bash
pyinstaller --onefile --windowed --name BouncingPotato --icon potato.ico bouncing_potato_app.py
```
