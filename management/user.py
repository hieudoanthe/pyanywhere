from re import template
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, get_flashed_messages
from sqlalchemy.sql.expression import false
from management.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from management import db
from sqlalchemy import or_


user = Blueprint("user", __name__)

@user.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form.get("data")
        password = request.form.get("password") 
        if data.isdigit():
            phone_number = data
            email = None
        else:
            email = data
            phone_number = None

        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif phone_number:
            user = User.query.filter_by(phone_number=phone_number).first()

        if user:
            if check_password_hash(user.password, password):
                session.permanent = True
                login_user(user, remember=True)
                flash("Logged in successfully!", category="success")
                return redirect(url_for("views.home"))
            else:
                flash("Sai mật khẩu!", category="error")
        else:
            flash("Người dùng không tồn tại!", category="error")

    messages = get_flashed_messages()
    return render_template("regis/login.html", user=current_user)

@user.route("/signup",methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form.get("data")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        # Kiểm tra xem dữ liệu là email hay số điện thoại
        if data.isdigit():
            phone_number = data
            email = None
        else:
            email = data
            phone_number = None
        if email and User.query.filter_by(email=email).first():
            flash("Email đã tồn tại!", category="error")
        elif phone_number and User.query.filter_by(phone_number=phone_number).first():
            flash("Số điện thoại đã tồn tại!", category="error")
        elif len(data) < 4:
            flash("Email hoặc số điện thoại không hợp lệ!", category="error")
        elif len(password) < 7:
            flash("Mật khẩu quá ngắn!", category="error")
        elif password != confirm_password:
            flash("Xác nhận mật khẩu không khớp!", category="error")
        else:
            existing_user = User.query.filter_by(user_name=user_name).first()
            if existing_user:
                flash("Tên đăng nhập đã tồn tại. Vui lòng chọn tên đăng nhập khác!", category="error")
            else:
                password = generate_password_hash(password, method="scrypt")
                new_user = User(email=email, phone_number=phone_number, password=password, user_name=user_name)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=True)
                    flash("Tạo tài khoản thành công!", category="success")
                    return redirect(url_for("user.login"))   
                except Exception as e:
                    flash(f"Error occurred: {str(e)}", category="error")

    messages = get_flashed_messages()
    return render_template("regis/signup.html", user=current_user)



@user.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.login"))