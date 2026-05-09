from flask import Blueprint,render_template,url_for,request,session,redirect
from database import *

orders_app=Blueprint('orders',__name__)

@orders_app.route('/orders',methods=['GET','POST'])
def orders_fn():
    if 'user' in session:
        # status change to either upcoming or completed
        event_status_change()
        events_list=allocated_list_events()
        return render_template("orders.html",events_list=events_list)
    else:
        return redirect(url_for('home'))