from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(100))
    owner_name = db.Column(db.String(100))
    gst_number = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    address = db.Column(db.Text)
    pincode = db.Column(db.String(20))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)

    company_id = db.Column(db.Integer)
    financial_year_id = db.Column(db.Integer)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)

    company_id = db.Column(db.Integer)
    financial_year_id = db.Column(db.Integer)   

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    company_id = db.Column(db.Integer)
    financial_year_id = db.Column(db.Integer) 


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    invoice_no = db.Column(db.String(50))
    invoice_date = db.Column(db.String(50))

    customer_name = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_amount = db.Column(db.Float)

    company_id = db.Column(db.Integer)
    financial_year_id = db.Column(db.Integer)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    supplier_name = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_amount = db.Column(db.Float)

    company_id = db.Column(db.Integer)
    financial_year_id = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))

class FinancialYear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_name = db.Column(db.String(50))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))