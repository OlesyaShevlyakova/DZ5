from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import *
from json import dumps
from db_alchemy import *
from utils import read_secret_key

app = Flask(__name__)


@app.route('/')
def index():
    """
    Главная форма отображения активов
    """
    if 'username' in session: # проверка, что есть сессия для пользователя
        conn = get_db_connection()
        assets = conn.execute("SELECT * FROM assets where id_user='%s'" % session['id_user']).fetchall()
        conn.close()
        return render_template('index.html', assets=assets, current_user=session['username'])
    else: # если сессии нет, то перекидываем на страницу логина
        return redirect(url_for('login_form'))



@app.route('/<int:asset_id>', methods=['GET', 'POST'])
def get_asset(asset_id):
    """
    Возвращаем информацию об конкретном активе
    """
    if request.method == 'GET':  # Если получение информации, то из базы берем актив
        conn = get_db_connection()
        asset = conn.execute('SELECT * FROM assets WHERE id = ? and id_user = ?',
                             (asset_id, session['id_user'])).fetchone()
        conn.close()
        return render_template('asset.html', asset=asset)
    elif request.method == 'POST':  # Удаляем выбранный актив
        conn = get_db_connection()
        conn.execute('DELETE FROM assets WHERE id = ? and id_user = ?',
                     (asset_id,session['id_user']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    if not session.modified:
        session.modified = True
    return redirect(url_for('login_form'))


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    """
    Обработка формы логина и регистрации
    В request.form['submit_button'] прописывается была попытка логина или регистрации
    """
    # Если пришел метод пост и нажата кнопка логина, то делаем авторизацию
    if request.method == 'POST' and request.form['submit_button'] == 'login':
        # Получаем с формы все входящие параметры
        login = request.form['login_name']
        password = request.form['login_psw']
        # поставил пользователь галочку запомнить его или нет
        if 'remember' in request.form:
            permanent = True
        else:
            permanent = False

        session.permanent = permanent # настройка перманентности сессии

        is_user_exist, id_user = check_user(login, password) # проверяем есть ли в БД запрашиваемый логин\пароль
        if not is_user_exist:  # не нашли пользователя, обновляем форму и выводим сообщение что не нашли логин\пароль
            return render_template(
                'login_form.html',
                msg_err="Пользователь и пароль не совпадают или не существуют"
            )
        else:  # удачная авторизация, записываем в сессию его логин
            session['username'] = login
            session['id_user'] = id_user
            return redirect(url_for('index'))
    # Если пришел метод пост и нажата кнопка регистрации, то делаем регистрацию
    elif request.method == 'POST' and request.form['submit_button'] == 'reg':
        login = request.form['reg_name']
        password = request.form['reg_psw']
        success, msg = reg_user(login, password)
        if not success:  # не удалось добавить пользователя
            return render_template('login_form.html', msg_err=msg)
        else:  # удалось добавить пользователя
            return render_template('login_form.html', msg_err=msg)
    else:  # к нам пришел не Post метод, значит просто страницу ему отображаем
        return render_template('login_form.html', msg_err="")


@app.route('/new', methods=['GET', 'POST'])
def new_asset():
    """Добавляем новый актив"""
    if request.method == 'POST':  # Если пришел метод пост, то надо добавить новый актив и вернуть на первую страницу
        assetselect = request.form['AssetSelect']
        amount = request.form['amount']
        mothpick = request.form['monthpick']
        # вызываем фукнция добавления актива
        add_asset(assetselect, amount, mothpick, session['id_user'])
        return redirect(url_for('index'))
    return render_template('add_asset.html')


@app.route("/request_assets", methods=["FETCH"])
def request_assets():
    """Запрос активов по выбранной дате"""
    asset_date = request.json['date']
    conn = get_db_connection()
    requested_assets: sqlite3.Row = conn.execute('SELECT * FROM assets WHERE date = ? and id_user = ?',
                                                 (asset_date, session['id_user'])).fetchall()
    conn.close()
    requested_assets = [tuple(asset) for asset in requested_assets]
    requested_assets = dumps(requested_assets)
    return {'data': requested_assets}  # Заносим в словарь, так как на pythonanywhere ошибки, что мы возвращаем list



if __name__ == '__main__':
    # Читаем секрет из файла
    err, resp = read_secret_key()
    if err:
        exit(resp)
    else:
        secret_key = resp
    app.secret_key = secret_key
    app.config["SESSION_PERMANENT"] = False

    with app.app_context():
        #init_db() # создаем таблицы на чистом SQL подходе
        init_db_alch() # создаем таблицы на SQLAclhemy подходе
    app.run(debug=True)
