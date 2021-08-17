from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    orders = db.relationship("OrderModel", back_populates="user")

    @property
    def password(self):
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        # Проверяем пароль через этот метод
        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
        return check_password_hash(self.password_hash, password)


orders_dishes_association = db.Table('users_chats',
                                     db.Column('order_id', db.Integer, db.ForeignKey('orders.id')),
                                     db.Column('dish_id', db.Integer, db.ForeignKey('dishes.id'))
                                     )


class DishModel(db.Model):
    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    price = db.Column(db.Integer)
    description = db.Column(db.String())
    picture = db.Column(db.String())
    category = db.relationship('CategoryModel', back_populates="dishes")
    cat_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    orders = db.relationship("OrderModel", secondary=orders_dishes_association, back_populates="dishes")


class CategoryModel(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    dishes = db.relationship("DishModel", back_populates="category")


class OrderModel(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String())
    sum_price = db.Column(db.Integer)
    status = db.Column(db.String())
    mail = db.Column(db.String())
    phone = db.Column(db.String())
    adress = db.Column(db.String())
    dishes = db.relationship('DishModel', secondary=orders_dishes_association, back_populates='orders')
    user = db.relationship('UserModel', back_populates="orders")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
