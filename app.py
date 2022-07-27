import csv

from models import Base, session, Brand, Product, engine
from cleaners import clean_price, clean_quantity, clean_date


def add_csv():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            brand_exists = session.query(Brand).filter(
                Brand.brand_name == row[0]).one_or_none()
            if brand_exists == None:
                brand = Brand(brand_name=row[0])
                session.add(brand)
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:
            already_exists = session.query(Product).filter(
                Product.product_name == row[0]).one_or_none()
            if already_exists == None:
                name = row[0]
                price = clean_price(row[1])
                quantity = clean_quantity(row[2])
                date_updated = clean_date(row[3])
                new_product = Product(product_name=name, product_price=price,
                                      product_quantity=quantity, date_updated=date_updated)
                session.add(new_product)
        session.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
