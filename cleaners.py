import datetime


def clean_price(string):
    print(string)
    string = string.replace('$', '')
    try:
        price = float(string)
    except ValueError:
        input('''
        \n***** PRICE ERROR *****
        \rThe price should be a number with a dollar symbol.
        \rEx: $2.99
        \rPress enter to try again.
        \r**********************''')
    return (int(price * 100))


def clean_quantity(quantity_str):
    try:
        product_quantity = int(quantity_str)
    except ValueError:
        input('''
                \n**** QUANTITY ERROR ****
                \rThe quantity should be a number.
                \rPress enter to try again.
                \r********************''')
        return
    else:
        return product_quantity


def clean_date(string):
    month, day, year = string.split('/')
    return datetime.date(int(year), int(month), int(day))
