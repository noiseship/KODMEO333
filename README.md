# ⌖ GitHub User Finder

**Автор:** Вавилин Матвей

---

## 📝 Описание

GitHub User Finder — десктопное GUI-приложение на Python (Tkinter) для поиска
пользователей GitHub по логину. Позволяет просматривать профили, добавлять
пользователей в избранное и сохранять их в файл `favorites.json`.

**Технологии:** Python 3, Tkinter, GitHub REST API v3, JSON, unittest

---

## 🚀 Установка и запуск

### Требования
- Python 3.7+
- Tkinter (входит в стандартную установку Python)
- Доступ к интернету (для запросов к GitHub API)
- Внешние библиотеки **не нужны**

### Запуск приложения

```bash
# 1. Клонировать репозиторий
git clone https://github.com/noiseship/KODMEO.git
cd KODMEO

# 2. Запустить приложение
python github_user_finder.py

# 3. Запустить тесты
python tests.py
```

---

## 🗂️ Структура проекта

```
KODMEO/
├── github_user_finder.py   # Основное GUI-приложение
├── tests.py                # Модульные тесты (15 тестов)
├── requirements.txt        # Зависимости (стандартная библиотека)
├── .gitignore              # Исключения Git
├── favorites.json          # Избранные пользователи (создаётся автоматически)
└── README.md               # Документация
```

---

## 🌐 Как использовать GitHub API

Приложение использует **GitHub REST API v3** — публичный API без авторизации
(до 60 запросов в час с одного IP).

### Endpoint 1 — Поиск пользователей

```
GET https://api.github.com/search/users?q={username}&per_page=10
```

**Пример запроса в Python:**
```python
import urllib.request, urllib.parse, json

query = "torvalds"
url = f"https://api.github.com/search/users?q={urllib.parse.quote(query)}&per_page=10"
req = urllib.request.Request(url, headers={"User-Agent": "GitHubUserFinder/1.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
users = data["items"]   # список найденных пользователей
```

**Пример ответа:**
```json
{
  "total_count": 1,
  "items": [
    {
      "login": "torvalds",
      "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
      "html_url": "https://github.com/torvalds"
    }
  ]
}
```

### Endpoint 2 — Детали пользователя

```
GET https://api.github.com/users/{login}
```

**Пример:**
```
GET https://api.github.com/users/torvalds
```

**Ключевые поля ответа:**

| Поле           | Тип    | Описание                        |
|----------------|--------|---------------------------------|
| `login`        | string | Имя пользователя                |
| `name`         | string | Полное имя                      |
| `public_repos` | int    | Количество публичных репозиториев |
| `followers`    | int    | Количество подписчиков          |
| `html_url`     | string | Ссылка на профиль               |

> ⚠️ Лимит без токена: **60 запросов/час** с одного IP.

---

## 💾 Формат favorites.json

Избранные пользователи сохраняются локально в `favorites.json`:

```json
[
  {
    "login": "torvalds",
    "name": "Linus Torvalds",
    "public_repos": 8,
    "followers": 230000,
    "html_url": "https://github.com/torvalds"
  },
  {
    "login": "octocat",
    "name": "The Octocat",
    "public_repos": 8,
    "followers": 14000,
    "html_url": "https://github.com/octocat"
  }
]
```

---

## 📖 Примеры использования

### Пример 1: Поиск пользователя
1. Введите имя в поле поиска, например: `torvalds`
2. Нажмите кнопку **Search** или клавишу **Enter**
3. В таблице появятся результаты: логин, имя, репозитории, подписчики

### Пример 2: Открытие профиля
1. Дважды кликните на любой строке в таблице результатов
2. Браузер откроет страницу профиля на GitHub

### Пример 3: Добавление в избранное
1. Кликните на строку пользователя, чтобы выбрать её
2. Нажмите кнопку **★ Add to Favorites**
3. Перейдите на вкладку **★ Favorites** — пользователь сохранён

### Пример 4: Удаление из избранного
1. Перейдите на вкладку **★ Favorites**
2. Выберите пользователя и нажмите **✕ Remove from Favorites**
3. Подтвердите удаление в диалоговом окне

### Пример 5: Валидация
| Действие             | Результат                                  |
|----------------------|--------------------------------------------|
| Пустое поле → Search | Ошибка: «Search field cannot be empty.»    |
| Только пробелы       | Ошибка: «Search field cannot be empty.»    |
| Повторное добавление | Сообщение: «уже в избранном»               |
| Нет интернета        | Диалог: «Cannot connect to GitHub»         |
| Превышен лимит API   | Диалог: «Rate limit exceeded»              |

---

## 🧪 Тесты

```bash
python tests.py
```

### Список тестов (15 штук):

**TestFavoritesStorage — тесты хранилища JSON:**

| Тест    | Тип      | Описание                                        |
|---------|----------|-------------------------------------------------|
| POS-01  | Positive | Сохранение одного пользователя                  |
| POS-02  | Positive | Сохранение нескольких пользователей             |
| POS-03  | Positive | Загрузка пустого списка при отсутствии файла    |
| POS-04  | Positive | Целостность данных после сохранения             |
| POS-05  | Positive | Перезапись избранных                            |
| NEG-01  | Negative | Повреждённый JSON — возвращает []               |
| NEG-02  | Negative | Сохранение пустого списка                       |
| NEG-03  | Negative | Дубликаты в JSON (защита на уровне UI)          |
| NEG-04  | Negative | Файл содержит пустой массив                     |
| NEG-05  | Negative | Файл содержит null                              |
| BND-01  | Boundary | Ровно один пользователь                         |
| BND-02  | Boundary | Пользователь с пустым именем                   |
| BND-03  | Boundary | Пользователь с 0 репозиториев                  |
| BND-04  | Boundary | UTF-8 / Unicode в имени пользователя           |
| BND-05  | Boundary | Удаление одного пользователя из списка          |

**TestSearchValidation — тесты валидации поля поиска:**

| Тест    | Описание                                   |
|---------|--------------------------------------------|
| VAL-01  | Пустая строка → ошибка                    |
| VAL-02  | Только пробелы → ошибка                   |
| VAL-03  | Корректный логин                           |
| VAL-04  | Логин с пробелами по краям — trim          |
| VAL-05  | Один символ — допустимый запрос            |

### Ожидаемый вывод:
```
test_bnd_01_exactly_one_user ... ok
test_bnd_02_user_with_empty_name ... ok
...
Ran 20 tests in 0.XXs
OK
```
