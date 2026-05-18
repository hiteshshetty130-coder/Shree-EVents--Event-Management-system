import sqlite3
import datetime
from flask import flash

def get_connection():
    con=sqlite3.connect("database.db",timeout=30,check_same_thread=False)
    return con

def init_db():
    con=get_connection()
    cursor=con.cursor()

    # login table
    cursor.execute(""" CREATE TABLE IF NOT EXISTS login(login_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                PASSWORD TEXT NOT NULL)""")
    cursor.execute(""" INSERT OR IGNORE INTO login(username,password)VALUES('SHREEEVENTS','SANATHRASHMI22')""")

    # events table
    cursor.execute(""" CREATE TABLE IF NOT EXISTS events(event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                event_date DATETIME NOT NULL,
                event_time DATETIME NOT NULL,
                place TEXT NOT NULL,
                cust TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                event_status TEXT DEFAULT 'upcoming',
                phone_number INTEGER NOT NULL
                )""")

    # inventory item adding table
    cursor.execute(""" CREATE TABLE IF NOT EXISTS inventory(item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   item_name TEXT UNIQUE NOT NULL,
                   item_quantity INTEGER NOT NULL,
                   item_price INTEGER NOT NULL)""")

    # inventory allocation table
    cursor.execute(""" CREATE TABLE IF NOT EXISTS allocation(id INTEGER PRIMARY KEY AUTOINCREMENT,
                   event_id INTEGER,
                   item_id INTEGER,
                   item_name TEXT,
                   price_per_unit DECIMAL,
                   total_price DECIMAL,
                   quantity INTEGER NOT NULL,
                   event_date DATETIME NOT NULL)""")

    con.commit()
    con.close()

# login checking
def check_user(username,password):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT * FROM login WHERE username=? AND password=?",(username,password))
    user=cursor.fetchone()
    con.close()
    return user

# monthly events data
def dashboard_data():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT COUNT(*) FROM events WHERE strftime('%m',event_date)=strftime('%m','now') AND strftime('%Y',event_date)=strftime('%Y','now')")
    cleared=cursor.fetchone()[0]
    con.commit()
    con.close()
    return cleared if cleared else 0

# total sales card data
def dashboard_total_sales():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT SUM(total_price) FROM allocation")
    pending=cursor.fetchone()[0]
    con.commit()
    con.close()
    return pending if pending else 0

# total events book data
def dashboard_total_events():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events=cursor.fetchone()[0]
    con.commit()
    con.close()
    return total_events

# upcoming events date wise
def dashboard_upcoming_data():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT event_name,event_date,event_time FROM events WHERE event_date>DATE('now') ORDER BY event_date ASC")
    upcoming_events=cursor.fetchall()
    con.commit()
    con.close()
    return upcoming_events

# charts data using joins
def charts_data():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT strftime('%m',events.event_date)as month,SUM(allocation.total_price) FROM allocation JOIN events ON allocation.event_id=events.event_id GROUP BY month")
    data=cursor.fetchall()
    return data

# event creation
def create_events(event_name,date,time,place,cust,phone_number):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("INSERT INTO events(event_name,event_date,event_time,place,cust,phone_number)VALUES(?,?,?,?,?,?)",(event_name,date,time,place,cust,phone_number))
    con.commit()
    con.close()

# events list
def events_list():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT event_id,event_name,event_date,event_time,place,cust,phone_number FROM events WHERE event_date>=DATE('now') ORDER BY event_id DESC")
    events_li=cursor.fetchall()
    con.commit()
    con.close()
    return events_li

# events list for inventory allocation (pending only)
def events_list_in():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT event_id,event_name,event_date,event_time,place,cust,phone_number FROM events WHERE status='pending'")
    events_li=cursor.fetchall()
    con.commit()
    con.close()
    return events_li

# delete event — no stock return needed since we never deduct upfront
def delete_events(event_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("DELETE FROM allocation WHERE event_id=?",(event_id,))
    cursor.execute("DELETE FROM events WHERE event_id=?",(event_id,))
    con.commit()
    con.close()

# update event
def update_events(id,name,date,time,place,cust,phone):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("UPDATE events SET event_name=?,event_date=?,event_time=?,place=?,cust=?,phone_number=? WHERE event_id=?",(name,date,time,place,cust,phone,id))
    con.commit()
    con.close()

# add inventory item
def add_inventory(name,quantity,price):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("INSERT INTO inventory(item_name,item_quantity,item_price)VALUES(?,?,?)",(name,quantity,price))
    con.commit()
    con.close()

# get inventory
# if event_date passed → deduct only items allocated to events on THAT same date
# if no event_date → show full stock (no deduction)
def get_inventory(event_date=None):
    con=get_connection()
    cursor=con.cursor()
    if event_date:
        cursor.execute("""
            SELECT
                i.item_id,
                i.item_name,
                i.item_quantity - COALESCE(SUM(CASE
                    WHEN a.event_date = ? THEN a.quantity
                    ELSE 0
                END), 0) AS available_quantity,
                i.item_price
            FROM inventory i
            LEFT JOIN allocation a ON i.item_id = a.item_id
            GROUP BY i.item_id, i.item_name, i.item_quantity, i.item_price
        """, (event_date,))
    else:
        cursor.execute("SELECT item_id, item_name, item_quantity, item_price FROM inventory")
    inven_data=cursor.fetchall()
    con.close()
    return inven_data

def delete_inventory_item(item_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("DELETE FROM inventory WHERE item_id=?",(item_id,))
    con.commit()
    con.close()

# search inventory
def search_inventory(search):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT item_id,item_name,item_quantity FROM inventory WHERE LOWER(item_name) LIKE LOWER(?)",(f"%{search}%",))
    search_data=cursor.fetchall()
    con.commit()
    con.close()
    return search_data

# get allocated events (upcoming only)
def allocated_events():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT * FROM events WHERE status='allocated' AND event_date>DATE('now') ORDER BY event_id DESC")
    pen_data=cursor.fetchall()
    con.commit()
    con.close()
    return pen_data

# payments — all allocated events
def allocated_orders_events():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT * FROM events WHERE status='allocated' ORDER BY event_id DESC")
    pen_data=cursor.fetchall()
    con.commit()
    con.close()
    return pen_data

# orders sorted by date
def allocated_list_events():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT * FROM events WHERE status='allocated' ORDER BY event_date DESC")
    pen_data=cursor.fetchall()
    con.commit()
    con.close()
    return pen_data

# allocated inventory list
def allocated_inventory_list():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT e.event_id,e.event_name,i.item_name,a.price_per_unit,a.quantity,a.total_price,a.item_id,e.event_date FROM allocation a JOIN events e ON e.event_id=a.event_id JOIN inventory i ON i.item_id=a.item_id WHERE e.event_date>DATE('now')")
    join_data=cursor.fetchall()
    con.commit()
    con.close()
    return join_data

# status update after allocation
def update_status(event_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("UPDATE events SET status='allocated' WHERE event_id=?",(event_id,))
    con.commit()
    con.close()

# delete allocation row
def delete_inventory(event_id,item_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("DELETE FROM allocation WHERE event_id=? AND item_id=?",(event_id,item_id))
    con.commit()
    con.close()

# total amount per event
def total_mount_calculations():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT event_id,SUM(quantity*price_per_unit)AS total FROM allocation GROUP BY event_id")
    total_data=cursor.fetchall()
    con.commit()
    con.close()
    return total_data

# update allocation — never touches inventory.item_quantity
# stock check is done against the event date's available quantity
def update_allocation(event_id, item_id, quantity, name, price):
    con=get_connection()
    cursor=con.cursor()

    # get old allocated quantity for this event+item
    cursor.execute("SELECT quantity FROM allocation WHERE event_id=? AND item_id=?",(event_id,item_id))
    row=cursor.fetchone()
    old_qty=row[0] if row else 0

    # get this event's date
    cursor.execute("SELECT event_date FROM events WHERE event_id=?",(event_id,))
    event_date=cursor.fetchone()[0]

    # stock check — only if increasing quantity
    if quantity > old_qty:
        # available = total stock minus all allocations on that same event date
        cursor.execute("""
            SELECT i.item_quantity - COALESCE(SUM(CASE
                WHEN a.event_date = ? THEN a.quantity
                ELSE 0
            END), 0)
            FROM inventory i
            LEFT JOIN allocation a ON i.item_id = a.item_id
            WHERE i.item_id = ?
            GROUP BY i.item_id
        """, (event_date, item_id))
        result=cursor.fetchone()
        available=result[0] if result else 0
        if (quantity - old_qty) > available:
            con.close()
            return "Not enough stock"

    # update allocation only — never touch inventory table
    if quantity == 0:
        cursor.execute("DELETE FROM allocation WHERE event_id=? AND item_id=?",(event_id,item_id))
    elif row:
        cursor.execute(
            "UPDATE allocation SET quantity=?, total_price=? WHERE event_id=? AND item_id=?",
            (quantity, quantity*price, event_id, item_id)
        )
    else:
        cursor.execute("""
            INSERT INTO allocation(event_id,item_id,quantity,item_name,price_per_unit,total_price,event_date)
            VALUES(?,?,?,?,?,?,?)
        """, (event_id, item_id, quantity, name, price, quantity*price, event_date))

    con.commit()
    con.close()

# get event by id for billing
def get_event_by_id(event_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id=?",(event_id,))
    event_by_id=cursor.fetchone()
    con.commit()
    con.close()
    return event_by_id

# get allocated items by event id
def get_item_by_id(event_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT * FROM allocation WHERE event_id=?",(event_id,))
    data=cursor.fetchall()
    con.commit()
    con.close()
    return data

# get total price for event
def total_by_item(event_id):
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("SELECT SUM(quantity*price_per_unit)FROM allocation WHERE event_id=?",(event_id,))
    data=cursor.fetchone()[0] or 0
    con.commit()
    con.close()
    return data

# update event status upcoming/completed
def event_status_change():
    con=get_connection()
    cursor=con.cursor()
    cursor.execute("UPDATE events SET event_status='completed' WHERE event_date<DATE('now')")
    cursor.execute("UPDATE events SET event_status='upcoming' WHERE event_date>=DATE('now')")
    con.commit()
    con.close()

def update_inventory_item(item_id, name, quantity, price):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("UPDATE inventory SET item_name=?, item_quantity=?, item_price=? WHERE item_id=?",
                   (name, quantity, price, item_id))
    con.commit()
    con.close()