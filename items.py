from flask import Blueprint,redirect,render_template,session,url_for,request
from database import *

items_app=Blueprint('items',__name__)

# events page route
@items_app.route('/items',methods=['GET','POST'])
def items_fn():
    if 'user' in session:
        inventories=get_inventory()
        return render_template('items.html',inventories=inventories)
    else:
        return redirect(url_for('home'))
    

    
@items_app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if 'user' in session:
        delete_inventory_item(item_id)
        return redirect(url_for('items.items_fn'))
    else:
        return redirect(url_for('home'))