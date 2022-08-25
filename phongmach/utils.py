from phongmach import db
from phongmach.models import User, RegistrationForm, Policy, PhieuKham,\
    ChiTietPhieuKham, Medicine, Unit, Receipt, ListPatient
import hashlib
from sqlalchemy import func, extract
from flask_login import current_user


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(), username=username.strip(), password=password, avatar=kwargs.get('avatar'))
    db.session.add(user)
    db.session.commit()


def max_patient():
    p = Policy.query.get(1)

    return p.max_patient


def max_money():
    p = Policy.query.get(1)

    return p.max_money


def count_book_in_day(booking_date):
    return RegistrationForm.query.filter(RegistrationForm.booking_date.__eq__(booking_date)).count()


def add_regform(name_patient, gender, phone_number, birth_date, booking_date, address):
    phone = int(phone_number.replace('0', '84', 1))
    book_appoint = RegistrationForm(name_patient=name_patient, gender=gender,
                                    phone_number=phone, birth_date=birth_date,
                                    booking_date=booking_date, address=address, user_id=current_user.id)
    db.session.add(book_appoint)
    db.session.commit()


def count_patient_in_day(month, year):
    return db.session.query(extract('day', PhieuKham.created_date),
                            func.count(PhieuKham.id)) \
                            .filter(extract('year', PhieuKham.created_date) == year)\
                            .filter(extract('month', PhieuKham.created_date) == month) \
                            .group_by(extract('day', PhieuKham.created_date)).all()


def chart_medicine(month, year):
    return Medicine.query.join(ChiTietPhieuKham, ChiTietPhieuKham.medicine_id.__eq__(Medicine.id)) \
        .join(PhieuKham, ChiTietPhieuKham.phieukham_id.__eq__(PhieuKham.id)) \
        .join(Unit, Unit.id.__eq__(Medicine.unit_id)) \
        .add_column(Unit.name) \
        .add_column(func.sum(ChiTietPhieuKham.quantity)) \
        .add_column(func.count(ChiTietPhieuKham.medicine_id)) \
        .filter(extract('year', PhieuKham.created_date) == year) \
        .filter(extract('month', PhieuKham.created_date) == month) \
        .group_by(Medicine.name).all()


def total_money(month, year):
    return db.session.query(extract('day', PhieuKham.created_date),
                            (func.sum(ChiTietPhieuKham.quantity * Medicine.price) + func.sum(Policy.max_money)))\
                            .join(ChiTietPhieuKham, ChiTietPhieuKham.phieukham_id.__eq__(PhieuKham.id)) \
                            .join(Medicine, ChiTietPhieuKham.medicine_id.__eq__(Medicine.id)) \
                            .join(Policy, Policy.id.__eq__(PhieuKham.policy_id))\
                            .filter(extract('year', PhieuKham.created_date) == year) \
                            .filter(extract('month', PhieuKham.created_date) == month) \
                            .group_by(extract('day', PhieuKham.created_date))\
                            .order_by(extract('day', PhieuKham.created_date)).all()


def total_money_month(month, year):
    return db.session.query(extract('month', PhieuKham.created_date),
                            (func.sum(ChiTietPhieuKham.quantity * Medicine.price) + func.sum(Policy.max_money)))\
                            .join(ChiTietPhieuKham, ChiTietPhieuKham.phieukham_id.__eq__(PhieuKham.id)) \
                            .join(Medicine, ChiTietPhieuKham.medicine_id.__eq__(Medicine.id)) \
                            .join(Policy, Policy.id.__eq__(PhieuKham.policy_id))\
                            .filter(extract('year', PhieuKham.created_date) == year) \
                            .filter(extract('month', PhieuKham.created_date) == month) \
                            .group_by(extract('month', PhieuKham.created_date)).all()


def read_medicine():
    return Medicine.query.all()


def get_regform_by_id(regform_id):
    return RegistrationForm.query.get(regform_id)


def get_name_patient_by_id(phieukham):
    if phieukham:
        id = phieukham['regis_id']
        r = RegistrationForm.query.get(id)
        return {
                'name': r.name_patient,
                'date': r.booking_date
                }


def add_phieu(phieukham, list_medicines):
    policy = 1
    r = get_regform_by_id(phieukham['regis_id'])
    if list_medicines:
        p = PhieuKham(symptom=phieukham['symptom'], predict=phieukham['predict'], RegistrationForm=r, policy_id=policy)
        db.session.add(p)

        for m in list_medicines.values():
            c = ChiTietPhieuKham(phieukham=p,
                                 medicine_id=m['id'],
                                 quantity=m['quantity'],
                                 dosage=m['dosage'])
            db.session.add(c)

        receipt = Receipt(money_default=count_medicines(list_medicines)['policy_money'],
                          money_medicines=count_medicines(list_medicines)['total_amount'],
                          phieukham=p,
                          policy_id=policy)
        db.session.add(receipt)

    db.session.commit()


def count_medicines(list_medicines):
    total_amount = 0

    if list_medicines:
        for m in list_medicines.values():
            total_amount += m['quantity'] * m['price']

    return {
        'total_amount': total_amount,
        'policy_money': max_money()
    }


def show_list_by_day(booking_date):
    r = RegistrationForm.query.filter(RegistrationForm.booking_date.__eq__(booking_date)).all()
    return r


def get_day_done(booking_date):
    if ListPatient.query.filter(ListPatient.date.__eq__(booking_date)).all():
        return 1
    return 0


def get_phone_number(booking_date):
    phone_number = []
    p = RegistrationForm.query.filter(RegistrationForm.booking_date.__eq__(booking_date)).all()

    for i in p:
        phone_number.append(i.phone_number)
    return phone_number


def add_list_patient(date):
    new_list = ListPatient(date=date)
    db.session.add(new_list)
    db.session.commit()
    for l in show_list_by_day(date):
        res = RegistrationForm.query.get(l.id)
        res.list_id = new_list.id
        db.session.add(res)
    db.session.commit()


def check_user(username):
    return User.query.filter_by(username=username).first()


def show_regform(user_id):
    return RegistrationForm.query.filter(RegistrationForm.user_id.__eq__(user_id))\
        .filter(RegistrationForm.list_id.__eq__(None)).all()


def delete_regform(regform_id):
    p = RegistrationForm.query.get(regform_id)
    db.session.delete(p)
    db.session.commit()
