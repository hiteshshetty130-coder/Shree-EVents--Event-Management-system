from flask import Blueprint, render_template, session, redirect, url_for
from database import *

payments_app = Blueprint('payments',__name__)

#PAYMENT PAGE
@payments_app.route('/payments',methods=['GET','POST'])
def payments_fn():

    if 'user' in session:
        events = allocated_orders_events()
        totals = total_mount_calculations()

        return render_template(
            "payments.html",
            events=events,
            totals=totals
        )
    else:
        return redirect(url_for('home'))

# billing function
@payments_app.route('/bill/<int:event_id>')
def bill_page(event_id):
    if 'user' in session:
        event = get_event_by_id(event_id)
        items = get_item_by_id(event_id)
        total = total_by_item(event_id)

        gst_total=total*9/100
        final_total=total+gst_total

        return render_template(
            "bill.html",
            event=event,
            items=items,
            total=total,
            gst_total=gst_total,
            final_total=final_total
        )
    else:
        return redirect(url_for('home'))