from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, Boolean
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
db = SQLAlchemy(app)


# CREATE FORM
class ListForm(FlaskForm):
    name = StringField('What the list?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class TodoFrom(FlaskForm):
    content = StringField('What to do?', validators=[DataRequired()])
    listId = SelectField('List id: ', choices=[], validators=[DataRequired()])  # Empty choices initially
    submit = SubmitField('Submit')


# CREATE TABLE

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    password = db.Column(db.String(50))
    user_list = db.relationship('List', backref='author')


class List(db.Model):
    __tablename__ = 'list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    date = db.Column(db.DateTime)
    list_item = db.relationship('ToDo', backref='author')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ToDo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    is_checked = db.Column(db.Boolean, default=False)
    content = db.Column(db.String(200))
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))


with app.app_context():
    db.create_all()


@app.route('/')
def start():
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(email=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        flash('Invalid credentials, please try again.')

        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('login.html')


@app.route('/all_lists', methods=['GET'])
def show_all(user_id):
    result_list = List.query.get_or_404(user_id)
    result_todo = ToDo.query.filter_by(list_id=result_list.id).all()
    return render_template('all.html', all_list=result_list, all_todo=result_todo)


@app.route('/list_create', methods=['POST', 'GET'])
def create_list():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    form_list = ListForm()
    if form_list.validate_on_submit():
        new_list = List(
            name=form_list.name.data,
            date=datetime.now(),
            user_id=user_id
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('list.html', form=form_list)


@app.route('/todo_create', methods=['POST', 'GET'])
def create_todo():
    form_todo = TodoFrom()
    form_todo.listId.choices = [(str(t.id), t.name) for t in List.query.all()]
    if form_todo.validate_on_submit():
        new_todo = ToDo(
            is_checked=False,
            content=form_todo.content.data,
            list_id=form_todo.listId.data
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('create_todo'))
    return render_template('todo.html', form=form_todo)


@app.route('/toggle_check/<int:todo_id>', methods=['POST'])
def toggle_check(todo_id):
    todo_item = ToDo.query.get(todo_id)
    if todo_item:
        todo_item.is_checked = not todo_item.is_checked
        db.session.commit()
    return redirect(url_for('show_all'))


if __name__ == '__main__':
    app.run(debug=True, port=5002)
