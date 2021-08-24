from flask import Flask,render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


app=Flask(__name__)

app.config["SECRET_KEY"]='SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class List(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    task=db.Column(db.String(100))


#db.create_all()
class ListForm(FlaskForm):
    list_item=StringField('To-Do',validators=[DataRequired()])

@app.route('/',methods=['GET','POST'])
def index():
    form=ListForm()
    if form.validate_on_submit():
        data=List(task=form.list_item.data)
        db.session.add(data)
        db.session.commit()
        redirect (url_for('index'))
    return render_template("index.html",form=form)



if __name__=="__main__":
    app.run(debug=True)