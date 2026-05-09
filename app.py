from flask import Flask,render_template,redirect,url_for,request,session
from dashboard import dashboard_app
from events import events_app
from inventory import inventory_app
from payments import payments_app 
from orders import orders_app
from items import items_app
from database import init_db,check_user
import sqlite3

# creating a flask app with scret key and blueprint to link other modules file to main
app=Flask(__name__)
app.secret_key="secret123shreeevents"
app.register_blueprint(dashboard_app)
app.register_blueprint(events_app)
app.register_blueprint(inventory_app)
app.register_blueprint(payments_app)
app.register_blueprint(orders_app)
app.register_blueprint(items_app)

# home route
@app.route('/')
def home():
    return render_template('login.html')

# login page if only logined then redirect to dashboard else stay in login
@app.route('/login',methods=['POST'])
def login_fn():
    error=None
    try:
        username=request.form['username'].strip()
        password=request.form['password'].strip()

        user=check_user(username,password) #call function in database.py file
        if user:
            session['user']=username
            return redirect(url_for('dashboard.dashboard_fn'))
        else:
            error="❌ Incorrect username or password Try Again!!"
            return render_template("login.html",error=error)
        
    except Exception as e:
        error="Something Went wrong. Try Again.."
        return render_template("login.html",error=error)
    
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('home'))
        

if __name__=="__main__":
    init_db()
    app.run(debug=True,use_reloader=False)
    