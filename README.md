# 🎙️ GoyidaTimeBot

**Created by: bochkagq**

## 🇷🇺 Русский (Russian)

Этот бот отслеживает время, проведенное пользователями в голосовых каналах, и ведет статистику за **день**, **месяц** и **все время**. Он включает в себя динамические таблицы лидеров (лидерборды), которые обновляются автоматически.

### ✨ Особенности

* 📊 Раздельная статистика (День / Месяц / Все время).
* 🔄 Автоматическое обновление лидербордов каждые 5 минут.
* ⚡ Команда принудительного обновления для администраторов.
* 🗄️ Асинхронная база данных SQLite (aiosqlite).
* 🛡️ Безопасное хранение токена через `.env`.

---

### 🚀 Инструкция по установке

#### 1. Подготовка (Windows & Linux)

Сначала склонируйте репозиторий или скачайте файлы бота в отдельную папку. Создайте файл `.env` в корневой папке и вставьте туда ваш токен:

```env
BOT_TOKEN=ВАШ_ТОКЕН_ЗДЕСЬ

```

#### 2. Создание виртуального окружения и установка

Виртуальное окружение (Venv) нужно, чтобы библиотеки бота не конфликтовали с другими проектами.

**Для Windows:**

1. Откройте терминал (PowerShell или CMD) в папке проекта.
2. Создайте окружение: `python -m venv venv`
3. Активируйте: `.\venv\Scripts\activate`
4. Установите библиотеки: `pip install discord.py aiosqlite python-dotenv`

**Для Linux:**

1. Откройте терминал.
2. Создайте окружение: `python3 -m venv venv`
3. Активируйте: `source venv/bin/activate`
4. Установите библиотеки: `pip install discord.py aiosqlite python-dotenv`

#### 3. Запуск

* **Windows:** `python main.py`
* **Linux:** `python3 main.py`

---

## 🇺🇸 English

This bot tracks the time users spend in voice channels and maintains statistics for **Day**, **Month**, and **All Time**. It features dynamic leaderboards that update automatically.

### ✨ Features

* 📊 Separate statistics (Daily / Monthly / Total).
* 🔄 Automatic leaderboard updates every 5 minutes.
* ⚡ Manual update command for administrators.
* 🗄️ Asynchronous SQLite database (aiosqlite).
* 🛡️ Secure token storage via `.env`.

---

### 🚀 Installation Guide

#### 1. Preparation (Windows & Linux)

Clone the repository or download the bot files. Create a `.env` file in the root folder and insert your token:

```env
BOT_TOKEN=YOUR_TOKEN_HERE

```

#### 2. Virtual Environment & Installation

A Virtual Environment (Venv) is recommended to keep dependencies isolated.

**For Windows:**

1. Open terminal (PowerShell or CMD) in the project folder.
2. Create environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\activate`
4. Install libraries: `pip install discord.py aiosqlite python-dotenv`

**For Linux:**

1. Open terminal.
2. Create environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install libraries: `pip install discord.py aiosqlite python-dotenv`

#### 3. Running the Bot

* **Windows:** `python main.py`
* **Linux:** `python3 main.py`

---

### 🛠️ Commands / Команды

| Command | Description / Описание |
| --- | --- |
| `!stats_day` | Personal stats for today / Личная статистика за день |
| `!stats_month` | Personal stats for this month / Статистика за месяц |
| `!stats_alltime` | Total personal stats / Статистика за все время |
| `!init_leaderboard_day` | Admin: Setup daily leaderboard / Создать топ за день |
| `!init_leaderboard_month` | Admin: Setup monthly leaderboard / Создать топ за месяц |
| `!init_leaderboard_alltime` | Admin: Setup an all time leaderboard / Создать топ за все время |
| `!update_now` | Admin: Force data sync / Принудительно обновить топы |
| `!ignore` | Admin: Ignore a person on the leaderboard / Игнорировать человека в таблице лидеров |

---

**Developed by bochkagq**

---
