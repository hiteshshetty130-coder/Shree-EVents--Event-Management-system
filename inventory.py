from flask import Blueprint,render_template,url_for,request,session,redirect
from database import *

inventory_app=Blueprint('inventory',__name__)

# route
@inventory_app.route('/inventory',methods=['GET','POST'])
# inventory function 
def inventory_fn():
    if 'user' in session: 
        # get the event id of particular event to allocate inventory 
        event_id=request.form.get('event_id') or request.args.get('event_id')
        inven_data = get_inventory()
        show_popup=False

        if request.method == "POST":

            # add inventory button clicked action 
            if "allocate_inventory" in request.form:
                # gets all name quanity and price and insert into table
                event_name = request.form['itemname']
                quantity = request.form['quantity']
                price = request.form['price']
                add_inventory(event_name, quantity, price)
                return redirect('/inventory')
            
            # save allocation action 
            elif "sava_alloc" in request.form:
                # get event id
                event_id=request.form.get('event_id')
                items=get_inventory()

                # get all the items from inventory table and add to 
                # allocation table if already added then increase quantity
                for item in items:
                    item_id=item[0]
                    stock=item[2]
                    item_name=item[1]
                    price_per=item[3]

                    # get qunatity from the input field in the form
                    qty=request.form.get(f'qty_{item_id}')

                    # only if qty is positive insert into allocation
                    if qty and int(qty)>=0:
                        update_allocation(event_id,item_id,int(qty),item_name,price_per)

                update_status(event_id) #change status to allocated
                inven_data=get_inventory()
                show_popup=False
                return redirect('/inventory')

            # search btn click action
            elif "search_btn" in request.form:
                search=request.form.get('search')
                inven_data=search_inventory(search)
                show_popup=True

            # clear btn click action
            elif "clear_btn" in request.form:
                inven_data=get_inventory()
                show_popup=True

            # delete btn click action
            elif "delete_btn" in request.form:
                event_id = request.form.get('event_id')
                item_id = request.form.get('item_id')

                items = get_inventory()

                # loop over the items 
                for item in items:
                    # if the items in loop and item deleted match then return to  available qty 
                    if str(item[0]) == str(item_id):
                        item_name = item[1]
                        price = item[3]

                        update_allocation(event_id, item_id, 0, item_name, price)

                return redirect('/inventory')            

            # show all the inevntory
            else:
                inven_data=get_inventory()
                show_popup=False
        else:
            inven_data=get_inventory()
            show_popup=False

        # create on dict show that you give existing allocated data of each event item 
        existing_alloc={}
        if event_id:
            show_popup=True
            rows=allocated_inventory_list()
            # loops and if the event id matches then add to dict
            # existing_alloc={"item_id":"quantity"}
            for row in rows:
                if str(row[0])==str(event_id):
                    existing_alloc[row[6]]=row[4]
        
        
        # get all required data
        events=events_list_in()
        allocated_list=allocated_inventory_list()
        allocated_events_list=allocated_events()
        total_data=total_mount_calculations()
        
        return render_template("inventory.html",existing_alloc=existing_alloc,events=events,inven_data=inven_data,show_popup=show_popup,event_id=event_id,allocated_events_list=allocated_events_list,allocated_list=allocated_list,total_data=total_data)
    else:
        return redirect(url_for('home'))