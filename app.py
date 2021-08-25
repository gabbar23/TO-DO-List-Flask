from flask import Flask,render_template,url_for,redirect,request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user
from wtforms import StringField
from wtforms.validators import DataRequired


app=Flask(__name__)

app.config["SECRET_KEY"]='SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db=SQLAlchemy(app)
class List(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(20))
    task=db.Column(db.String(200))
    is_done=db.Column(db.Boolean)

db.create_all()
class ListForm(FlaskForm):
    list_title=StringField('Title',validators=[DataRequired()])
    list_task=StringField('Task',validators=[DataRequired()])

@app.route('/',methods=['GET','POST'])
def index():
    tasks_data=List.query.all()
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
def done():
    task=request.args.get('task_id')
    task_done=List.query.get(task)
    print("hhereee")
    task_done.is_done=True
    db.session.commit()
    print(type(task_done.is_done))
    return redirect(url_for('index'))



@app.route('/delete')
def delete():
    task=request.args.get('task_id')
    task_to_delete=List.query.get(task)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(debug=True)