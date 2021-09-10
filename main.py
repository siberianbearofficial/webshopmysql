from flask import Flask, render_template
import config
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from data import db_session
from data.item import Item
from data.user import User

db_session.global_init("db/shopdb.sqlite")
app = Flask(__name__)
app.config.from_object(config)
# если делаешь регистрацию
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


def render_page(path, **kwargs):
    return render_template(path, **kwargs)


@app.route('/')
def index_page():
    return render_page('index.html', title='Главная страница')


@app.route('/basket')
@login_required
def basket_page():
    return current_user


if __name__ == '__main__':
    app.run(port=8002)
