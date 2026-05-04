#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub User Finder - приложение для поиска пользователей GitHub
Автор: Вавилин Матвей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import urllib.request
import urllib.parse
import urllib.error


FAVORITES_FILE = "favorites.json"


# ── JSON helpers ─────────────────────────────────────────────────────────────

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


# ── GitHub API ────────────────────────────────────────────────────────────────

def search_github_users(query, per_page=10):
    """Поиск пользователей через GitHub REST API v3."""
    encoded = urllib.parse.quote(query)
    url = f"https://api.github.com/search/users?q={encoded}&per_page={per_page}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "GitHubUserFinder/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    return data.get("items", [])


def get_user_details(login):
    """Получить подробности профиля пользователя."""
    url = f"https://api.github.com/users/{urllib.parse.quote(login)}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "GitHubUserFinder/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


# ── Main Application ──────────────────────────────────────────────────────────

class GitHubUserFinderApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GitHub User Finder")
        self.root.geometry("900x620")
        self.root.resizable(True, True)
        self.root.configure(bg="#0d1117")

        self.favorites = load_favorites()
        self.search_results = []

        self._build_styles()
        self._build_ui()
        self._refresh_favorites_list()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background="#0d1117", foreground="#e6edf3",
                        font=("Courier New", 10))
        style.configure("TFrame", background="#0d1117")
        style.configure("TLabel", background="#0d1117", foreground="#e6edf3")
        style.configure("TLabelframe", background="#161b22", foreground="#58a6ff",
                        bordercolor="#30363d", relief="solid")
        style.configure("TLabelframe.Label", background="#161b22",
                        foreground="#58a6ff", font=("Courier New", 10, "bold"))
        style.configure("TEntry", fieldbackground="#161b22", foreground="#e6edf3",
                        insertcolor="#e6edf3", bordercolor="#30363d")
        style.configure("TButton", background="#21262d", foreground="#e6edf3",
                        bordercolor="#30363d", focuscolor="none",
                        font=("Courier New", 10, "bold"))
        style.map("TButton",
                  background=[("active", "#388bfd"), ("pressed", "#1f6feb")],
                  foreground=[("active", "#ffffff")])
        style.configure("Accent.TButton", background="#1f6feb", foreground="#ffffff",
                        font=("Courier New", 10, "bold"))
        style.map("Accent.TButton",
                  background=[("active", "#388bfd"), ("pressed", "#1158c7")])
        style.configure("Treeview", background="#161b22", foreground="#e6edf3",
                        fieldbackground="#161b22", bordercolor="#30363d",
                        rowheight=28, font=("Courier New", 10))
        style.configure("Treeview.Heading", background="#21262d",
                        foreground="#8b949e", font=("Courier New", 10, "bold"))
        style.map("Treeview", background=[("selected", "#1f6feb")])
        style.configure("TNotebook", background="#0d1117", bordercolor="#30363d")
        style.configure("TNotebook.Tab", background="#161b22", foreground="#8b949e",
                        padding=[14, 6], font=("Courier New", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#0d1117")],
                  foreground=[("selected", "#58a6ff")])

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Label(self.root, text="⌖  GitHub User Finder",
                          bg="#0d1117", fg="#58a6ff",
                          font=("Courier New", 18, "bold"))
        header.pack(pady=(18, 4))

        sub = tk.Label(self.root, text="// search · save · explore",
                       bg="#0d1117", fg="#8b949e",
                       font=("Courier New", 9))
        sub.pack(pady=(0, 12))

        # Search frame
        search_frame = ttk.LabelFrame(self.root, text="Search", padding=10)
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 6))

        row = ttk.Frame(search_frame)
        row.pack(fill=tk.X)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(row, textvariable=self.search_var,
                                      font=("Courier New", 11), width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=4)
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        self.search_btn = ttk.Button(row, text="Search",
                                     style="Accent.TButton",
                                     command=self._do_search)
        self.search_btn.pack(side=tk.LEFT)

        self.error_label = tk.Label(search_frame, text="", bg="#161b22",
                                    fg="#f85149",
                                    font=("Courier New", 9))
        self.error_label.pack(anchor=tk.W, pady=(4, 0))

        # Notebook / tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 8))

        # ── Tab 1: Results ────────────────────────────────────────────────────
        results_tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(results_tab, text="  Results  ")

        cols_r = ("login", "name", "repos", "followers", "url")
        self.results_tree = ttk.Treeview(results_tab, columns=cols_r,
                                         show="headings", height=12)
        self._setup_columns(self.results_tree,
                            [("login", "Username", 160),
                             ("name", "Name", 160),
                             ("repos", "Repos", 70),
                             ("followers", "Followers", 90),
                             ("url", "Profile URL", 280)])

        sb_r = ttk.Scrollbar(results_tab, orient=tk.VERTICAL,
                             command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=sb_r.set)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_r.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_tree.bind("<Double-1>", self._on_result_double_click)

        btn_r = ttk.Frame(self.root)
        btn_r.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(btn_r, text="★  Add to Favorites",
                   command=self._add_selected_to_favorites).pack(side=tk.LEFT, padx=5)
        self.status_label = tk.Label(btn_r, text="", bg="#0d1117",
                                     fg="#3fb950", font=("Courier New", 9))
        self.status_label.pack(side=tk.LEFT, padx=10)

        # ── Tab 2: Favorites ──────────────────────────────────────────────────
        fav_tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(fav_tab, text="  ★ Favorites  ")

        cols_f = ("login", "name", "repos", "followers", "url")
        self.fav_tree = ttk.Treeview(fav_tab, columns=cols_f,
                                     show="headings", height=12)
        self._setup_columns(self.fav_tree,
                            [("login", "Username", 160),
                             ("name", "Name", 160),
                             ("repos", "Repos", 70),
                             ("followers", "Followers", 90),
                             ("url", "Profile URL", 280)])

        sb_f = ttk.Scrollbar(fav_tab, orient=tk.VERTICAL,
                             command=self.fav_tree.yview)
        self.fav_tree.configure(yscrollcommand=sb_f.set)
        self.fav_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_f.pack(side=tk.RIGHT, fill=tk.Y)

        btn_f = ttk.Frame(self.root)
        btn_f.pack(fill=tk.X, padx=20, pady=(0, 14))

        ttk.Button(btn_f, text="✕  Remove from Favorites",
                   command=self._remove_selected_favorite).pack(side=tk.LEFT, padx=5)

        self.fav_count_label = tk.Label(btn_f, text="Saved: 0",
                                        bg="#0d1117", fg="#8b949e",
                                        font=("Courier New", 9))
        self.fav_count_label.pack(side=tk.RIGHT, padx=10)

    def _setup_columns(self, tree, cols):
        for cid, heading, width in cols:
            tree.heading(cid, text=heading)
            tree.column(cid, width=width, minwidth=50)

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.error_label.config(text="⚠  Search field cannot be empty.")
            self.search_entry.focus()
            return None
        self.error_label.config(text="")
        return query

    # ── Search ────────────────────────────────────────────────────────────────

    def _do_search(self):
        query = self._validate_search()
        if query is None:
            return

        self.search_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Searching...", fg="#58a6ff")
        self.root.update()

        # Clear old results
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)
        self.search_results = []

        try:
            items = search_github_users(query)
            if not items:
                self.status_label.config(text="No users found.", fg="#8b949e")
                self.search_btn.config(state=tk.NORMAL)
                return

            for item in items:
                try:
                    details = get_user_details(item["login"])
                except Exception:
                    details = item

                user = {
                    "login": details.get("login", ""),
                    "name": details.get("name") or "",
                    "public_repos": details.get("public_repos", "?"),
                    "followers": details.get("followers", "?"),
                    "html_url": details.get("html_url", ""),
                }
                self.search_results.append(user)
                self.results_tree.insert("", tk.END, values=(
                    user["login"],
                    user["name"],
                    user["public_repos"],
                    user["followers"],
                    user["html_url"],
                ))

            count = len(self.search_results)
            self.status_label.config(
                text=f"Found {count} user(s). Double-click to open profile.",
                fg="#3fb950")
            self.notebook.select(0)

        except urllib.error.HTTPError as e:
            if e.code == 403:
                messagebox.showerror("Rate Limit",
                                     "GitHub API rate limit exceeded.\nWait a minute and try again.")
            else:
                messagebox.showerror("API Error", f"HTTP error: {e.code}")
            self.status_label.config(text="", fg="#f85149")

        except urllib.error.URLError:
            messagebox.showerror("Network Error",
                                 "Cannot connect to GitHub.\nCheck your internet connection.")
            self.status_label.config(text="", fg="#f85149")

        finally:
            self.search_btn.config(state=tk.NORMAL)

    # ── Open profile in browser ───────────────────────────────────────────────

    def _on_result_double_click(self, event):
        selected = self.results_tree.selection()
        if not selected:
            return
        values = self.results_tree.item(selected[0])["values"]
        url = values[4]
        if url:
            import webbrowser
            webbrowser.open(url)

    # ── Favorites ─────────────────────────────────────────────────────────────

    def _add_selected_to_favorites(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please select a user from the results list first.")
            return

        values = self.results_tree.item(selected[0])["values"]
        login = values[0]

        if any(f["login"] == login for f in self.favorites):
            self.status_label.config(
                text=f"'{login}' is already in favorites.", fg="#e3b341")
            return

        user = next((u for u in self.search_results if u["login"] == login), None)
        if user:
            self.favorites.append(user)
            save_favorites(self.favorites)
            self._refresh_favorites_list()
            self.status_label.config(
                text=f"★ '{login}' added to favorites!", fg="#3fb950")

    def _remove_selected_favorite(self):
        selected = self.fav_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please select a user from the favorites list.")
            return

        values = self.fav_tree.item(selected[0])["values"]
        login = values[0]

        if messagebox.askyesno("Confirm", f"Remove '{login}' from favorites?"):
            self.favorites = [f for f in self.favorites if f["login"] != login]
            save_favorites(self.favorites)
            self._refresh_favorites_list()

    def _refresh_favorites_list(self):
        for row in self.fav_tree.get_children():
            self.fav_tree.delete(row)
        for user in self.favorites:
            self.fav_tree.insert("", tk.END, values=(
                user.get("login", ""),
                user.get("name", ""),
                user.get("public_repos", ""),
                user.get("followers", ""),
                user.get("html_url", ""),
            ))
        self.fav_count_label.config(text=f"Saved: {len(self.favorites)}")

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("Starting GitHub User Finder...")
    app = GitHubUserFinderApp()
    app.run()
