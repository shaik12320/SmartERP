import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from reportlab.pdfgen import canvas
from io import BytesIO
from models import db, Company, Customer, Supplier, Product, Sale, Purchase, User, FinancialYear

app = Flask(__name__, template_folder="templates")
app.secret_key = "smarterp_secret_2026"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smarterp.db"
print("DATABASE URI =", app.config["SQLALCHEMY_DATABASE_URI"])

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ INIT DB
db.init_app(app)
import os

print("DATABASE URI =", app.config["SQLALCHEMY_DATABASE_URI"])
print("CURRENT FOLDER =", os.getcwd())

with app.app_context():
    db.create_all()
    print("DATABASE CREATED SUCCESSFULLY")
    print("CURRENT FOLDER:", os.getcwd())
    print("INSTANCE PATH:", app.instance_path)


@app.route("/")
def home():
    return flask.render_template("index.html")


from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():

    if flask.request.method == "POST":

        email = flask.request.form["email"]
        password = flask.request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            flask.session["user_id"] = user.id
            flask.session["user_name"] = user.name

            return flask.redirect(flask.url_for("dashboard"))

        flask.flash("Invalid Email or Password")

    return flask.render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if flask.request.method == "POST":

        user = User(
            name=flask.request.form["name"],
            email=flask.request.form["email"],
            password=generate_password_hash(
                flask.request.form["password"]
            )
        )

        db.session.add(user)
        db.session.commit()

        return flask.redirect(flask.url_for("login"))

    return flask.render_template("register.html")


@app.route("/logout")
def logout():

    flask.session.clear()

    return flask.redirect(flask.url_for("login"))

@app.route("/dashboard")
def dashboard():

    # 🔐 LOGIN CHECK
    if "user_id" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    # 🏢 COMPANY CHECK
    if "company_id" not in flask.session:
        flask.flash("Please select a company first")
        return flask.redirect(flask.url_for("company"))

    # 📅 FINANCIAL YEAR CHECK
    if "financial_year_id" not in flask.session:
        flask.flash("Please select financial year first")
        return flask.redirect(flask.url_for("financial_year"))

    company_id = flask.session["company_id"]
    fy_id = flask.session["financial_year_id"]

    # 📊 FILTERED DATA (IMPORTANT ERP PART)
    total_customers = Customer.query.filter_by(
        company_id=company_id,
        financial_year_id=fy_id
    ).count()

    total_suppliers = Supplier.query.filter_by(
        company_id=company_id,
        financial_year_id=fy_id
    ).count()

    total_products = Product.query.filter_by(
        company_id=company_id,
        financial_year_id=fy_id
    ).count()

    total_sales = Sale.query.filter_by(
        company_id=company_id,
        financial_year_id=fy_id
    ).count()

    total_purchases = Purchase.query.filter_by(
        company_id=company_id,
        financial_year_id=fy_id
    ).count()

    # 🖥️ SEND TO TEMPLATE
    return flask.render_template(
        "dashboard.html",
        total_customers=total_customers,
        total_suppliers=total_suppliers,
        total_products=total_products,
        total_sales=total_sales,
        total_purchases=total_purchases,
        company_name=flask.session.get("company_name"),
        financial_year_name=flask.session.get("financial_year_name")
    )

@app.route("/select_company/<int:id>")
def select_company(id):

    company = Company.query.get_or_404(id)

    flask.session["company_id"] = company.id
    flask.session["company_name"] = company.company_name

    return flask.redirect(flask.url_for("dashboard"))

@app.route("/company")
def company():

    companies = Company.query.all()

    return flask.render_template(
        "company.html",
        companies=companies
    )


@app.route("/add_company", methods=["POST"])
def add_company():

    company = Company(
        company_name=flask.request.form["company_name"],
        owner_name=flask.request.form["owner_name"],
        gst_number=flask.request.form["gst_number"],
        phone=flask.request.form["phone"],
        email=flask.request.form["email"],
        website=flask.request.form["website"],
        address=flask.request.form["address"],
        pincode=flask.request.form["pincode"]
    )

    db.session.add(company)
    db.session.commit()

    return flask.redirect(flask.url_for("company"))


@app.route("/edit_company/<int:id>", methods=["GET", "POST"])
def edit_company(id):

    company = Company.query.get_or_404(id)

    if flask.request.method == "POST":

        company.company_name = flask.request.form["company_name"]
        company.owner_name = flask.request.form["owner_name"]
        company.gst_number = flask.request.form["gst_number"]
        company.phone = flask.request.form["phone"]
        company.email = flask.request.form["email"]
        company.website = flask.request.form["website"]
        company.address = flask.request.form["address"]
        company.pincode = flask.request.form["pincode"]

        db.session.commit()

        return flask.redirect(flask.url_for("company"))

    return flask.render_template(
        "edit_company.html",
        company=company
    )


@app.route("/delete_company/<int:id>")
def delete_company(id):

    company = Company.query.get_or_404(id)

    db.session.delete(company)
    db.session.commit()

    return flask.redirect(flask.url_for("company"))

@app.route("/customers")
def customers_page():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    customers = Customer.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    return flask.render_template("customer.html", customers=customers)

@app.route("/add_customer", methods=["POST"])
def add_customer():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    customer = Customer(
        name=flask.request.form["name"],
        mobile=flask.request.form["mobile"],
        email=flask.request.form["email"],
        address=flask.request.form["address"],

        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    )

    db.session.add(customer)
    db.session.commit()

    return flask.redirect(flask.url_for("customers_page"))


@app.route("/edit_customer/<int:id>", methods=["GET", "POST"])
def edit_customer(id):

    customer = Customer.query.filter_by(
    id=id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first_or_404()

    if flask.request.method == "POST":
        customer.name = flask.request.form["name"]
        customer.mobile = flask.request.form["mobile"]
        customer.email = flask.request.form["email"]
        customer.address = flask.request.form["address"]

        db.session.commit()

        return flask.redirect(flask.url_for("customers_page"))

    return flask.render_template(
        "edit_customer.html",
        customer=customer
    )


@app.route("/delete_customer/<int:id>")
def delete_customer(id):

    customer = Customer.query.filter_by(
    id=id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first_or_404()

    db.session.delete(customer)
    db.session.commit()

    return flask.redirect(flask.url_for("customers_page"))

@app.route("/suppliers")
def suppliers():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    suppliers = Supplier.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    return flask.render_template(
        "suppliers.html",
        suppliers=suppliers
    )

@app.route("/add_supplier", methods=["POST"])
def add_supplier():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))
    
    supplier = Supplier(
        name=flask.request.form["name"],
        mobile=flask.request.form["mobile"],
        email=flask.request.form["email"],
        address=flask.request.form["address"],

        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    )

    db.session.add(supplier)
    db.session.commit()

    return flask.redirect(flask.url_for("suppliers"))

@app.route("/edit_supplier/<int:id>", methods=["GET", "POST"])
def edit_supplier(id):

    supplier = Supplier.query.filter_by(
    id=id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first_or_404()

    if flask.request.method == "POST":
        supplier.name = flask.request.form["name"]
        supplier.mobile = flask.request.form["mobile"]
        supplier.email = flask.request.form["email"]
        supplier.address = flask.request.form["address"]

        db.session.commit()

        return flask.redirect(flask.url_for("suppliers"))

    return flask.render_template(
        "edit_supplier.html",
        supplier=supplier
    )

@app.route("/delete_supplier/<int:id>")
def delete_supplier(id):

    supplier = Supplier.query.filter_by(
    id=id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first_or_404()

    db.session.delete(supplier)
    db.session.commit()

    return flask.redirect(flask.url_for("suppliers"))

@app.route("/inventory")
def inventory():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    products = Product.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    return flask.render_template(
        "inventory.html",
        products=products
    )

@app.route("/add_product", methods=["POST"])
def add_product():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))


    product = Product(
        product_name=flask.request.form["product_name"],
        category=flask.request.form["category"],
        quantity=int(flask.request.form["quantity"]),
        price=float(flask.request.form["price"]),

        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    )

    db.session.add(product)
    db.session.commit()

    return flask.redirect(flask.url_for("inventory"))

@app.route("/edit_product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    # session check (IMPORTANT)
    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    product = Product.query.filter_by(
    id=id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first_or_404()
    
    if flask.request.method == "POST":

        product.product_name = flask.request.form["product_name"]
        product.category = flask.request.form["category"]
        product.quantity = int(flask.request.form["quantity"])
        product.price = float(flask.request.form["price"])

        db.session.commit()

        return flask.redirect(flask.url_for("inventory"))

    return flask.render_template(
        "edit_product.html",
        product=product
    )

@app.route("/delete_product/<int:id>")
def delete_product(id):

    product = Product.query.filter_by(
    id=id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first_or_404()

    db.session.delete(product)
    db.session.commit()

    return flask.redirect(flask.url_for("inventory"))

@app.route("/sales")
def sales():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    sales = Sale.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    products = Product.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    return flask.render_template(
        "sales.html",
        sales=sales,
        products=products
    )

@app.route("/add_sale", methods=["POST"])
def add_sale():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    product_id = int(flask.request.form["product_id"])
    quantity = int(flask.request.form["quantity"])

    product = Product.query.filter_by(
    id=product_id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first()

    if product and product.quantity >= quantity:

        total = product.price * quantity

        sale = Sale(
    invoice_no=flask.request.form["invoice_no"],
    invoice_date=flask.request.form["invoice_date"],
    customer_name=flask.request.form["customer_name"],
    product_name=product.product_name,
    quantity=quantity,
    total_amount=total,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
)


        product.quantity -= quantity

        db.session.add(sale)
        db.session.commit()

    return flask.redirect(flask.url_for("sales"))

@app.route("/purchase")
def purchase():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    purchases = Purchase.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    products = Product.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).all()

    return flask.render_template(
        "purchase.html",
        purchases=purchases,
        products=products
    )

@app.route("/add_purchase", methods=["POST"])
def add_purchase():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    product_id = int(flask.request.form["product_id"])
    quantity = int(flask.request.form["quantity"])

    product = Product.query.filter_by(
    id=product_id,
    company_id=flask.session["company_id"],
    financial_year_id=flask.session["financial_year_id"]
).first()

    if product:

        total = product.price * quantity

        purchase = Purchase(
            supplier_name=flask.request.form["supplier_name"],
            product_name=product.product_name,
            quantity=quantity,
            total_amount=total,

            company_id=flask.session["company_id"],
            financial_year_id=flask.session["financial_year_id"]
        )

        product.quantity += quantity

        db.session.add(purchase)
        db.session.commit()

    return flask.redirect(flask.url_for("purchase"))

@app.route("/reports")
def reports():

    if "company_id" not in flask.session:
        return flask.redirect(flask.url_for("company"))

    if "financial_year_id" not in flask.session:
        return flask.redirect(flask.url_for("financial_year"))

    total_customers = Customer.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).count()

    total_suppliers = Supplier.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).count()

    total_products = Product.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).count()

    total_sales = Sale.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).count()

    total_purchases = Purchase.query.filter_by(
        company_id=flask.session["company_id"],
        financial_year_id=flask.session["financial_year_id"]
    ).count()

    return flask.render_template(
        "reports.html",
        total_customers=total_customers,
        total_suppliers=total_suppliers,
        total_products=total_products,
        total_sales=total_sales,
        total_purchases=total_purchases
    )

@app.route("/financial_year")
def financial_year():

    years = FinancialYear.query.all()

    return flask.render_template(
        "financial_year.html",
        years=years
    )


@app.route("/add_financial_year", methods=["POST"])
def add_financial_year():

    fy = FinancialYear(
        year_name=flask.request.form["year_name"],
        start_date=flask.request.form["start_date"],
        end_date=flask.request.form["end_date"]
    )

    db.session.add(fy)
    db.session.commit()

    return flask.redirect(flask.url_for("financial_year"))

@app.route("/select_financial_year/<int:id>")
def select_financial_year(id):

    fy = FinancialYear.query.get_or_404(id)

    flask.session["financial_year_id"] = fy.id
    flask.session["financial_year_name"] = fy.year_name

    return flask.redirect(flask.url_for("dashboard"))

@app.route("/invoice/<int:id>")
def invoice(id):
    sale = Sale.query.get_or_404(id)
    return flask.render_template("invoice.html", sale=sale)

from reportlab.pdfgen import canvas
from io import BytesIO
from flask import make_response

@app.route("/invoice/pdf/<int:id>")
def invoice_pdf(id):
    sale = Sale.query.get_or_404(id)

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 800, f"Invoice ID: {sale.id}")
    p.drawString(100, 780, f"Customer: {sale.customer_name}")
    p.drawString(100, 760, f"Total: {sale.total_amount}")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=invoice_{id}.pdf"

    return response

@app.route("/download-pdf/<int:id>")

def download_invoice():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 800, "SMART ERP INVOICE")
    p.drawString(100, 780, "Thank you for your purchase")

    p.showPage()
    p.save()

    buffer.seek(0)

    return make_response(buffer.getvalue(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=invoice.pdf"
    })
if __name__ == "__main__":
    app.run(debug=True)