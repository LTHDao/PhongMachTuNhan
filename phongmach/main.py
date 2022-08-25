from phongmach import login
from flask import render_template, url_for, session, jsonify
from phongmach.admin import *
import utils
from flask_login import login_user, logout_user, login_required
import cloudinary.uploader
from twilio.rest import Client


@app.route("/")
def home():
    if current_user.is_authenticated and current_user.user_role == UserRole.NURSE:
        return redirect(url_for('home_nurse'))
    return render_template('home.html')


@app.route('/home-nurse')
@login_required
def home_nurse():
    if current_user.is_authenticated and current_user.user_role != UserRole.NURSE:
        return redirect(url_for('home'))
    return render_template('home_nurse.html')


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(name=name, username=username, password=password, avatar=avatar_path)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mật khẩu không khớp!!!'
        except Exception as ex:
            err_msg = "Nhập thông tin bị lỗi: " + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ""
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            if current_user.is_authenticated and current_user.user_role == UserRole.NURSE:
                return redirect(url_for('home_nurse'))
            return redirect(url_for('home'))
        else:
            err_msg = 'Username hoặc password KHÔNG chính xác!!!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/user-logout')
def user_signout():
    logout_user()

    return redirect(url_for('home'))


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/book-appoint', methods=['get', 'post'])
@login_required
def book_appoint():
    err_msg = ""

    if request.method.__eq__('POST'):
        name_patient = request.form.get('name_patient')
        gender = request.form.get('gender')
        phone_number = request.form.get('phone_number')
        birth_date = request.form.get('birth_date')
        booking_date = request.form.get('booking_date')
        address = request.form.get('address')

        if utils.count_book_in_day(booking_date=booking_date) < utils.max_patient() \
                and utils.get_day_done(booking_date=booking_date) == 0:
            try:
                utils.add_regform(name_patient=name_patient, gender=gender, phone_number=phone_number,
                                  birth_date=birth_date, booking_date=booking_date, address=address)
            except Exception as ex:
                err_msg = "Nhập thông tin bị lỗi: " + str(ex)
            else:
                if current_user.is_authenticated and current_user.user_role == UserRole.NURSE:
                    return redirect(url_for('home_nurse'))
                return redirect(url_for('home'))
        else:
            err_msg = "Ngày bạn chọn đã hết!"

    return render_template('book_appoint.html', err_msg=err_msg)


@app.route('/danh-sach-kham', methods=['get', 'post'])
def danh_sach_kham():
    booking_date = request.args.get('booking_date', datetime.now().date())
    list_form = utils.show_list_by_day(booking_date)

    return render_template('list_form.html', booking_date=booking_date, list_form=list_form)


@app.route('/danh-sach-ngay/<booking_date>', methods=['get', 'post'])
def done_list_and_send_sms(booking_date):
    if utils.get_day_done(booking_date) == 0:
        try:
            account_sid = 'ACe667c85add9ee216836746661b519bce'
            auth_token = '9f6e92a6af5c6bae28c2cd344592f3cd'
            client = Client(account_sid, auth_token)

            for send in utils.get_phone_number(booking_date):
                message = client.messages.create(
                    messaging_service_sid='MG9f95524af96c43614a1c8cf4e71ad734',
                    body='Xin chao! Day la phong mach tu gia truyen,'
                         ' lich kham cua ban da duoc ghi nhan, hay den dung gio kham da dang ky nhe!!!',
                    to='+' + send
                )

                print(message.sid)

            utils.add_list_patient(booking_date)
        except:
            err_msg = "Lỗi! Không thể hoàn tất ngày này! Thử lại sau."
        else:
            return redirect(url_for('home_nurse'))
    else:
        err_msg = "Lỗi! Ngày này đã chốt rồi!!!"

    return render_template('list_form.html', err_msg=err_msg)


@app.route('/api/add-phieu', methods=['post'])
def add_phieu():
    regis_id = request.json.get('regis_id')
    symptom = request.json.get('symptom')
    predict = request.json.get('predict')

    phieukham = {
        'regis_id': regis_id,
        'symptom': symptom,
        'predict': predict
    }
    session['phieukham'] = phieukham

    return session['phieukham']


@app.route('/api/add-medicine', methods=['post'])
def add_medicine():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    unit_name = data.get('unit')
    dosage = data.get('dosage')
    price = data.get('price')

    list_medicines = session.get('list_medicines')
    if not list_medicines:
        list_medicines = {}

    if id in list_medicines:
        list_medicines[id]['quantity'] = list_medicines[id]['quantity'] + 1
    else:
        list_medicines[id] = {
            'id': id,
            'name': name,
            'price': price,
            'unit': unit_name,
            'dosage': dosage,
            'quantity': 1
        }
    session['list_medicines'] = list_medicines

    return session['list_medicines']


@app.route('/api/update', methods=['put'])
def update_medicines():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    list_medicines = session.get('list_medicines')
    if list_medicines and id in list_medicines:
        list_medicines[id]['quantity'] = quantity
        session['list_medicines'] = list_medicines

    return session['list_medicines']


@app.route('/api/delete-medicines/<medicine_id>', methods=['delete'])
def delete_medicines(medicine_id):
    list_medicines = session.get('list_medicines')

    if list_medicines and medicine_id in list_medicines:
        del list_medicines[medicine_id]
        session['list_medicines'] = list_medicines

    return session['list_medicines']


@app.route('/api/save', methods=['post'])
def save():
    try:
        utils.add_phieu(session.get('phieukham'), session.get('list_medicines'))
    except:
        return jsonify({'code': 400})
    else:
        return jsonify({'code': 200})


@app.route('/nhap-don-thuoc', methods=['get', 'post'])
def luu_don_thuoc():
    return render_template('phieu_kham.html',
                           medicines=utils.read_medicine(),
                           regis=utils.get_name_patient_by_id(session.get('phieukham')))


@app.route('/receipt', methods=['get', 'post'])
def receipt():
    money = utils.count_medicines(session.get('list_medicines'))
    patient = utils.get_name_patient_by_id(session.get('phieukham'))
    del session['phieukham']
    del session['list_medicines']
    return render_template('pay.html', money=money, patient=patient)


@app.route('/user/<username>')
@login_required
def user(username):
    return render_template('user.html', user=utils.check_user(username))


@app.route('/registration_form/<user_id>')
@login_required
def registration_form(user_id):
    return render_template('my_registration_form.html', regform=utils.show_regform(user_id))


@app.route('/delete-regform')
@login_required
def delete_regform():
    regform_id = request.args.get('regform_id')
    if regform_id:
        utils.delete_regform(regform_id=int(regform_id))

    return redirect(url_for('registration_form', user_id=current_user.id))


if __name__ == '__main__':
    app.run(debug=True)
