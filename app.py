from enum import unique
from os import name
from flask import Flask,render_template,url_for,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user,current_user
from wtforms import StringField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, URL ,ValidationError
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin


app=Flask(__name__)

app.config["SECRET_KEY"]='SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


loginmanager=LoginManager()
loginmanager.init_app(app)
loginmanager.login_view='login'

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@loginmanager.user_loader
def load_user(user_id):
    try:
        return Users.query.get(user_id)
    except:
        return None


db=SQLAlchemy(app)
class Users(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(10))
    username=db.Column(db.String(10),unique=True)
    password=db.Column(db.String(10))
    lists = db.relationship('List', backref='users', lazy='dynamic')

class List(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(20))
    task=db.Column(db.String(200))
    is_done=db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


db.create_all()

class ListForm(FlaskForm):
    list_title=StringField('Title',validators=[DataRequired()])
    list_task=StringField('Task',validators=[DataRequired()])

class Register(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exits. Please choose another.')

class Login(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('Wrong Username or Password')

@app.route('/',methods=['GET','POST'])
@login_required
def index():
    tasks_data=List.query.get(current_user.id)
    form=ListForm()
    if form.validate_on_submit():
        data=List(task=form.list_task.data,title=form.list_title.data)
        db.session.add(data)
        db.session.commit()
        form.list_task.data=""
        form.list_title.data=""
        return redirect (url_for('index'))
    return render_template("index.html",form=form,tasks=tasks_data)


@app.route('/done')
@login_required
def done():
    task=request.args.get('task_id')
    task_done=List.query.get(task)
    print("hhereee")
    task_done.is_done=True
    db.session.commit()
    print(type(task_done.is_done))
    return redirect(url_for('index'))



@app.route('/delete')
@login_required
def delete():
    task=request.args.get('task_id')
    task_to_delete=List.query.get(task)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/register',methods=["GET","POST"]) 
def register():
    form=Register()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        # form.validate_username(form.username.data)
        user=Users(name=form.name.data,username=form.username.data,password=hash_and_salted_password)
        db.session.add(user)
        db.session.commit()
        form.username.data=""
        form.password.data=""
        login_user(user)
        return redirect(url_for('index'))
    return render_template("register.html",form=form)

@app.route('/login',methods=["GET","POST"])
def login():
    form=Login()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user=Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):

            login_user(user)
            if 'next' in session and session['next']:
                if is_safe_url(session['next']):
                    return redirect(session['next'])
            return redirect(url_for('index'))
        return redirect(url_for('index'))

    session['next'] = request.args.get('next')
    return render_template("login.html", form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("logi")
if __name__=="__main__":
    app.run(debug=True)