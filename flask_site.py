import os, sqlite3
from flask import Flask, abort, g, redirect, render_template, session, url_for, request, flash
from FDataBase import FDataBase
import pypugjs

# Config
DATABASE = '/tmp/flask_site.db'
DEBUG = True
SECRET_KEY = 'dmhmd3E@#klj//jg(gg&&mmgDD>>)'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flask_site.db')))
# app.config['SECRET_KEY'] = 'dmhmd3E@#klj//jg(gg&&mmgDD>>)'
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
# app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

''' 1 вариант  без БД
menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Первое приложение", "url": "first-app"},
        {"name": "Обратная связь", "url": "contact"},
    ]
'''
# соединение с базой данных
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Создание таблиц базы данных
# через python console -> from flask_site import create_db -> create_db()
# https://www.youtube.com/watch?v=aHWQkbk3xVA&list=PLA0M1Bcd0w8yrxtwgqBvT6OM4HkOU3xYn    8:00
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    # соединение с БД, если оно не установлено
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    # закрываем соединение с БД, если оно установлено
    if hasattr(g, 'link_db'):
        g.link_db.close()

# простой вариант, лучше не делать
'''@app.route("/")
@app.route("/index")
def index():
    return "index"

@app.route("/about")
def about():
    return "<h1>about</h1>"
'''

@app.route("/")
def index():
    db =get_db()
    dbase = FDataBase(db)
    return render_template('index.pug', menu= dbase.getMenu()) # menu=menu

@app.route("/about")
def about():
    print(url_for('about'))
    return render_template('about.pug', title="О сайте", menu=[])

@app.route("/contact", methods=["POST", "GET"])
def contact():
    
    if request.method == "POST":
        print(request.form)
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.pug', title="Обратная связь", menu=[])

@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == "ttt" and request.form['psw'] == "1111":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.pug', title="Авторизация", menu=[])

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.pug', title='Страница не найдена', menu=[]), 404

# переменный url адрес
'''
способы описания URL @app.route("/url/<variable>")
конверторы: int, float, path
@app.route("/url/<path:variable>")
'''
@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"Пользователь: {username}"

# Добавление статьи
@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_post.pug', menu=dbase.getMenu(), title='Добавление статьи')

# END переменный url адрес

# тестовый контекст запроса
'''
для проверки ф-ции url_for


нужно отключить :
    if __name__ == "__main__":
        app.run(debug=True)
'''
# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('about'))
#     print(url_for('profile', username="rrr"))
# End тестовый контекст запроса



if __name__ == "__main__":
    app.run(debug=True)