from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,TextAreaField
from wtforms.validators import DataRequired
from models import db, Admin, MemberBulanan, MemberHarian

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'



# Konfigurasi SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.config['WTF_CSRF_ENABLED'] = False



# Inisialisasi Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'



#Client Side
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/join/daily', methods=['GET', 'POST'])
def join_daily():
    if request.method == 'POST':
        nama = request.form['nama']
        jenis_kelamin = request.form['jenis_kelamin']
        alamat = request.form['alamat']
        
        new_member = MemberHarian(nama=nama, jenis_kelamin=jenis_kelamin, alamat=alamat)
        db.session.add(new_member)
        db.session.commit()

        return redirect('/thank_you')

    return render_template('join_daily.html')



@app.route('/join/monthly', methods=['GET', 'POST'])
def join_monthly():
    if request.method == 'POST':
        nama = request.form['nama']
        jenis_kelamin = request.form['jenis_kelamin']
        alamat = request.form['alamat']
        nomor_hp = request.form['nomor_hp']
        
        new_member = MemberBulanan(nama=nama, jenis_kelamin=jenis_kelamin, alamat=alamat, nomor_hp=nomor_hp)
        db.session.add(new_member)
        db.session.commit()

        return redirect('/thank_you')

    return render_template('join_monthly.html')



@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

def findOut(objectData) :
    try:
        tes_attributes = vars(objectData)
        
        for field, value in tes_attributes.items():
            print(f"{field}: {value}")

    except Exception as e:
        print(f"Error retrieving object attributes: {e}") 



#Admin Side
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



# Fungsi untuk melakukan login jika is_admin == 1
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Admin.query.filter_by(username=username).first()
        if user and user.check_password(password=password) and user.is_admin == 1:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah atau bukan admin.', 'danger')

    return render_template('login.html', form=form)



# Rute untuk admin_dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_authenticated or not current_user.is_admin == 1:
        flash('Anda tidak memiliki izin untuk mengakses halaman ini atau belum login sebagai admin.', 'danger')
        return redirect(url_for('login'))

    daily_members = MemberHarian.query.all()
    monthly_members = MemberBulanan.query.all()

    return render_template('admin.html', daily_members=daily_members, monthly_members=monthly_members)



# Rute untuk logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



class MemberForm(FlaskForm):
    nama = StringField('Nama', validators=[DataRequired()])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-Laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    alamat = StringField('Alamat', validators=[DataRequired()])
    nomor_hp = StringField('Nomor HP')
    submit = SubmitField('Submit')



# Update Member Route
@app.route('/admin/update_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def update_member(member_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    member = MemberHarian.query.get_or_404(member_id)
    form = MemberForm(obj=member)

    if form.validate_on_submit():
        member.nama = form.nama.data
        member.jenis_kelamin = form.jenis_kelamin.data
        member.alamat = form.alamat.data
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('update_member.html', form=form, member=member)



@app.route('/admin/delete_member/<member_type>/<int:member_id>', methods=['POST'])
@login_required     
def delete_member(member_type, member_id):
    if member_type == 'daily':
        member = MemberHarian.query.get_or_404(member_id)
    elif member_type == 'monthly':
        member = MemberBulanan.query.get_or_404(member_id)
    else:
        flash('Invalid member type', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(member)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

class DailyMemberForm(FlaskForm):
    nama = StringField('Nama', validators=[DataRequired()])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-Laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    alamat = TextAreaField('Alamat', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form untuk menambahkan anggota bulanan
class MonthlyMemberForm(FlaskForm):
    nama = StringField('Nama', validators=[DataRequired()])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-Laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    alamat = TextAreaField('Alamat', validators=[DataRequired()])
    nomor_hp = StringField('Nomor HP')
    submit = SubmitField('Submit')



@app.route('/admin/daily_members')
@login_required
def admin_daily_members():
    if not current_user.is_authenticated or not current_user.is_admin == 1:
        flash('Anda tidak memiliki izin untuk mengakses halaman ini atau belum login sebagai admin.', 'danger')
        return redirect(url_for('login'))

    daily_members = MemberHarian.query.all()
    return render_template('daily_members.html', daily_members=daily_members)



@app.route('/admin/monthly_members')
@login_required
def admin_monthly_members():
    if not current_user.is_authenticated or not current_user.is_admin == 1:
        flash('Anda tidak memiliki izin untuk mengakses halaman ini atau belum login sebagai admin.', 'danger')
        return redirect(url_for('login'))

    monthly_members = MemberBulanan.query.all()
    return render_template('monthly_members.html', monthly_members=monthly_members)
from flask import request



@app.route('/admin/add_daily_member', methods=['GET', 'POST'])
@login_required
def add_daily_member():
    if current_user.is_admin != 1:
        flash('Anda tidak memiliki izin untuk menambahkan anggota harian.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        nama = request.form['nama']
        jenis_kelamin = request.form['jenis_kelamin']
        alamat = request.form['alamat']

        new_member = MemberHarian(nama=nama, jenis_kelamin=jenis_kelamin, alamat=alamat)
        db.session.add(new_member)

        try:
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat menambahkan anggota harian.', 'danger')
            print(f"Error: {str(e)}")

    return render_template('add_daily_member.html')



@app.route('/admin/add_monthly_member', methods=['GET', 'POST'])
@login_required
def add_monthly_member():
    if not current_user.is_admin:
        flash('You do not have permission to add monthly members.', 'danger')
        return redirect(url_for('index'))

    form = MonthlyMemberForm()

    if form.validate_on_submit():
        nama = form.nama.data
        jenis_kelamin = form.jenis_kelamin.data
        alamat = form.alamat.data
        nomor_hp = form.nomor_hp.data

        new_member = MemberBulanan(nama=nama, jenis_kelamin=jenis_kelamin, alamat=alamat, nomor_hp=nomor_hp)
        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_monthly_member.html', form=form)



@app.route('/admin/update_daily_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def update_daily_member(member_id):
    if not current_user.is_authenticated or not current_user.is_admin == 1:
        flash('Anda tidak memiliki izin untuk mengakses halaman ini atau belum login sebagai admin.', 'danger')
        return redirect(url_for('login'))

    member = MemberHarian.query.get_or_404(member_id)
    form = DailyMemberForm(obj=member)

    if form.validate_on_submit():
        member.nama = form.nama.data
        member.jenis_kelamin = form.jenis_kelamin.data
        member.alamat = form.alamat.data
        db.session.commit()

        return redirect(url_for('admin_daily_members'))

    return render_template('update_daily_members.html', form=form, member=member)



@app.route('/admin/update_monthly_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def update_monthly_member(member_id):
    if not current_user.is_authenticated or not current_user.is_admin == 1:
        flash('Anda tidak memiliki izin untuk mengakses halaman ini atau belum login sebagai admin.', 'danger')
        return redirect(url_for('login'))

    member = MemberBulanan.query.get_or_404(member_id)
    form = MonthlyMemberForm(obj=member)

    if form.validate_on_submit():
        member.nama = form.nama.data
        member.jenis_kelamin = form.jenis_kelamin.data
        member.alamat = form.alamat.data
        member.nomor_hp = form.nomor_hp.data
        db.session.commit()

        return redirect(url_for('admin_monthly_members'))

    return render_template('update_monthly_members.html', form=form, member=member)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)