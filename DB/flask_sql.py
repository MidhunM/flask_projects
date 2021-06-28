from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField
from wtforms.validators import ValidationError, DataRequired, \
    Email, EqualTo, Length

app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)



class CreateUserForm(FlaskForm):
    username = StringField(label=('Username'), 
        validators=[DataRequired(), 
        Length(max=64)])
    email = StringField(label=('Email'), 
        validators=[DataRequired(), 
        Email(), 
        Length(max=120)])
    password = PasswordField(label=('Password'), 
        validators=[DataRequired(), 
        Length(min=2, message='Password should be at least %(min)d characters long')])
    confirm_password = PasswordField(
        label=('Confirm Password'), 
        validators=[DataRequired(message='*Required'),
        EqualTo('password', message='Both password fields must be equal!')])

    receive_emails = BooleanField(label=('Receive merketting emails.'))

    submit = SubmitField(label=('Submit'))


    def validate_username(self,username):
       if '%' in username.data:
          raise ValidationError("Character % is not allowed in username")


@app.route('/wtf', methods=('GET', 'POST'))
def wtf_sample():
    form = CreateUserForm()
    if form.validate_on_submit():
        return f'''<h1> Welcome {form.username.data} </h1>'''
    return render_template('forms.html', form=form)



class Students(db.Model):
   id   = db.Column('student_id', db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   city = db.Column(db.String(50))  
   addr = db.Column(db.String(200))
   pin  = db.Column(db.String(10))

   def __init__(self, name, city, addr,pin):
      self.name = name
      self.city = city
      self.addr = addr
      self.pin = pin


@app.route('/')
def show_all():
   return render_template('show_all.html', students = Students.query.all() )

@app.route('/show')
def show_one():
   return render_template('show_data.html')

@app.route('/show_names',methods = ['GET', 'POST'])
def search_one():
   if request.method == 'POST':
      if request.form['f_name']=='':
         flash('Please enter a value', 'error')
      else:   
         names = request.form['f_name']     
         flash('Record was successfully found')
         return render_template('show_data.html', students = Students.query.filter_by(name=names.lower()).all() )

   return render_template('show_data.html')



@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['name'] or not request.form['city'] or not request.form['addr']:
         flash('Please enter all the fields', 'error')
      else:
         student = Students(request.form['name'], request.form['city'],
            request.form['addr'], request.form['pin'])
         
         db.session.add(student)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)