from flask import Blueprint, render_template, url_for, request, session, redirect, flash
from database import *

inventory_app = Blueprint('inventory', __name__)


# ─── Utilities ───────────────────────────────────────────────────────────────

def safe_int(val):
    """Convert to int safely, return 0 for empty/invalid input."""
    try:
        return int(val) if val and val.strip() else 0
    except (ValueError, TypeError):
        return 0


def get_event_date(event_id):
    """Get event date from event_id."""
    if event_id:
        event = get_event_by_id(event_id)
        if event:
            return event[2]
    return None


def save_cart(event_date):
    """
    Save currently visible item quantities from the form
    into session cart before searching or clearing.
    """
    cart = session.get('alloc_cart', {})
    all_items = get_inventory(event_date)

    for item in all_items:
        item_id = item[0]
        qty = safe_int(request.form.get(f'qty_{item_id}'))
        if qty > 0:
            cart[str(item_id)] = qty
        else:
            cart.pop(str(item_id), None)

    session['alloc_cart'] = cart


def build_existing_alloc(event_id):
    """
    Build existing_alloc dict:
    1. Load saved allocations from DB
    2. Overlay session cart on top (cart = latest user input)
    """
    existing_alloc = {}

    # Step 1 - from DB
    rows = allocated_inventory_list()
    for row in rows:
        if str(row[0]) == str(event_id):
            existing_alloc[row[6]] = row[4]

    # Step 2 - session cart overrides DB
    cart = session.get('alloc_cart', {})
    for item_id_str, qty in cart.items():
        try:
            existing_alloc[int(item_id_str)] = qty
        except:
            existing_alloc[item_id_str] = qty

    return existing_alloc


# ─── POST Handlers ───────────────────────────────────────────────────────────

def handle_add_inventory():
    """Handle adding a new inventory item."""
    item_name = request.form['itemname']
    quantity = request.form['quantity']
    price = request.form['price']
    add_inventory(item_name, quantity, price)
    return redirect('/inventory')


def handle_save_allocation(event_id):
    """Handle saving the full allocation to DB."""
    event_date = get_event_date(event_id)

    # save visible quantities into cart first
    save_cart(event_date)
    cart = session.get('alloc_cart', {})

    # check if cart is empty
    if not cart:
        flash("Please enter a quantity greater than 0 for at least one item.", "error")
        return redirect(f'/inventory?event_id={event_id}')

    # build item map for name and price lookup
    all_items = get_inventory(event_date)
    item_map = {str(i[0]): (i[1], i[3]) for i in all_items}

    selected = False
    for item_id_str, qty in cart.items():
        if item_id_str in item_map:
            item_name = item_map[item_id_str][0]
            price_per = item_map[item_id_str][1]
            update_allocation(event_id, item_id_str, qty, item_name, price_per)
            selected = True

    if not selected:
        flash("Please allocate at least one inventory item.", "error")
        return redirect(f'/inventory?event_id={event_id}')

    # clear cart and update event status
    session.pop('alloc_cart', None)
    update_status(event_id)
    return redirect('/inventory')


def handle_search(event_date):
    """Save quantities then search inventory."""
    save_cart(event_date)
    search = request.form.get('search')
    return search_inventory(search)


def handle_clear_search(event_date):
    """Save quantities then clear search."""
    save_cart(event_date)
    return get_inventory(event_date)


def handle_delete_allocation():
    """Handle deleting a single allocated item."""
    event_id = request.form.get('event_id')
    item_id = request.form.get('item_id')

    event_date = get_event_date(event_id)
    items = get_inventory(event_date)

    for item in items:
        if str(item[0]) == str(item_id):
            item_name = item[1]
            price = item[3]
            update_allocation(event_id, item_id, 0, item_name, price)

    return redirect('/inventory')


# ─── Main Route ──────────────────────────────────────────────────────────────

@inventory_app.route('/inventory', methods=['GET', 'POST'])
def inventory_fn():
    if 'user' not in session:
        return redirect(url_for('home'))

    event_id = request.form.get('event_id') or request.args.get('event_id')
    event_date = get_event_date(event_id)
    inven_data = get_inventory(event_date)
    show_popup = False

    if request.method == 'POST':

        if 'allocate_inventory' in request.form:
            return handle_add_inventory()

        elif 'sava_alloc' in request.form:
            return handle_save_allocation(event_id)

        elif 'search_btn' in request.form:
            inven_data = handle_search(event_date)
            show_popup = True

        elif 'clear_btn' in request.form:
            inven_data = handle_clear_search(event_date)
            show_popup = True

        elif 'delete_btn' in request.form:
            return handle_delete_allocation()

    else:
        # GET - clear cart if no event selected (fresh open)
        if not event_id:
            session.pop('alloc_cart', None)

    # build existing_alloc and show popup if event is selected
    existing_alloc = {}
    if event_id:
        show_popup = True
        existing_alloc = build_existing_alloc(event_id)

    return render_template(
        "inventory.html",
        existing_alloc=existing_alloc,
        events=events_list_in(),
        inven_data=inven_data,
        show_popup=show_popup,
        event_id=event_id,
        allocated_events_list=allocated_events(),
        allocated_list=allocated_inventory_list(),
        total_data=total_mount_calculations()
    )