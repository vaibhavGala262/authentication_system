from flask import Flask  , request , render_template , redirect , url_for, flash , session
import requests
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from authlib.integrations.flask_client import OAuth
from models import User 
import stripe
import re

stripe.api_key = 'sk_test_tR3PYbcVNZZ796tH88S4VQ2u'

from database import db
from api_key import CLIENT_SECRET ,CLIENT_ID
YOUR_DOMAIN= 'http://127.0.0.1:5000/'



app = Flask(__name__ , template_folder='templates' )
oauth = OAuth(app) # integrates app with OAuth

google = oauth.register(
    name  = 'google' , 
    client_id = CLIENT_ID, 
    client_secret =CLIENT_SECRET , 
    authorize_url='https://accounts.google.com/o/oauth2/auth' , 
    
    server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration', # without this doesnt work 3rd method
    client_kwargs= {'scope':'openid profile email'}
)



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



@app.route('/login/')

def login_google():

    try:
      redirect_uri = url_for('authorize_google' , _external=True)
      return google.authorize_redirect(redirect_uri)

    except Exception as e:
      app.logger.error(f"Errorr during login : {str(e)}")
      return f"Error occured {str(e)}" , 500
    
@app.route('/authorize/google')
def authorize_google():
    try :
        token = google.authorize_access_token()
        """
        userinfo_endpoint= google.server_metadata_url['userinfo_endpoint']
       
        1... metadata = requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
        userinfo_endpoint = metadata.get("userinfo_endpoint")
        
        2... metadata = google.load_server_metadata()  # Fetch metadata
        userinfo_endpoint = metadata['userinfo_endpoint']  # Get userinfo endpoint

        3...userinfo_endpoint= google.server_metadata['userinfo_endpoint']
        Any method works 
        """
        
        userinfo_endpoint= google.server_metadata['userinfo_endpoint']
        resp = google.get(userinfo_endpoint) 
        user_info = resp.json()
        username = user_info['email']


        user = User.query.filter_by(name = username ).first()
        if not user:
            user = User(name= username , password=generate_password_hash(username) )
            db.session.add(user)
            db.session.commit()

            session['username']= username
            session['oauth_token']=token
        return render_template('Logged_in.html')
    
    except Exception as e :
        return str(e)


           
    
    

       


if __name__ == '__main__' :
    app.run(host="0.0.0.0" , debug =True)


