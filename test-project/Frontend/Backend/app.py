from flask import Flask , request, make_response, jsonify,session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Shopping,Product,User,Order,Comment
from flask_cors import CORS
import statistics
import jwt
from werkzeug.exceptions import NotFound
import datetime
from functools import wraps
import paypalrestsdk
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'A\xd0\xe3\x9b\xef\x90\xb7\x15\x82\xd6\x99\xe6'
migrate = Migrate(app , db)
db.init_app(app)
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": "Adf1GO83Qh22D-T938DQj9_d7KF-nUTNK5n8bhSkRVZEP1rTDX6mM_BoIxHzreGzuUEhv1ZmkyIN4aPq",
    "client_secret": "EKs4oRBe0fFWfM5Lka11-LGGxfIYjV2o5_kv4LdDJV7nNxsnEQl_icjf20qx_z6qVdD099XrQekNudDY"
})
 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({"message": "Token is missing"})
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({"message": "token is missing or invalid"}),406
        return f(*args, **kwargs)
    return decorated    
@app.route('/')
def home():
    return 'E-shop data API'

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        token = jwt.encode({
            'user': data['email'],
            'exp': str(datetime.datetime.utcnow() + datetime.timedelta(hours=2))
        }, app.config['SECRET_KEY'])
        session['user_id'] = user.id
        session['role'] = user.role
        return jsonify({
            "token": token,
            "user":User.query.filter_by(email=email).first().to_dict()
        }),200
    else:
        return jsonify(message="Invalid email or password"), 401  

@app.route('/users', methods = ['GET'])
@token_required
def get_users():
    if request.method == 'GET':       
        users=[user.to_dict() for user in User.query.all()]      
  
        return jsonify(users) , 200

@app.route('/products', methods=['GET', 'POST'])
def get_all_products():
    if request.method == 'GET':          
        return make_response(
            jsonify([product.to_dict() for product in Product.query.order_by(Product.price).all()]),
            200
        )
    elif request.method == 'POST':
         data = request.get_json()
         new_product = Product(name=data['name'],
                               image_url = data['image_url'], 
                               price = data['price'], 
                               quantity = data['quantity'], 
                               category = data['category'], 
                               description =data['description'], 
                               specs = data['specs'],
                               user_id = data['user_id'],
                            )
         db.session.add(new_product)
         db.session.commit()
         return make_response(
             jsonify({"message":"successfully added"}),
             200
         )
    
@app.route('/comments', methods = ["POST", "GET"])
def get_all_comments():
    if request.method == "GET":
        all_comments = [comment.to_dict() for comment in Comment.query.all()]       
        response = make_response(
            jsonify(all_comments),
            200
        )
        return response
    elif request.method == "POST":
        data = request.get_json()
        user = User.query.filter_by(id=data['user_id']).first()
        product = Product.query.filter_by(id = data['product_id']).first()
        new_comment = Comment(
            commenter =  f'{user.first_name} {user.second_name}',
            comment = data['comment'],
            rating = data['rating'],
            product_name =  product.name,
            user_id = data['user_id'],
            product_id = data['product_id']        
        )
        db.session.add(new_comment)
        db.session.commit()
        return make_response(
            jsonify({"message": "Added successfully"}),
            200
        )
@app.route('/user/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@token_required
def get_one_user(id):
    if request.method == 'GET':
        user = User.query.filter_by(id =id).first()
        return make_response(
            jsonify(user.to_dict()),
            200
        )
    elif request.method == 'DELETE':
        user = User.query.filter_by(id =id).first()
        db.session.delete(user)
        db.session.commit()
        return make_response(
            jsonify({"message":"deleted successfully"}),
            200
        )
    elif request.method == 'PATCH':
        user = User.query.filter_by(id =id).first()
        data = request.get_json()      

        for attr in data:
            setattr(user, attr, data.get(attr))
        db.session.add(user)
        db.session.commit()
        user_dict = user.to_dict()
        response = make_response(
            jsonify(user_dict),
            200
        )
        return response
    
@app.route('/product/<int:id>', methods =["GET","PATCH","DELETE"])
@token_required
def get_specific_product(id):
    if request.method == "GET":
        return make_response(
            jsonify(Product.query.filter_by(id = id).first().to_dict()),
            200
        )
    elif request.method == "DELETE": 
        db.session.delete(Product.query.filter_by(id=id).first() )
        db.session.commit()
        return make_response(
            jsonify({"message":"Deleted successfully"}),
            200
        )
    
    elif request.method == 'PATCH':
        data = request.get_json()
        product = Product.query.filter_by(id=id).first()    

        for attr in data:
            setattr(product, attr, data.get(attr))
        db.session.add(product)
        db.session.commit()
        product_dict = product.to_dict()
        response = make_response(
            jsonify(product_dict),
            200
        )
        return response
    
@app.route("/comment/<int:id>", methods =["DELETE", "GET"])
@token_required 
def certain_comment(id):
    if request.method == "GET":
        return make_response(
            jsonify(Comment.query.filter_by(id=id).first().to_dict()),
            200
        )
    elif request.method == "DELETE":    
        db.session.delete(Comment.query.filter_by(id=id).first())
        db.session.commit()
        return make_response(
            jsonify({"message":"Delete successfully"}),
            200
        )
@app.route("/comments/<int:user_id>")
@token_required 
def get_according_user(user_id):
    products_id = [product.id for product in Product.query.filter_by(user_id = user_id).all()] 
    all_comments = []
    i = 0
    while i < len(products_id):
        comments = Comment.query.all()
        for comment in comments:
            if comment.product_id == products_id[i]:
                all_comments.append({
                    "id": comment.id,
                    "customer_name": comment.commenter,
                    "comment":comment.comment,
                    "rating": comment.rating,
                    "product_name": comment.product_name,
                    "created_at": comment.created_at,
                    "user_id": comment.user_id,
                    "product_id":comment.product_id
                    })
        i+= 1
       
    return make_response(
        jsonify(all_comments),
        200
    )

@app.route("/orders", methods = ["GET", "POST"])
@token_required
def get_all_orders():
    if request.method == "GET":
        return make_response(
            jsonify([order.to_dict() for order in Order.query.all()])
        )
    elif request.method == "POST":
        data = request.get_json()
        product = Product.query.filter_by(id = data['product_id']).first()
        user = User.query.filter_by(id = data['user_id']).first()

        new_order = Order(
            product_name = product.name,
            payment_method = data['payment_method'],
            customer_name =  f"{user.first_name} {user.second_name}",
            status = data['status'],
            quantity = data['quantity'],
            total_amount = data['quantity']* product.price,
            product_id = data['product_id'],
            user_id = data['user_id']
        )
        db.session.add(new_order)
        db.session.commit()

        return make_response(
            jsonify({"message":"Order added successfully"}),
            200
        )
    
@app.route("/order/<int:id>", methods = ["GET", "PATCH", "DELETE"])
@token_required
def get_an_order(id):
    if request.method == "GET":
        return make_response(
            jsonify([Order.query.filter_by(id = id).first().to_dict()]),
            200
        )
    elif request.method == "PATCH":
        data = request.get_json()
        order = Order.query.filter_by(id=id).first()    

        for attr in data:
            setattr(order, attr, data.get(attr))
        db.session.add(order)
        db.session.commit()
        product_dict = order.to_dict()
        response = make_response(
            jsonify(product_dict),
            200
        )
        return response
    elif request.method == "DELETE":
        db.session.delete(Order.query.filter_by(id=id).first()) 
        db.session.commit()
        return make_response(
            jsonify({"message": "Deleted successfully"})
        )

@app.route('/shopping', methods = ["GET", "POST"])
@token_required
def getting_shopping_cart():
    if request.method == "GET":
        return make_response(
            jsonify([shop.to_dict() for shop in Shopping.query.all()]),
            200            
        )
    elif request.method == "POST":
        data = request.get_json()
        product = Product.query.filter_by(id=data['product_id']).first()
        new_item = Shopping(
            product_name = product.name,
            quantity = data['quantity'],
            price = product.price,
            product_id = data['product_id'],
            user_id =data['user_id']
        )
        db.session.add(new_item)
        db.session.commit()
        return make_response(
            jsonify({"message":"Added successfuly"}),
            200
        )

@app.route('/shopping/<int:id>', methods = ["GET", "PATCH","DELETE"])
@token_required
def get_one_shopping(id):
    if request.method == "GET":
        return make_response(
            jsonify(Shopping.query.filter_by(id=id).first().to_dict()),
            200
        )
    elif request.method == "DELETE":
        db.session.delete(Shopping.query.filter_by(id=id).first())
        db.session.commit() 
        return make_response(
            jsonify({"messsage":"Deleted successfully"}),
            200
        )
    elif request.method == "PATCH":
        data = request.get_json()
        item = Shopping.query.filter_by(id=id).first()    

        for attr in data:
            setattr(item, attr, data.get(attr))
        db.session.add(item)
        db.session.commit()        
        response = make_response(
            jsonify(item.to_dict()),
            200
        )
        return response  

@app.route('/admin/<int:id>')
@token_required
def get_dashboard_details(id):
    user = User.query.filter_by(id=id).first()
    products = Product.query.filter_by(user_id=id).all()
    number_of_products = 0
    orders = 0
    ratings =[]
    for product in products:
        number_of_products += 1
        for comment in Comment.query.filter_by(product_id=product.id).all():
            ratings.append(comment.rating)
        for order in Order.query.filter_by(product_id=product.id).all():
            orders += 1    
    return make_response(
       jsonify(
        {
            "full_name": f"{user.first_name} {user.second_name}",
            "shop_id": f"SHOP00{user.id}",
            "products": number_of_products,
            "rating": statistics.mean(ratings),
            "orders": orders
        }
        ),
        200
    )

@app.route('/signup', methods=["POST"])
def handle_signup():
    data =request.get_json()
    new_user = User(
        first_name = data['first_name'],
        second_name = data['second_name'],
        email = data['email'],
        phone_number = data['phone_number'],
        address =data['address'],
        password = data['password'],
        role = data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return make_response(
        jsonify({"message":"added succesfully"}),
        200
    )

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: The requested resource does not exist.",
        404
    )

    return response   

@app.route('/create-paypal-order', methods=['POST'])
def create_paypal_order():
    try:
        data = request.get_json()

        # Validate input data
        if not data or not isinstance(data, dict) or "cart" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        cart = data["cart"]
        if not isinstance(cart, list):
            return jsonify({"error": "Invalid cart data"}), 400

        total_amount = 0
        items = []

        for item in cart:
            product_id = item.get("id")
            quantity = item.get("quantity")

            order_item = Order.query.get(product_id)  # Use the Order class
            if order_item is None:
                return jsonify({"error": f"Product with ID {product_id} not found"}), 404

            product_name = order_item.product_name
            product_price = order_item.total_amount

            if not quantity or quantity <= 0:
                return jsonify({"error": "Invalid product data"}), 400

            item_total = product_price * quantity
            total_amount += item_total

            items.append({
                "name": product_name,
                "price": product_price,
                "currency": "USD",
                "quantity": quantity
            })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "item_list": {
                    "items": items
                },
                "amount": {
                    "total": total_amount,
                    "currency": "USD"
                },
                "description": "Your order description"
            }]
        })

        if payment.create():
            return jsonify({"id": payment.id})
        else:
            return jsonify({"error": payment.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def capture_order(order_id):
    capture = Capture.find(order_id)
    if capture:
        return {
            "product_name": capture.transaction_item_list[0].name,
            "customer_name": capture.payer_info.email,
            "status": capture.state,
            "quantity": capture.transaction_item_list[0].quantity,
            "amount": capture.transaction_amount.value,
            "currency": capture.transaction_amount.currency,
            "product_id": capture.transaction_item_list[0].sku,
            "user_id": 1  # Replace with the actual user ID based on your logic
        }
    return None

def create_new_order(data, payment_method):
    captured_order_data = capture_order(data["orderID"])
    if captured_order_data:
        new_order = Order(
            product_name=captured_order_data["product_name"],
            payment_method=payment_method,
            customer_name=captured_order_data["customer_name"],
            status=captured_order_data["status"],
            quantity=captured_order_data["quantity"],
            total_amount=captured_order_data["amount"],
            product_id=captured_order_data["product_id"],
            user_id=captured_order_data["user_id"]
        )
        db.session.add(new_order)
        db.session.commit()
        return captured_order_data
    return None

@app.route('/capture-paypal-order', methods=['POST'])
def capture_paypal_order():
    try:
        data = request.get_json()

        if not data or "orderID" not in data or "payment_method" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        payment_method = data["payment_method"]

        captured_order_data = create_new_order(data, payment_method)
        if captured_order_data:
            return jsonify(captured_order_data), 200
        else:
            return jsonify({"error": "Failed to capture PayPal order"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-shopping-cart', methods=['GET'])
def get_shopping_cart():
    try:
        # Fetch shopping cart data from your database
        shopping_cart_data = Shopping.query.all()

        # Convert shopping cart data to a list of dictionaries
        shopping_cart = []
        for item in shopping_cart_data:
            shopping_cart.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
            })

        return jsonify(shopping_cart), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)