from flask import Blueprint, render_template, flash, request, jsonify, get_flashed_messages
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from .import db
import json
from django.shortcuts import render
from django.db.models import Q
from management.models import Product, Detail, Cart, Warehouse, TotalOrder, Order, User
from urllib.parse import quote
from urllib.parse import quote_plus
from urllib.parse import unquote_plus
from flask_login import user_logged_in
from flask import session
from werkzeug.utils import secure_filename
from flask import session, redirect, url_for
views = Blueprint("views", __name__)

# Kiểm tra đăng nhập
def isLoggedIn():
    return current_user.is_authenticated
# Trang chủ
@views.route("/home", methods=["GET","POST"])
@views.route("/", methods=["GET","POST"])
@login_required
def home(): 
    men_products = []
    women_products = []
    products = Product.query.all()
    for product in products:
        details = Detail.query.filter_by(product_id=product.product_id).all()
        
        for detail in details:
            if detail.type_product == 'Nam_':
                men_products.append((product, detail.type_product))
            elif detail.type_product == 'Nữ_':
                women_products.append((product, detail.type_product))
    first_images = [get_first_image(product.image) for product, _ in men_products]
    first_images += [get_first_image(product.image) for product, _ in women_products]
    messages = get_flashed_messages()
    total_quantity = session.get('total_quantity', 0)
    return render_template("index/index.html",total_quantity=total_quantity,men_products=men_products, women_products=women_products,first_images=first_images, user=current_user if current_user.is_authenticated else None)
def get_first_image(image):
    if image:
        image_list = image.split(';')
        return image_list[0]
    return None


# Nam
@views.route("/male_page", methods=["GET","POST"])
@login_required
def male_page():
    total_quantity = session.get('total_quantity', 0)
    return render_template('male/male_page.html')
@views.route("/shoemale_page", methods=["GET","POST"])
def shoemale_page():
    total_quantity = session.get('total_quantity', 0)
    return render_template('male/shoemale_page.html')
@views.route("/fashion_male", methods=["GET","POST"])
def fashion_male():
    men_products = []
    women_products = []
    products = Product.query.all()
    for product in products:
        details = Detail.query.filter_by(product_id=product.product_id).all()
        for detail in details:
            if detail.type_product == 'Nam_' or detail.type_product == 'Nam':
                men_products.append((product,detail.type_product))
            elif detail.type_product == 'Nữ_' or detail.type_product == 'Nữ':
                women_products.append((product, detail.type_product))
    total_quantity = session.get('total_quantity', 0)
    return render_template('male/fashion_male.html',men_products=men_products,women_products=women_products)


# Nữ
@views.route("/female_page", methods=["GET","POST"])
def female_page():
    total_quantity = session.get('total_quantity', 0)
    return render_template('female/female_page.html')
@views.route("/shoefemale_page", methods=["GET","POST"])
def shoefemale_page():
    total_quantity = session.get('total_quantity', 0)
    return render_template('female/shoefemale_page.html') 
@views.route("/fashion_female", methods=["GET","POST"])
def fashion_female():
    total_quantity = session.get('total_quantity', 0)
    return render_template('female/fashion_female.html')


# Trẻ em
@views.route("/kid_page", methods=["GET","POST"])
def kid_page():
    total_quantity = session.get('total_quantity', 0)
    return render_template('kid/kid_page.html')
@views.route("/shoekid_page", methods=["GET","POST"])
def shoekid_page():
    total_quantity = session.get('total_quantity', 0)
    return render_template('kid/shoekid_page.html')
    # Thời trang trẻ em
@views.route("/fashion_kid", methods=["GET","POST"])
def fashion_kid():
    total_quantity = session.get('total_quantity', 0)
    return render_template('kid/fashion_kid.html')


# Infomation
@views.route('/infomation/<string:name_product>')
def infomation(name_product):
    decoded_name_product = unquote_plus(name_product)
    product = Product.query.filter_by(name_product=decoded_name_product).first()
    if product:
        detail = Detail.query.filter_by(product_id=product.product_id).first()
        detail.describe = detail.describe.replace('\n','<br>')
        detail.extend = detail.extend.replace('\n','<br>')
        colors = detail.color_product.split(';')
        sizes = detail.size_product.split(';')
        describes = detail.describe.split(';')
        extends = detail.extend.split(';')
        images = product.image.split(';')
        other_products_Nam = Product.query.filter(Product.product_id != product.product_id, Product.product_id <= 12).limit(100).all()
        other_products_Nu = Product.query.filter(Product.product_id != product.product_id, Product.product_id > 12, Product.product_id <= 22).limit(100).all()
        return render_template('info/info.html', product=product, detail=detail, colors=colors, sizes=sizes, describes=describes, extends=extends, images=images,other_products_Nam=other_products_Nam,other_products_Nu=other_products_Nu)
    else:
        return name_product
    total_quantity = session.get('total_quantity', 0)

# Cart
def create_cart_for_user(user):
    # Kiểm tra xem người dùng đã có giỏ hàng chưa bằng cách kiểm tra user_id trong bảng Cart
    cart = Cart.query.filter_by(user_id=user.user_id).first()
    if not cart:
        cart = Cart(user_id=user.user_id)
        db.session.add(cart)
        db.session.commit()

@views.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Sản phẩm không tồn tại"}), 404

    # Kiểm tra và tạo giỏ hàng cho người dùng nếu cần
    create_cart_for_user(current_user)

    # Lấy giỏ hàng của người dùng
    cart = Cart.query.filter_by(user_id=current_user.user_id).first()

    # Tách chuỗi ảnh thành một danh sách các ảnh
    image_list = product.image.split(';')

    # Lấy ảnh đầu tiên từ danh sách
    first_image = image_list[0] if image_list else None

    # Tạo mới sản phẩm chỉ với ảnh đầu tiên
    new_product = Product(
        cart_id=cart.cart_id,
        name_product=product.name_product,
        price=product.price,
        quantity=1,
        image=first_image
    )


    # Thêm sản phẩm mới vào session
    db.session.add(new_product)
    db.session.commit()

  # Lấy product_id của sản phẩm đã được thêm vào giỏ hàng
    added_product = Product.query.filter_by(cart_id=cart.cart_id, auto_imei=new_product.auto_imei).first()
    if added_product:
        product_id_in_cart = added_product.product_id
    else:
        return jsonify({"message": "Không tìm thấy sản phẩm trong giỏ hàng"}), 404

    # Lấy thông tin sản phẩm từ request
    product_info = request.get_json()

    # Tạo một đối tượng mới của Detail và thêm thông tin từ request
    new_detail = Detail(
        product_id=product_id_in_cart,
        size_product=product_info.get('selectedSize'),
        color_product=product_info.get('selectedColor')
    )

    # Thêm detail mới vào session
    db.session.add(new_detail)
    db.session.commit()

    return jsonify({"message": "Sản phẩm đã được thêm vào giỏ hàng"}), 200




# Xử lý sự kiện khi người dùng đăng nhập
@user_logged_in.connect
def on_user_logged_in(sender, user):
    # Kiểm tra và tạo giỏ hàng cho người dùng nếu cần
    create_cart_for_user(user)

@views.route('/cart', methods=["GET"])
@login_required
def cart():
    # Lấy user_id của người dùng đã đăng nhập
    user_id = current_user.get_id()  

    # Lấy thông tin giỏ hàng
    cart = Cart.query.filter_by(user_id=user_id).first()  
    if not cart:
        return jsonify({'message': 'Không tìm thấy giỏ hàng.'}), 404

    # Lấy danh sách sản phẩm trong giỏ hàng
    products_in_cart = Product.query.filter_by(cart_id=cart.cart_id).all()

    # Tạo danh sách để chứa thông tin chi tiết của từng sản phẩm
    products_details = []
    for product in products_in_cart:
        # Lấy chi tiết của từng sản phẩm
        detail = Detail.query.filter_by(product_id=product.product_id).first()
        products_details.append({
            'product_id': product.product_id,
            'name_product': product.name_product,
            'price': float(product.price),  # Chuyển đổi giá thành float
            'quantity': product.quantity,
            'image': product.image,
            'date_added': product.date_added,
            'details': {
                'type_product': detail.type_product,
                'color_product': detail.color_product,
                'size_product': detail.size_product,
                'producer': detail.producer,
                'describe': detail.describe,
                'extend': detail.extend
            } if detail else {}
        })
    total_price = sum(product['price'] * product['quantity'] for product in products_details)
    total_quantity = sum(product['quantity'] for product in products_details)
    session['total_quantity'] = total_quantity

    return render_template('cart/cart.html', products_details=products_details, total_price=total_price, total_quantity=total_quantity)


# Xóa sản phẩm
@views.route('/remove_product/<int:product_id>', methods=['POST'])
@login_required
def remove_product(product_id):
    # Tìm sản phẩm cần xóa
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Sản phẩm không tồn tại"}), 404

    # Xóa sản phẩm khỏi bảng chi tiết (detail) trước
    detail = Detail.query.filter_by(product_id=product_id).first()
    if detail:
        db.session.delete(detail)

    # Tiếp theo, xóa sản phẩm khỏi bảng sản phẩm (product)
    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Sản phẩm và chi tiết của nó đã được xóa thành công"}), 200


# Order
@views.route("/order", methods=["GET", "POST"])
def order():
    user_id = current_user.get_id()  

    cart = Cart.query.filter_by(user_id=user_id).first()  
    if not cart:
        return jsonify({'message': 'Không tìm thấy giỏ hàng.'}), 404

    products_in_cart = Product.query.filter_by(cart_id=cart.cart_id).all()

    products_details = []
    for product in products_in_cart:

        detail = Detail.query.filter_by(product_id=product.product_id).first()
        products_details.append({
            'product_id': product.product_id,
            'name_product': product.name_product,
            'price': float(product.price),  
            'quantity': product.quantity,
            'image': product.image,
            'date_added': product.date_added,
            'details': {
                'type_product': detail.type_product,
                'color_product': detail.color_product,
                'size_product': detail.size_product,
                'producer': detail.producer,
                'describe': detail.describe,
                'extend': detail.extend
            } if detail else {}
        })

    total_order_user = sum(product['price'] * product['quantity'] for product in products_details)
    user_id = current_user.user_id
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
      
        new_order = Order(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            zip_code = zip_code,
            totlal_order_user = total_order_user
        )
        
        try:
            db.session.add(new_order)
            db.session.commit()
            flash("Đặt hàng thành công!", "success")
            return redirect(url_for('views.home'))
        except Exception as e:
            flash("An error occurred while placing the order. Please try again later.", "error")
    return render_template("order/order.html",total_order_user=total_order_user)
# Quantity
@views.route('/update_quantity/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    data = request.json
    quantity = data.get('quantity')

    # Lấy thông tin sản phẩm từ cơ sở dữ liệu
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Sản phẩm không tồn tại"}), 404

    # Cập nhật số lượng sản phẩm
    product.quantity = quantity
    db.session.commit()

    return jsonify({"message": "Số lượng sản phẩm đã được cập nhật"}), 200


@views.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        name_product = request.form['name_product']
        price = request.form['price']
        quantity = request.form['quantity']
        images = request.files.getlist('image')

        existing_product = Product.query.filter_by(name_product=name_product).first()
        if existing_product:
            flash("Product with the same name already exists in the database", category="error")
            return render_template('admin/add_product.html')

        # Khởi tạo sản phẩm mới với cart_id mặc định là 1
        new_product = Product(cart_id=1, name_product=name_product, price=price, quantity=quantity, image="",by_admin=True)

        image_filenames = []
        for image in images:
            if image:
                image_filename = secure_filename(image.filename)
                image.save(f'/home/Hyong/pyanywhere/management/static/img/imgdatabase/{image_filename}')
                image_filenames.append(image_filename)
        # Lưu danh sách các tên file ảnh dưới dạng chuỗi, cách nhau bởi dấu ';'
        new_product.image = ';'.join(image_filenames)
        db.session.add(new_product)
        try:
            db.session.commit()
            flash("Vui lòng thêm chi tiết sản phẩm!", "success")
            return redirect(url_for('views.admin_detail', product_id=new_product.product_id))
        except:
            db.session.rollback()
            flash("An error occurred. Product could not be added.", "error")
    
    return render_template('admin/add_product.html')


@views.route("/management_list", methods=["GET","POST"])
@login_required
def list_product():
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))
    products = Product.query.filter_by(cart_id=1).all()
    return render_template('admin/list_product.html',products=products)
# Sửa thông tin sản phẩm
@views.route('/update_product/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))
    # Tìm sản phẩm cần cập nhật từ cơ sở dữ liệu
    product = Product.query.get_or_404(product_id)

    # Cập nhật thông tin sản phẩm từ dữ liệu gửi từ phía client
    product.name_product = request.json.get('name_product', product.name_product)
    product.price = request.json.get('price', product.price)
    product.quantity = request.json.get('quantity', product.quantity)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()

    # Trả về thông báo cập nhật thành công (hoặc có thể trả về JSON khác tùy ý)
    return jsonify({'message': 'Product updated successfully'})
# Xóa sản phẩm trong danh sách sản phẩm được quản lí 
@views.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))
    try:
        # Xóa chi tiết sản phẩm từ bảng Detail trước
        detail_to_delete = Detail.query.filter_by(product_id=product_id).first()
        if detail_to_delete:
            db.session.delete(detail_to_delete)
            db.session.commit()

        # Sau đó, xóa sản phẩm từ bảng Product
        product_to_delete = Product.query.get(product_id)
        if product_to_delete:
            db.session.delete(product_to_delete)
            db.session.commit()

        flash("Xóa sản phẩm thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Xóa sản phẩm không thành công: " + str(e), "error")

    return redirect(url_for('views.list_product'))

@views.route("/approve", methods=["GET","POST"])
@login_required
def approve():
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))
    return render_template('admin/approve.html')
from flask_login import current_user

@views.route("/income", methods=["GET","POST"])
@login_required
def income():
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))

    all_products = Product.query.filter_by(cart_id=1).all()
    all_orders = Product.query.filter(Product.cart_id != 1).all()

    total_price = sum(float(product.quantity) * float(product.price) for product in all_products)
    total_price_order = sum(float(product.quantity) * float(product.price) for product in all_orders)

    warehouse_item = Warehouse.query.first()
    if warehouse_item is None:
        warehouse_item = Warehouse(total_warehouse=total_price)
        db.session.add(warehouse_item)
    else:
        warehouse_item.total_warehouse = total_price

    db.session.commit()

    return render_template('admin/income.html', total_price=total_price, total_price_order=total_price_order)

@views.route("/admin_detail/<int:product_id>", methods=["GET", "POST"])
@login_required
def admin_detail(product_id):
    if current_user.role != 'Admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        type_product = request.form['type_product']
        color_product = request.form['color_product']
        size_product = request.form['size_product']
        producer = request.form['producer']
        describe = request.form['describe']
        extend = request.form['extend']
        
        if product_id:
            existing_detail = Detail.query.filter_by(product_id=product_id).first()
            if existing_detail:
                    flash("Chi tiết sản phẩm cho sản phẩm này đã được thêm trước đó.", "error")
            else:
                new_detail = Detail(
                    product_id=product_id,
                    type_product=type_product,
                    color_product=color_product,
                    size_product=size_product,
                    producer=producer,
                    describe=describe,
                    extend=extend
                )
                db.session.add(new_detail)
                db.session.commit()
                flash("Thêm chi tiết sản phẩm thành công!", "success")
        else:
                flash("Không tồn tại mã sản phẩm!", "error")

    product = Product.query.get(product_id)
    return render_template('admin/add_detail.html', product_id=product_id,product=product)

@views.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    # Xử lý logic xóa ở đây
    order_to_delete = Order.query.get(order_id)
    db.session.delete(order_to_delete)
    db.session.commit()
    return redirect(url_for('views.approve'))