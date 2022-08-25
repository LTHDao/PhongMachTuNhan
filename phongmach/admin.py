from phongmach import db, app, utils
from phongmach.models import Medicine, Unit, User, UserRole, Policy
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask_admin import BaseView, expose, Admin
from flask import redirect, request
from datetime import datetime

admin = Admin(app=app, name='PHÒNG MẠCH TƯ SỐ MỘT', template_mode='bootstrap4')


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class UnitView(AuthenticatedModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True
    form_excluded_columns = ['medicine']
    column_labels = {
        "name": "Tên đơn vị thuốc"
    }


class UserView(AuthenticatedModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True
    column_exclude_list = ['password', 'avatar']
    column_labels = {
        "name": "Tên người dùng",
        "activate": "Tình trạng",
        "joined_date": "Ngày đăng ký",
        "user_role": "Quyền"
    }


class MedicineView(AuthenticatedModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True
    column_exclude_list = ['ingredients', 'dosage', 'uses', 'image']

    column_searchable_list = ['name', 'ingredients']
    column_filters = ['unit']
    column_labels = {
        "name": "Tên thuốc",
        "uses": "Công dụng",
        "ingredients": "Thành phần",
        "dosage": "Liều dùng",
        "price": "Giá",
        "image": "Hình ảnh",
        "active": "Còn sử dụng",
        "created_date": "Ngày thêm thuốc",
        "unit": "Đơn vị"
    }
    form_excluded_columns = ['active', 'detail_medicine']


class ChangePolicy(AuthenticatedModelView):
    can_view_details = True
    can_delete = False
    can_create = False
    edit_modal = True
    details_modal = True
    column_exclude_list = ['created_date']
    column_labels = {
        'max_patient': "Số lượng bệnh nhân tối đa khám trong ngày",
        "max_money": "Số tiền cho một lượt khám"
    }
    form_excluded_columns = ['phieukham']


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class StatsView(BaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        return self.render('admin/stats.html', month=month, year=year,
                           money=utils.total_money(month=month, year=year),
                           count_patient=utils.count_patient_in_day(month=month, year=year),
                           total_money=utils.total_money_month(month=month, year=year))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class StatsMedicineView(BaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        return self.render('admin/statsmedicine.html', chart_medicine=utils.chart_medicine(month=month, year=year),
                           month=month, year=year)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


admin.add_view(UnitView(Unit, db.session, name='Đơn vị thuốc'))
admin.add_view(MedicineView(Medicine, db.session, name='Thuốc'))
admin.add_view(UserView(User, db.session, name='Người dùng'))
admin.add_view(ChangePolicy(Policy, db.session, name="Quy định"))
admin.add_view(StatsView(name='Thống kê doanh thu'))
admin.add_view(StatsMedicineView(name='Thống kê thuốc'))
admin.add_view(LogoutView(name='Đăng xuất'))
