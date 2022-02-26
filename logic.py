import datetime

from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from data import db_session
from data.item import Item
from data.user import User
from data.shop import Shop
from data.order import Order

split_for_basket = '|||'
split_for_basket_btw_items = '--'


def login(login_form):
    # создаём сессию
    session = db_session.create_session()
    # получаем юзера
    user = session.query(User).filter(User.email == login_form.email.data).first()
    # всегда надо закрывать сессии если ты не ники
    session.close()
    # если не нашли юзера
    if not user:
        return "нет такого пользователя"
    elif not user.check_password(login_form.password.data):  # если пароли не сошлись
        return "неверный логин или пароль"
    else:  # всё хорошо логинимся
        login_user(user)
    return "OK"


def register(register_form):
    # создаём сессию
    session = db_session.create_session()
    # создаем юзера
    user = User()
    user.email = register_form.email.data
    user.set_password(register_form.password.data)
    user.name = register_form.name.data
    user.access = 0
    session.add(user)
    session.commit()
    session.close()
    login(register_form)
    return 'OK'


def create_item(name, description, price, count):
    session = db_session.create_session()
    item = Item()
    item.name = name
    item.count = count
    item.price = price
    item.description = description
    session.add(item)
    session.commit()
    session.close()
    return 'OK'


def remove_item(item_id):
    session = db_session.create_session()
    users = session.query(User).all()
    session.close()
    for user in users:
        if user.basket != '' and user.basket is not None:
            if item_id in user.basket.split(split_for_basket):
                remove_item_from_basket_user(item_id, user)
    session = db_session.create_session()
    item = session.query(Item).filter(Item.id == item_id).first()
    session.delete(item)
    session.commit()
    session.close()
    return 'OK'


def get_all_items():
    session = db_session.create_session()
    items = session.query(Item).all()
    session.close()
    items_list = []
    for item in items:
        item_dict = {'id': item.id, 'name': item.name, 'description': item.description, 'count': item.count,
                     'price': item.price}
        items_list.append(item_dict)
    return items_list


def add_item_to_basket(item_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == current_user.email).first()
    if user.basket is not None and user.basket != '':
        new_basket = ''
        flag = False
        for item_in_basket in user.basket.split(split_for_basket):
            item_in_basket_split = item_in_basket.split(split_for_basket_btw_items)
            if item_in_basket_split[0] == item_id:
                item_in_basket_split[1] = str(int(item_in_basket_split[1]) + 1)
                flag = True
            if new_basket != '':
                new_basket += (split_for_basket + item_in_basket_split[0])
                new_basket += (split_for_basket_btw_items + item_in_basket_split[1])
            else:
                new_basket = item_in_basket_split[0] + split_for_basket_btw_items + item_in_basket_split[1]
        if not flag:
            new_basket += (split_for_basket + str(item_id) + split_for_basket_btw_items + '1')
        user.basket = new_basket
    else:
        user.basket = str(item_id) + split_for_basket_btw_items + '1'
    session.commit()
    session.close()
    return 'OK'


def remove_item_from_basket(item_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == current_user.email).first()
    new_basket = ''
    if user.basket is not None and user.basket != '':
        for item_in_basket in user.basket.split(split_for_basket):
            id_in_basket = item_in_basket.split(split_for_basket_btw_items)[0]
            if id_in_basket != item_id:
                if new_basket != '':
                    new_basket += (split_for_basket + str(item_in_basket))
                else:
                    new_basket = str(item_in_basket)
    user.basket = new_basket
    session.commit()
    session.close()
    return 'OK'


def remove_item_from_basket_user(item_id, user_got):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == user_got.email).first()
    new_basket = ''
    if user.basket is not None and user.basket != '':
        for item_in_basket in user.basket.split(split_for_basket):
            id_in_basket = item_in_basket.split(split_for_basket_btw_items)[0]
            if id_in_basket != item_id:
                if new_basket != '':
                    new_basket += (split_for_basket + str(item_in_basket))
                else:
                    new_basket = str(item_in_basket)
    user.basket = new_basket
    session.commit()
    session.close()
    return 'OK'


def get_items_from_basket():
    basket = current_user.basket
    if basket is None:
        session = db_session.create_session()
        user = session.query(User).filter(User.email == current_user.email)
        user.basket = ''
        session.commit()
        session.close()
        basket = ''
    ids = []
    for item in basket.split(split_for_basket):
        ids.append(item.split(split_for_basket_btw_items))
    items_list = []
    if len(ids) > 0:
        all_items = get_all_items()
        for item in all_items:
            if str(item['id']) in ids:
                items_list.append(item)
    return items_list


def is_admin():
    return current_user.access == 1


def create_admin(username):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == username).first()
    user.access = 1
    session.commit()
    session.close()


def get_item(item_id):
    session = db_session.create_session()
    item = session.query(Item).filter(Item.id == item_id).first()
    session.close()
    return item


def get_about_text():
    session = db_session.create_session()
    shop = session.query(Shop).first()
    if shop is None:
        shop = Shop()
        shop.about = 'Not configured'
        session.add(shop)
        session.commit()
    about_text = shop.about if shop.about is not None else ''
    session.close()
    return about_text


def set_about_text(about_text):
    session = db_session.create_session()
    shop = session.query(Shop).first()
    if shop is None:
        shop = Shop()
        shop.about = about_text
        session.add(shop)
    else:
        shop.about = about_text
    session.commit()
    session.close()
    return 'OK'


def create_order(name, middle_name, surname, birthday):
    order = Order()
    order.name = name
    order.middle_name = middle_name
    order.surname = surname
    birthday_list = birthday.split('-')
    order.birthday = datetime.datetime(int(birthday_list[0]), int(birthday_list[1]), int(birthday_list[2]))
    order.email = current_user.email
    order.status = 0
    order.items = current_user.basket
    session = db_session.create_session()
    session.add(order)
    session.commit()
    session.close()
    return 'OK'


def get_all_orders():
    session = db_session.create_session()
    orders = session.query(Order).all()
    session.close()
    return orders if orders is not None else []


def get_order(order_id):
    session = db_session.create_session()
    order = session.query(Order).filter(Order.id == order_id).first()
    session.close()
    return order


def get_items_from_order(order):
    item_ids = order.items.split(split_for_basket)
    session = db_session.create_session()
    item_list = []
    for item_id in item_ids:
        item_list.append(session.query(Item).filter(Item.id == item_id).first())
    return item_list


def change_order_status(order_id, status):
    session = db_session.create_session()
    order = session.query(Order).filter(Order.id == order_id).first()
    order.status = status
    session.commit()
    session.close()
    return 'OK'
