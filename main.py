from flask import Flask, render_template, request, redirect, url_for
from database import *
from json import dumps

app = Flask(__name__)

@app.route('/')
def index():
    """Отображаем все активы из БД"""
    conn = get_db_connection()
    assets = conn.execute('SELECT * FROM assets').fetchall()
    conn.close()
    return render_template('index.html', assets=assets)


@app.route('/<int:asset_id>', methods=['GET', 'POST'])
def get_asset(asset_id):

    if request.method != 'POST':  # Возвращаем информацию об конкретном активе
        conn = get_db_connection()
        asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
        conn.close()
        return render_template('asset.html', asset=asset)
    elif request.method == 'POST':  # Удаляем выбранный актив
        conn = get_db_connection()
        conn.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))


@app.route('/new', methods=['GET', 'POST'])
def new_asset():
    """Добавляем новый актив"""
    if request.method == 'POST':  # Если пришел метод пост, то надо добавить новый актив и вернуть на первую страницу
        assetselect = request.form['AssetSelect']
        amount = request.form['amount']
        mothpick = request.form['monthpick']
        conn = get_db_connection()
        conn.execute('INSERT INTO assets (name, amount, date) VALUES (?, ?, ?)', (assetselect, amount, mothpick))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_asset.html')


@app.route("/request_assets", methods=["FETCH"])
def request_assets():
    """Запрос активов по выбранной дате"""
    asset_date = request.json['date']
    conn = get_db_connection()
    requested_assets: sqlite3.Row = conn.execute('SELECT * FROM assets WHERE date = ?', (asset_date,)).fetchall()
    conn.close()
    requested_assets = [tuple(asset) for asset in requested_assets]
    requested_assets = dumps(requested_assets)
    return {'data': requested_assets}  # Заносим в словарь, так как на pythonanywhere ошибки, что мы возвращаем list


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=False)
