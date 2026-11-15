import sqlite3
from typing import Optional
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Donate Shop")

ADMIN_ID = 8800181441


def init_db():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            product_title TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)
  # Добавим демо-товары, если таблица пустая
  cursor.execute("SELECT COUNT(*) FROM products")
  if cursor.fetchone()[0] == 0:
    sample_products = [
        ("Telegram Stars (100)", "Stars", "15000 сум", "⭐"),
        ("Telegram Premium (1 мес)", "Premium", "45000 сум", "💎"),
        ("Robux (400)", "Robux", "55000 сум", "🎮"),
        ("Standoff 2 Gold (500)", "Standoff 2", "40000 сум", "🪙"),
    ]
    cursor.executemany(
        "INSERT INTO products (title, category, price, image) VALUES (?, ?, ?,"
        " ?)",
        sample_products,
    )
  conn.commit()
  conn.close()


init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
  conn = sqlite3.connect("database.db")
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM products")
  products = cursor.fetchall()
  conn.close()

  html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Donate Shop</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background: #0f0b1e; color: #fff; font-family: sans-serif; margin: 0; padding: 15px; }
            h1 { text-align: center; color: #b19cd9; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
            .card { background: #1a1429; border: 1px solid #3d2c5e; border-radius: 12px; padding: 15px; text-align: center; }
            .btn { background: #7b2cbf; color: white; border: none; padding: 8px 12px; border-radius: 8px; cursor: pointer; margin-top: 10px; width: 100%; font-weight: bold; }
            .btn:active { background: #9d4edd; }
            .admin-link { display: block; text-align: center; margin-top: 20px; color: #9d4edd; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>💎 Donate Shop</h1>
        <div class="grid">
    """
  for p in products:
    html_content += f"""
            <div class="card">
                <div style="font-size: 30px;">{p['image']}</div>
                <h3>{p['title']}</h3>
                <p style="color: #b19cd9;">{p['price']}</p>
                <button class="btn" onclick="alert('Заказ товара {p['title']} оформлен!')">Купить</button>
            </div>
        """

  html_content += """
        </div>
        <a href="/admin" class="admin-link">⚙️ Панель администратора</a>
    </body>
    </html>
    """
  return HTMLResponse(content=html_content)


@app.get("/admin", response_class=HTMLResponse)
def admin_panel():
  conn = sqlite3.connect("database.db")
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM products")
  products = cursor.fetchall()
  conn.close()

  html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Admin Panel</title>
        <style>
            body { background: #0f0b1e; color: #fff; font-family: sans-serif; padding: 20px; }
            input, button { padding: 10px; margin: 5px 0; width: 100%; border-radius: 6px; border: 1px solid #3d2c5e; background: #1a1429; color: #fff; }
            button { background: #7b2cbf; font-weight: bold; cursor: pointer; }
            ul { padding: 0; list-style: none; }
            li { background: #1a1429; margin-bottom: 8px; padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; }
        </style>
    </head>
    <body>
        <h2>⚙️ Панель администратора</h2>
        <form action="/admin/add" method="post">
            <input type="text" name="title" placeholder="Название товара" required>
            <input type="text" name="category" placeholder="Категория" required>
            <input type="text" name="price" placeholder="Цена" required>
            <input type="text" name="image" placeholder="Эмодзи или иконка" required>
            <button type="submit">Добавить товар</button>
        </form>
        <h3>Существующие товары:</h3>
        <ul>
    """
  for p in products:
    html += f"<li><span>{p['image']} {p['title']} - {p['price']}</span></li>"

  html += """
        </ul>
        <a href="/" style="color: #b19cd9;">⬅️ На главную</a>
    </body>
    </html>
    """
  return HTMLResponse(content=html)


@app.post("/admin/add")
def add_product(
    title: str = Form(...),
    category: str = Form(...),
    price: str = Form(...),
    image: str = Form(...),
):
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO products (title, category, price, image) VALUES (?, ?, ?, ?)",
      (title, category, price, image),
  )
  conn.commit()
  conn.close()
  return RedirectResponse(url="/admin", status_code=303)
