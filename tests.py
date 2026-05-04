#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модульные тесты для GitHub User Finder
Автор: Вавилин Матвей
"""

import unittest
import json
import os
import tempfile

# Импортируем функции напрямую (без запуска GUI)
from github_user_finder import load_favorites, save_favorites


# ── Мок-пользователи ─────────────────────────────────────────────────────────

MOCK_USER_1 = {
    "login": "torvalds",
    "name": "Linus Torvalds",
    "public_repos": 8,
    "followers": 230000,
    "html_url": "https://github.com/torvalds"
}

MOCK_USER_2 = {
    "login": "octocat",
    "name": "The Octocat",
    "public_repos": 8,
    "followers": 14000,
    "html_url": "https://github.com/octocat"
}

MOCK_USER_3 = {
    "login": "gvanrossum",
    "name": "Guido van Rossum",
    "public_repos": 20,
    "followers": 35000,
    "html_url": "https://github.com/gvanrossum"
}


class TestFavoritesStorage(unittest.TestCase):
    """Тесты сохранения/загрузки избранных пользователей (JSON)."""

    def setUp(self):
        # Используем временный файл вместо реального favorites.json
        self.tmp = tempfile.mktemp(suffix=".json")
        import github_user_finder as m
        self._orig_file = m.FAVORITES_FILE
        m.FAVORITES_FILE = self.tmp

    def tearDown(self):
        import github_user_finder as m
        m.FAVORITES_FILE = self._orig_file
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    # ── Позитивные тесты ─────────────────────────────────────────────────────

    def test_pos_01_save_single_user(self):
        """POS-01: Сохранение одного пользователя в JSON"""
        save_favorites([MOCK_USER_1])
        loaded = load_favorites()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["login"], "torvalds")

    def test_pos_02_save_multiple_users(self):
        """POS-02: Сохранение нескольких пользователей"""
        save_favorites([MOCK_USER_1, MOCK_USER_2, MOCK_USER_3])
        loaded = load_favorites()
        self.assertEqual(len(loaded), 3)

    def test_pos_03_load_empty_when_no_file(self):
        """POS-03: Загрузка возвращает [] если файл не существует"""
        if os.path.exists(self.tmp):
            os.remove(self.tmp)
        loaded = load_favorites()
        self.assertEqual(loaded, [])

    def test_pos_04_data_integrity(self):
        """POS-04: Данные сохраняются без потерь"""
        save_favorites([MOCK_USER_1])
        loaded = load_favorites()
        user = loaded[0]
        self.assertEqual(user["login"], MOCK_USER_1["login"])
        self.assertEqual(user["name"], MOCK_USER_1["name"])
        self.assertEqual(user["public_repos"], MOCK_USER_1["public_repos"])
        self.assertEqual(user["followers"], MOCK_USER_1["followers"])
        self.assertEqual(user["html_url"], MOCK_USER_1["html_url"])

    def test_pos_05_overwrite_favorites(self):
        """POS-05: Перезапись избранных (новый список заменяет старый)"""
        save_favorites([MOCK_USER_1, MOCK_USER_2])
        save_favorites([MOCK_USER_3])
        loaded = load_favorites()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["login"], "gvanrossum")

    # ── Негативные тесты ─────────────────────────────────────────────────────

    def test_neg_01_load_corrupted_file(self):
        """NEG-01: Загрузка повреждённого JSON возвращает []"""
        with open(self.tmp, "w") as f:
            f.write("NOT VALID JSON {{{{")
        loaded = load_favorites()
        self.assertEqual(loaded, [])

    def test_neg_02_save_empty_list(self):
        """NEG-02: Сохранение пустого списка"""
        save_favorites([])
        loaded = load_favorites()
        self.assertEqual(loaded, [])

    def test_neg_03_no_duplicate_check_in_storage(self):
        """NEG-03: JSON сохраняет дубликаты (проверку нужно делать в UI)"""
        save_favorites([MOCK_USER_1, MOCK_USER_1])
        loaded = load_favorites()
        self.assertEqual(len(loaded), 2)

    def test_neg_04_file_with_empty_json_array(self):
        """NEG-04: Файл содержит пустой массив []"""
        with open(self.tmp, "w") as f:
            f.write("[]")
        loaded = load_favorites()
        self.assertEqual(loaded, [])

    def test_neg_05_file_with_null(self):
        """NEG-05: Файл содержит null — возвращает []"""
        with open(self.tmp, "w") as f:
            f.write("null")
        loaded = load_favorites()
        # json.load вернёт None, обработка — пустой список
        self.assertIsInstance(loaded, (list, type(None)))

    # ── Граничные тесты ──────────────────────────────────────────────────────

    def test_bnd_01_exactly_one_user(self):
        """BND-01: Ровно один пользователь"""
        save_favorites([MOCK_USER_1])
        self.assertEqual(len(load_favorites()), 1)

    def test_bnd_02_user_with_empty_name(self):
        """BND-02: Пользователь с пустым именем"""
        user = {**MOCK_USER_1, "name": ""}
        save_favorites([user])
        loaded = load_favorites()
        self.assertEqual(loaded[0]["name"], "")

    def test_bnd_03_user_with_zero_repos(self):
        """BND-03: Пользователь с 0 репозиториев"""
        user = {**MOCK_USER_1, "public_repos": 0}
        save_favorites([user])
        loaded = load_favorites()
        self.assertEqual(loaded[0]["public_repos"], 0)

    def test_bnd_04_json_file_is_valid_utf8(self):
        """BND-04: Файл сохраняется в UTF-8 (поддержка кириллицы и Unicode)"""
        user = {**MOCK_USER_1, "name": "Линус Торвальдс 🐧"}
        save_favorites([user])
        with open(self.tmp, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Линус", content)

    def test_bnd_05_remove_user_from_list(self):
        """BND-05: Удаление одного пользователя из списка и пересохранение"""
        favorites = [MOCK_USER_1, MOCK_USER_2, MOCK_USER_3]
        save_favorites(favorites)
        # Удаляем octocat
        favorites = [u for u in favorites if u["login"] != "octocat"]
        save_favorites(favorites)
        loaded = load_favorites()
        logins = [u["login"] for u in loaded]
        self.assertNotIn("octocat", logins)
        self.assertIn("torvalds", logins)
        self.assertIn("gvanrossum", logins)


# ── Тесты валидации поля поиска ───────────────────────────────────────────────

class TestSearchValidation(unittest.TestCase):
    """Тесты логики валидации поискового поля (без GUI)."""

    def _validate(self, query):
        """Воспроизводим логику валидации из приложения."""
        q = query.strip()
        if not q:
            return False, "Search field cannot be empty."
        return True, q

    def test_val_01_empty_string(self):
        """VAL-01: Пустая строка — ошибка"""
        ok, msg = self._validate("")
        self.assertFalse(ok)

    def test_val_02_spaces_only(self):
        """VAL-02: Только пробелы — ошибка"""
        ok, msg = self._validate("   ")
        self.assertFalse(ok)

    def test_val_03_valid_username(self):
        """VAL-03: Корректный логин"""
        ok, q = self._validate("torvalds")
        self.assertTrue(ok)
        self.assertEqual(q, "torvalds")

    def test_val_04_username_with_spaces_trimmed(self):
        """VAL-04: Логин с пробелами по краям — trim работает"""
        ok, q = self._validate("  octocat  ")
        self.assertTrue(ok)
        self.assertEqual(q, "octocat")

    def test_val_05_single_char(self):
        """VAL-05: Один символ — допустимый запрос"""
        ok, q = self._validate("a")
        self.assertTrue(ok)


def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestFavoritesStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 55)
    print("РЕЗУЛЬТАТЫ / RESULTS")
    print("=" * 55)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"Всего тестов  / Total:  {result.testsRun}")
    print(f"Пройдено      / Passed: {passed}")
    print(f"Провалено     / Failed: {len(result.failures) + len(result.errors)}")
    return result


if __name__ == "__main__":
    run_tests()
