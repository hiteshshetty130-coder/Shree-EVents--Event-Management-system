from flask import Blueprint,render_template,url_for,request,session,redirect,flash
from database import *

inventory_app=Blueprint('inventory',__name__)

@inventory_app.route('/inventory',methods=['GET','POST'])
def inventory_fn():
    if 'user' in session:
        event_id=request.form.get('event_id') or request.args.get('event_id')
        show_popup=False

        # get event date for the selected event
        event_date=None
        if event_id:
            event=get_event_by_id(event_id)
            if event:
                event_date=event[2]

        # initialize existing_alloc early
        existing_alloc={}

        inven_data=get_inventory(event_date)

        if request.method == "POST":

            # add inventory item
            if "allocate_inventory" in request.form:
                event_name=request.form['itemname']
                quantity=request.form['quantity']
                price=request.form['price']
                add_inventory(event_name,quantity,price)
                return redirect('/inventory')

            # save allocation
            elif "sava_alloc" in request.form:
                event_id=request.form.get('event_id')
                event=get_event_by_id(event_id)
                event_date=event[2] if event else None

                items=get_inventory(event_date)
                selected=False

                # merge form quantities into session cart
                cart=session.get('alloc_cart',{})
                for item in items:
                    item_id=item[0]
                    qty=request.form.get(f'qty_{item_id}')
                    if qty is not None:
                        if int(qty)>0:
                            cart[str(item_id)]=int(qty)
                        else:
                            cart.pop(str(item_id),None)
                session['alloc_cart']=cart

                # save everything in cart to DB
                all_items=get_inventory(event_date)
                item_map={str(i[0]):(i[1],i[3]) for i in all_items}

                for item_id_str,qty in cart.items():
                    if item_id_str in item_map:
                        item_name=item_map[item_id_str][0]
                        price_per=item_map[item_id_str][1]
                        update_allocation(event_id,item_id_str,qty,item_name,price_per)
                        selected=True

                if not selected:
                    flash("Please allocate at least one inventory item")
                    return redirect(f'/inventory?event_id={event_id}')

                # clear cart after saving
                session.pop('alloc_cart',None)
                update_status(event_id)
                show_popup=False
                return redirect('/inventory')

            # search
            elif "search_btn" in request.form:
                search=request.form.get('search')

                # save currently visible quantities into session cart before searching
                cart=session.get('alloc_cart',{})
                all_items=get_inventory(event_date)
                for item in all_items:
                    item_id=item[0]
                    qty=request.form.get(f'qty_{item_id}')
                    if qty is not None:
                        if int(qty)>0:
                            cart[str(item_id)]=int(qty)
                        else:
                            cart.pop(str(item_id),None)
                session['alloc_cart']=cart

                inven_data=search_inventory(search)
                show_popup=True

            # clear search
            elif "clear_btn" in request.form:
                # save currently visible quantities into session cart before clearing
                cart=session.get('alloc_cart',{})
                all_items=get_inventory(event_date)
                for item in all_items:
                    item_id=item[0]
                    qty=request.form.get(f'qty_{item_id}')
                    if qty is not None:
                        if int(qty)>0:
                            cart[str(item_id)]=int(qty)
                        else:
                            cart.pop(str(item_id),None)
                session['alloc_cart']=cart

                inven_data=get_inventory(event_date)
                show_popup=True

            # delete allocation item
            elif "delete_btn" in request.form:
                event_id=request.form.get('event_id')
                item_id=request.form.get('item_id')

                event=get_event_by_id(event_id)
                event_date=event[2] if event else None
                items=get_inventory(event_date)

                for item in items:
                    if str(item[0])==str(item_id):
                        item_name=item[1]
                        price=item[3]
                        update_allocation(event_id,item_id,0,item_name,price)

                return redirect('/inventory')

            else:
                inven_data=get_inventory(event_date)
                show_popup=False

        else:
            inven_data=get_inventory(event_date)
            show_popup=False
            # clear cart when opening fresh (GET request without event_id)
            if not event_id:
                session.pop('alloc_cart',None)

        # build existing_alloc — start from DB saved values
        if event_id:
            show_popup=True
            rows=allocated_inventory_list()
            for row in rows:
                if str(row[0])==str(event_id):
                    existing_alloc[row[6]]=row[4]

        # overlay session cart on top of DB values
        # session cart always wins (latest user input)
        cart=session.get('alloc_cart',{})
        for item_id_str,qty in cart.items():
            try:
                existing_alloc[int(item_id_str)]=qty
            except:
                existing_alloc[item_id_str]=qty

        events=events_list_in()
        allocated_list=allocated_inventory_list()
        allocated_events_list=allocated_events()
        total_data=total_mount_calculations()

        return render_template("inventory.html",existing_alloc=existing_alloc,events=events,inven_data=inven_data,show_popup=show_popup,event_id=event_id,allocated_events_list=allocated_events_list,allocated_list=allocated_list,total_data=total_data)
    else:
        return redirect(url_for('home'))