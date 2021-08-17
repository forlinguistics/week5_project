from flask import Flask
from flask import render_template, request, abort, redirect, session
from datetime import datetime
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import *

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
admin = Admin(app)
admin.add_view(ModelView(UserModel, db.session))
admin.add_view(ModelView(CategoryModel, db.session))
admin.add_view(ModelView(OrderModel, db.session))
admin.add_view(ModelView(DishModel, db.session))


@app.route('/')
def main_page():
    cat = db.session.query(CategoryModel).all()
    dish_dict = {}
    for i in cat:
        dishes = db.session.query(DishModel).filter(DishModel.cat_id == i.id)
        dish_dict[i.title] = list(dishes)
    login_mail = session.get('user_mail', '')
    logged = login_mail != ''
    items_num = session.get('items_num', 0)
    items_price = session.get('items_price', 0)
    return render_template('main.html', data=dish_dict, dish_num=items_num, price=items_price, user=login_mail, is_logged = logged)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error_msg = ""  # Пока ошибок нет

    if request.method == "POST":

        # При регистрации у нас два поля
        email = request.form.get("inputEmail")
        password = request.form.get("inputPassword")

        if not email or not password:
            # Не задано как минимум одно из полей
            error_msg = "Не указано имя или пароль"
            return render_template("register.html", error_msg=error_msg)

        # Создаем и сохраняем нового пользователя в БД

        user = UserModel(mail=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template("register.html", error_msg=error_msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        mail = request.form.get("inputEmail")
        password = request.form.get("inputPassword")
        user = UserModel.query.filter_by(mail=mail).first()
        if user and user.password_valid(password):
            session["user_id"] = user.id
            session["user_mail"] = user.mail
            session["user_cart"] = []
            session['items_num'] = 0
            session['items_price'] = 0
            return redirect('/')
        else:
            return render_template("login.html", error_msg="Неверное имя или пароль")
    return render_template("login.html")


@app.route('/logout')
def logout():
    if session.get("user_id"):
        session.pop("user_id")
    return redirect("/login")


@app.route('/addtocart/<int:dish_id>/')
def add(dish_id):
    cart = session.get('user_cart', [])
    cart.append(dish_id)
    session['user_cart'] = cart
    items_num = session.get('items_num', 0)
    items_price = session.get('items_price', 0)
    item = db.session.query(DishModel).get_or_404(dish_id)
    session['items_num'] = items_num + 1
    session['items_price'] = items_price + item.price
    return redirect('/')


@app.route('/cart', methods=["GET", "POST"])
def disp_cart():
    cart_ids = session.get('user_cart', [])
    dish_num = len(cart_ids)
    cart = db.session.query(DishModel).filter(DishModel.id.in_(cart_ids))
    user_id = session.get('user_id', -1)
    user_email = session.get('user_mail', None)
    is_logged = user_id != -1
    f_price = sum([i.price for i in cart])
    if request.method == 'POST':
        order = OrderModel(date=datetime.today().strftime('%d-%m-%Y'), sum_price=f_price, status='ordered',
                           mail=user_email, phone=request.form['phone'], adress=request.form['adress'], user_id=user_id,
                           dishes=list(cart))
        db.session.add(order)
        db.session.commit()
        session['user_cart'] = []
        session['items_num'] = 0
        session['items_price'] = 0
        return render_template('ordered.html')
    return render_template('cart.html', cart=cart, dish_num=dish_num, price=f_price, is_logged=is_logged,
                           user=user_email)


@app.route('/delete/<int:dish_id>/')
def delete(dish_id):
    cart = session.get('user_cart', [])
    cart.remove(dish_id)
    session['user_cart'] = cart
    item = db.session.query(DishModel).get_or_404(dish_id)
    items_num = session.get('items_num', 1)
    items_price = session.get('items_price', item.price)
    session['items_num'] = items_num - 1
    session['items_price'] = items_price - item.price
    return redirect('/cart')


@app.route('/account')
def acc():
    user_id = session.get('user_id', -1)
    orders = db.session.query(OrderModel).filter(OrderModel.user_id == user_id).all()
    return render_template('account.html', orders=orders, dish_num=session.get('items_num', 0),
                           price=session.get('items_price', 0), user=session.get('user_mail', ''),is_logged = user_id !=-1)


if __name__ == '__main__':
    app.run()
