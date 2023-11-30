from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1111@localhost:3306/kiosk'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy()
db.init_app(app)

class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullfilled = db.Column(db.String(50))
    order_date = db.Column(db.Date)  # You can add more fields as needed

    # Establish a one-to-many relationship with OrderProduct
    order_products = db.relationship('OrderProduct', backref='order', lazy=True)

class OrderProduct(db.Model):
    __tablename__ = 'orderproduct'

    order_product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

def transform_row_to_result(row):
    result = []
    current_order_id = None
    order_products = {}
    for item in row:
        order_id, product_name, quantity = item
        if order_id != current_order_id:
            if current_order_id is not None:
                result.append((current_order_id, order_products))
            current_order_id = order_id
            order_products = {}
        order_products[product_name] = quantity
    if current_order_id is not None:
        result.append((current_order_id, order_products))
    return result

@app.route('/', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        # return render_template('test.html', form_data=request.form.items())
        if all(int(value) == 0 for _, value in request.form.items()):
           flash('주문하실 음료의 수를 넣어주세요')
           return redirect(url_for('order'))
        order_check=[]
        for key, value in request.form.items():
            if int(value) > 0:
                stock_left = db.session.query(Product).filter(Product.product_name==key).all()
                print(stock_left)
                if stock_left[0].stock < int(value):
                    order_check.append(stock_left[0].product_name)
        if len(order_check) > 0:
            flash(f'{order_check}는 재고를 확인 해주세요')
            return redirect(url_for('order'))
        order=Order(fullfilled="False", order_date=datetime.now())
        db.session.add(order)
        db.session.commit()
        order_confirm = []
        for key, value in request.form.items():
            if int(value) > 0:
                temp = db.session.query(Product).filter(Product.product_name==key).all()
                prod_key = int(temp[0].product_id)
                ordered_items = OrderProduct(order_id=order.order_id, product_id=prod_key, quantity=value)
                db.session.add(ordered_items)
                product_update = Product.query.get_or_404(prod_key)
                product_update.stock = product_update.stock - int(value)
                db.session.commit()
                order_confirm.append(f'{key} : {value} 잔')
        print(order_confirm)
        return render_template('ordered.html', order_confirm=order_confirm)

    # GET render
    stock_left = db.session.query(Product).all()
    return render_template('order.html', stock_left=stock_left)

@app.route('/todo', methods=['GET', 'POST'])
def ordertodo():
    if request.method == 'POST':
        order_number = request.form.get('order_id')
        order = Order.query.get(order_number)
        if order:
            order.fullfilled = "True"
            db.session.commit()
    
    # Create the SQLAlchemy query
    query = db.session.query(
        Order.order_id,
        Product.product_name,
        OrderProduct.quantity
    ).select_from(Order) \
    .join(OrderProduct, Order.order_id == OrderProduct.order_id) \
    .join(Product, OrderProduct.product_id == Product.product_id) \
    .filter(Order.fullfilled == "False") \
    .order_by(Order.order_id, Product.product_id)

    # Execute the query and fetch results
    result = query.all()
    
    order_set = transform_row_to_result(result)
        
    # Render the template and pass the results
    return render_template('order_summary.html', order_set=order_set)
    
@app.route('/cancel', methods=['POST'])
def cancel_order():
    order_number = request.form.get('order_id')
    order = Order.query.get(order_number)
    if order:
        query = db.session.query(OrderProduct.product_id, OrderProduct.quantity).filter(OrderProduct.order_id == order_number)
        results = query.all()
        print(results)
        for prodcut, q in results:
            product = Product.query.get(prodcut)
            product.stock += q
        order.fullfilled = "Cancel"
        db.session.commit()
    return redirect(url_for('ordertodo'))