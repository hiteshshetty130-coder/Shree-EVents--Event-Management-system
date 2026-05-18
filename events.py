from flask import Blueprint,redirect,render_template,session,url_for,request
from database import *
from datetime import date

events_app=Blueprint('events',__name__)

# events page route
@events_app.route('/events',methods=['GET','POST'])
def events_fn():
    try:
        
        if 'user' in session:
            edit_data=None

            # if create button is presed then insert data in to database
            if request.method=='POST' and 'create' in request.form:
                event_name=request.form['eventname']
                event_date=request.form['date']
                time=request.form['time']
                place=request.form['place']
                cust=request.form['cust']
                phone=request.form['phone']
                create_events(event_name,event_date,time,place,cust,phone)
                return redirect('/events')
            
            # if delete button in table is clicked then delete that row also in database
            elif request.method=="POST" and 'delete' in request.form:
                event_id=request.form['id']
                delete_events(event_id)
                return redirect('/events')

            # if edit button clicked then store all row data in dict and that helps to show in form to edit 
            elif request.method=="POST" and "edit" in request.form:
                edit_data={
                    "id": request.form['id'],
                    "name": request.form['eventname'],
                    "date": request.form['date'],
                    "time": request.form['time'],
                    "place": request.form['place'],
                    "cust": request.form['cust'],
                    "phone":request.form['phone']
                }

            # if edit is clicked and then update is made data is update4d in row and database
            elif request.method=="POST" and 'update' in request.form:         
                id=request.form['id']
                event_name=request.form['eventname']
                event_date=request.form['date']
                time=request.form['time']
                place=request.form['place']
                cust=request.form['cust']
                phone=request.form['phone']

                update_events(id,event_name,event_date,time,place,cust,phone)
                return redirect('/events')
            
            # function to display all the events data in table
            list_data=events_list()
            tdate=str(date.today())
            return render_template('events.html',list_data=list_data,edit_data=edit_data,tdate=tdate)
            
        else:
            return redirect(url_for('home'))
    
    except Exception as e:
        print(e)
        return("Unexpected Error")
        return redirect(url_for('home'))