import csv
import time
import datetime

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
    \rProduct Price: \t${product.product_price / 100}
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
    date_updated = datetime.datetime.now().date()
    brand = input("\rBrand: ")
    brand_exists = session.query(Brand).filter(
        Brand.brand_name == brand).first()
    if brand_exists:
        brand_id = brand_exists.brand_id
    else:
        new_brand = Brand(brand_name=brand)
        session.add(new_brand)
        session.commit()
        brand_id = new_brand.brand_id
    new_product = Product(product_name=name, product_quantity=quantity,
                          product_price=price, date_updated=date_updated,
                          brand_id=brand_id)
    existing_product = session.query(
        Product).filter(Product.product_name == new_product.product_name
                        ).first()
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
    print(f"Current Name: {product.product_name}")
    new_name = input("Provide a new Name: ")
    print(f"Current Price: ${product.product_price / 100}")
    price_error = True
    while price_error:
        new_price = input("Provide a new Price: $")
        new_price = clean_price(new_price)
        if type(new_price) == int:
            price_error = False
    print(f"Current Quantity: {product.product_quantity}")
    quantity_error = True
    while quantity_error:
        new_quantity = input("Provide a new quantity: ")
        new_quantity = clean_quantity(new_quantity)
        if type(new_quantity) == int:
            quantity_error = False
    product.product_name = new_name
    product.product_price = new_price
    product.product_quantity = new_quantity
    product.date_updated = datetime.datetime.now().date()

    session.commit()
    input('''
    \rProduct succesfully updated!
    \rPress enter to go back to the main menu''')


def delete_product(product):
    confirm = input("Are you sure you want to delete this product? Y/N ")
    if confirm.lower() == 'y':
        session.delete(product)
        session.commit()
        print("\nProduct successfully deleted")
        input("Press enter to go back to the main menu ")


def analysis():
    products = session.query(Product)
    brands = session.query(Brand)
    number_of_products = products.count()
    number_of_brands = brands.count()
    most_expensive = products.order_by(
        Product.product_price.desc()).first()
    least_expensive = products.order_by(
        Product.product_price).first()
    # https://stackoverflow.com/questions/28033656/finding-most-frequent-values-in-column-of-array-in-sql-alchemy
    most_common_brand_id, occurances = session.query(
        Product.brand_id, func.count(Product.product_id).label('qty')
        ).group_by('brand_id').order_by(desc('qty')).first()
    most_common_brand = session.query(
        Brand).filter_by(brand_id=most_common_brand_id
                         ).one_or_none().brand_name
    print(f"""
    \rTotal Products: {number_of_products}
    \rTotal Brands: {number_of_brands}
    \rMost Expensive: {most_expensive.product_name}
    \rLeast Expensive: {least_expensive.product_name}
    \rMost Popular Brand: {most_common_brand} with {occurances} products""")
    time.sleep(2)


def create_backup():
    with open('backup_inventory.csv', 'w') as file:
        fieldnames = ['product_name', 'product_price',
                      'product_quantity', 'date_updated',
                      'brand_name']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        products = session.query(Product).all()
        for product in products:
            price = "{:.2f}".format(product.product_price / 100)
            writer.writerow({
                    fieldnames[0]: product.product_name,
                    fieldnames[1]: f"${price}",
                    fieldnames[2]: product.product_quantity,
                    fieldnames[3]: product.date_updated.strftime("%m/%d/%Y"),
                    fieldnames[4]: product.brand.brand_name})
    print("\nSuccessfully created a backup of the inventory")
    with open('backup_brands.csv', 'w') as file:
        fieldnames = ['brand_id', 'brand_name']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        brands = session.query(Brand).all()
        for brand in brands:
            writer.writerow({
                                fieldnames[0]: brand.brand_id,
                                fieldnames[1]: brand.brand_name
                            })
    print("\nSuccessfully created a backup of the brands")


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
                                      product_quantity=quantity,
                                      date_updated=date_updated,
                                      brand_id=brand_id)
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
        elif choice == 'b':
            create_backup()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    app()
