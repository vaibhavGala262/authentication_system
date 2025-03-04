from flask import Flask  , request , render_template , redirect , url_for, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from models import User 

from database import db


app = Flask(__name__ , template_folder='templates' )
app.config['SECRET_KEY'] = 'supersecretkey123!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vaibhavgala262@localhost:3307/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()   # create all tables


@app.route('/')
def home():
    user = User.query.all()

    return render_template('base.html')


@app.route('/register' , methods = ['POST', 'GET'])
def register():
    if request.method=='POST': 

        # we are still not checking if username exists
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password  )
        # then add values to database 
        user = User(name =username ,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect('login' )

    elif request.method =='GET':
        return render_template('register.html')


@app.route('/login' ,  methods = ['POST', 'GET'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method== 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user=User.query.filter_by(name=username).first()
        
        if user and check_password_hash(user.password , password):
            flash('Login successful!', 'success')
            return redirect('/')
        else :
            flash('Enter correct credentials')
            return render_template('login.html')  # maybe we can write more if statement to give context to user exactly what is wrong


if __name__ == '__main__' :
    app.run(host="0.0.0.0" , debug =True)


