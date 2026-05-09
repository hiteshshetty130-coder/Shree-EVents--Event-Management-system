from flask import Blueprint,redirect,render_template,session,url_for
import sqlite3
from database import *

# creating a blueprint to register in main 
dashboard_app=Blueprint('dashboard',__name__)

# dashboard route
@dashboard_app.route('/dashboard')
def dashboard_fn():
    try:
        
        # calling all function in database file and returning the output to dashboard.html
        if 'user' in session:
            data=charts_data()
            months=[]
            sales=[]
            month_name={
                "01":"JAN",
                "02":"FEB",
                "03":"MAR",
                "04":"APR",
                "05":"MAY",
                "06":"JUN",
                "07":"JUL",
                "08":"AUG",
                "09":"SEP",
                "10":"OCT",
                "11":"NOV",
                "12":"DEC"
            }
            cleared=dashboard_data()
            pending=dashboard_total_sales()
            total_events=dashboard_total_events()
            upcoming_events=dashboard_upcoming_data()
            event_status_change()
            for row in data:
                months.append(month_name[row[0]])
                sales.append(row[1])
            return render_template('dashboard.html',months=months,sales=sales,cleared=cleared,pending=pending,total_events=total_events,upcoming_events=upcoming_events)
        else:
            return redirect(url_for('home'))
    
    except Exception as e:
        return render_template('login.html')