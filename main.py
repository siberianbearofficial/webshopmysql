from flask import Flask, render_template, request, redirect
import config
from data.forms import *
from logic import *


db_session.global_init("db/shopdb.sqlite")
app = Flask(__name__)
app.config.from_object(config)
# если делаешь регистрацию
login_manager = LoginManager()
login_manager.init_app(app)


not_logged_in = '$dnfjwnij&yegrhbhjh^2wygrjhbvhj^tgyirgihbhkbk)gdhfvhjvhgvGUCTY%@cgvfgjvuaghdbkqf'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


def render_page(path, **kwargs):
    name = current_user.name if not current_user.is_anonymous else not_logged_in
    return render_template(path, name=name, **kwargs)


@app.route('/')
def index_page():
    if current_user.is_anonymous:
        return redirect('/login')
    return render_page('index.html', title='Главная', items=get_all_items())


@app.route('/logout')
def logout_page():
    if not current_user.is_anonymous:
        logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if request.method == 'POST' and form.submit.data:
        print(login(form))  # пришёл положительный ответ с формы
        return redirect('/')
    elif request.method == 'POST' and form.cancel.data:
        return redirect('/')  # отмена действия
    return render_page('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if request.method == 'POST' and form.submit.data:
        error = register(form)  # пришёл положительный ответ с формы
        if error == 'OK':
            return redirect('/')
    elif request.method == 'POST' and form.cancel.data:
        return redirect('/')  # отмена действия
    return render_page('register.html', title='Регистрация', form=form)


@app.route('/create')
@login_required
def create_item_page():
    if is_admin():
        name = request.args['name']
        description = request.args['description']
        price = int(request.args['price'])
        count = int(request.args['count'])
        print(create_item(name, description, price, count))
        return redirect('/admin')
    return redirect('/')


@app.route('/remove')
@login_required
def remove_item_page():
    if is_admin():
        print(remove_item(request.args['item_id']))
        return redirect('/admin')
    return redirect('/')


@app.route('/get_all_items')
def get_all_items_page():
    print(get_all_items())
    return redirect('/')


@app.route('/basket')
@login_required
def basket_page():
    return render_page('basket.html', items=get_items_from_basket(), title='Корзина')


@app.route('/about')
def about_page():
    return render_page('about.html', content=get_about_text(), title='О нас')


@app.route('/order', methods=['GET', 'POST'])
def order_page():
    if request.method == 'GET':
        return redirect('/')
    else:
        name = request.form['name']
        middle_name = request.form['middlename']
        surname = request.form['surname']
        birthday = request.form['birthday']
        print(create_order(name, middle_name, surname, birthday))
        # Заказ создали, а теперь неплохо бы деньги получить с человека :)
        # Но пока я не написал метод для создания заказа, здесь будет просто редирект на главную страницу
        return redirect('/')


@app.route('/change_about')
@login_required
def change_about_page():
    if is_admin():
        print(set_about_text(request.args['about']))
        return redirect('/admin')
    return redirect('/')


@app.route('/get_about_text')
def get_about_text_page():
    return get_about_text()


@app.route('/add_item_to_basket/<int:item_id>')
def add_item_to_basket_page(item_id):
    print(add_item_to_basket(item_id))
    return redirect('/')


@app.route('/admin')
@login_required
def admin_page():
    if not is_admin():
        return redirect('/')
    return render_page('admin.html', content=get_about_text(), title='Панель администратора')


@app.route('/create_admin')
@login_required
def create_admin_page():
    if is_admin():
        username = request.args['username']
        create_admin(username)
        return redirect('/admin')
    return redirect('/')


@app.route('/admincode')
@login_required
def make_myself_admin():
    if request.args['sc'] == config.SECRET_KEY:
        create_admin(current_user.email)
        return redirect('/admin')
    return redirect('/')


@app.route('/item_description/<int:item_id>')
def item_description_page(item_id):
    item = get_item(item_id)
    if item is None:
        return redirect('/')
    return render_page('item_description.html', item=item, title=item['name'] + ' - описание')


@app.route('/order_details/<int:order_id>')
@login_required
def order_details_page(order_id):
    if is_admin():
        order = get_order(order_id)
        if order is None:
            return redirect('/')
        items = get_items_from_order(order)
        return render_page('order_details.html', order=order, title='Заказ ' + str(order.id), items=items)
    else:
        return redirect('/')


@app.route('/all_orders')
@login_required
def all_orders_page():
    if not is_admin():
        return redirect('/')
    return render_page('orders.html', orders=get_all_orders(), title='Все заказы')


if __name__ == '__main__':
    app.run(port=8002)
