import csv
import time

from models import Base, session, Brand, Product, engine
from cleaners import clean_price, clean_quantity, clean_date
from sqlalchemy import func, desc


def main_menu():
    '''
    Display the main menu and get the user's input.
    '''
    while True:
        print("""
        \nWelcome to the inventory management system!
        \rPlease select an option:
        \n V - View single product
        \r N - Add a new product
        \r A - view an Analysis
        \r B - Make a backup""")
        choice = input("\rEnter your choice: ").lower()
        if choice in ['v', 'n', 'a', 'b']:
            return choice
        else:
            input("""
            \n***** INVALID INPUT *****
            \rPlease enter a valid option.
            \rPress enter to try again.""")


def product_menu():
    while True:
        print('''
            \r**** PRODUCT Menu ****
            \r1) Delete this product
            \r2) Update this Product
            \r3) Back to main menu''')
        choice = input("\nWhat would you like to do? ").lower()
        if choice in ['1', '2', '3']:
            return choice
        else:
            input('''
                \rPlease choose one of the options above..
                \rPress enter to try again''')


def print_product(product):
    print(f"""
    \rProduct ID: \t{product.product_id}
    \rProduct Name: \t{product.product_name}
    \rBrand Name: \t{product.brand.brand_name}
    \rProduct Qty: \t{product.product_quantity}
    \rProduct Price: \t{product.product_price}
    \rDate Updated: \t{product.date_updated.strftime("%m/%d/%Y")}""")


def read_product():
    id_options = []
    for product in session.query(Product):
        id_options.append(product.product_id)
    id_error = True
    while id_error:
        choice = input(f"""
        \nID options: {id_options}
        \rProduct ID: """)
        try:
            product_id = int(choice)
        except ValueError:
            input("""
            \n***** INVALID INPUT *****
            \rPlease enter a valid ID.
            \rPress enter to try again.""")
        else:
            if product_id in id_options:
                id_error = False
            else:
                input("""
                \n***** INVALID INPUT *****
                \rPlease enter a valid ID.
                \rPress enter to try again.""")
    product = session.query(Product).filter_by(product_id=choice).first()
    print_product(product)
    choice = product_menu()
    if choice == '1':
        delete_product(product)
    elif choice == '2':
        update_product(product)


def create_product():
    name = input("\rProduct Name: ")
    price_error = True
    while price_error:
        price = input("\rProduct Price: ")
        price = clean_price(price)
        if type(price) == int:
            price_error = False
    quantity_error = True
    while quantity_error:
        quantity = input("\rProduct Quantity: ")
        quantity = clean_quantity(quantity)
        if type(quantity) == int:
            quantity_error = False
    date_error = True
    while date_error:
        date_updated = input("\rDate Updated: ")
        try:
            date_updated = clean_date(date_updated)
        except ValueError:
            input('''
                \n**** DATE ERROR ****
                \rThe date format should include a valid DD/MM/YYYY format from the past
                \rEx: 4/28/2021
                \rPress enter to try again.
                \r*******************''')
        else:
            date_error = False
    brand = input("\rBrand: ")
    brand_exists = session.query(Brand).filter(
        Brand.brand_name == brand).first()
    if brand_exists:
        brand_id = brand_exists.brand_id
    else:
        brand_id = session.query(Brand).count() + 1
        new_brand = Brand(brand_id=brand_id, brand_name=brand)
        session.add(new_brand)
    new_product = Product(product_name=name, product_quantity=quantity,
                          product_price=price, date_updated=date_updated,
                          brand_id=brand_id)
    existing_product = session.query(Product).filter(Product.product_name == new_product.product_name).first()
    if existing_product:
        existing_product.product_name = name
        existing_product.product_price = price
        existing_product.product_quantity = quantity
        existing_product.date_updated = date_updated
        existing_product.brand_id = brand_id
    else:
        session.add(new_product)
    session.commit()
    print("\rProduct added!")


def update_product(product):
    print('updating product')
    '''
    Update an existing product
    '''
    product.product_name = input("Provide a new Name")

    time.sleep(2)


def delete_product(product):
    print('deleting product')
    time.sleep(2)


def analysis():
    most_expensive = session.query(Product).order_by(
        Product.product_price.desc()).first()
    least_expensive = session.query(Product).order_by(
        Product.product_price).first()
    most_popular_brand = session.query(Product).order_by(
        desc(func.count(Product.brand_id))).first()
    least_popular_brand = session.query(Product).order_by(
        func.count(Product.brand_id)).first()
    print(f"""
    \rMost Expensive: {most_expensive.product_name}
    \rLeast Expensive: {least_expensive.product_name}
    \rMost Popular Brand: {most_popular_brand}""")
    time.sleep(2)


def add_csv():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            brand_exists = session.query(Brand).filter(
                Brand.brand_name == row[0]).one_or_none()
            if brand_exists is None:
                brand = Brand(brand_name=row[0])
                session.add(brand)
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:
            already_exists = session.query(Product).filter(
                Product.product_name == row[0]).one_or_none()
            if already_exists is None:
                name = row[0]
                price = clean_price(row[1])
                quantity = clean_quantity(row[2])
                date_updated = clean_date(row[3])
                brand_id = session.query(Brand).filter(
                    Brand.brand_name == row[4]).one().brand_id
                new_product = Product(product_name=name, product_price=price,
                                      product_quantity=quantity, date_updated=date_updated, brand_id=brand_id)
                session.add(new_product)
        session.commit()


def app():
    app_running = True
    while app_running:
        choice = main_menu()
        if choice == 'v':
            read_product()
        elif choice == 'n':
            create_product()
        elif choice == 'a':
            analysis()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    app()
