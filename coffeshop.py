import csv
import os
from pathlib import Path

Product = dict[str, str]

CSV_FILE = Path(__file__).parent / "coffee.csv"
SALES_FILE = Path(__file__).parent / "sales.csv"
PRODUCT_FIELDS = ["ProductID", "ProductName", "Price", "Stock", "Sold"]
SALES_FIELDS = [
    "Rank",
    "ProductID",
    "ProductName",
    "UnitPrice",
    "UnitsSold",
    "Revenue",
    "StockLeft",
]
TABLE_LINE = "-" * 73
MENU_WIDTH = 38
OWNER_PASSWORD = os.environ.get("COFFEE_OWNER_PASSWORD", "admin123")
OWNER_PASSWORD_ATTEMPTS = 3


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _safe_int(value: object) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _safe_float(value: object) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def _normalize_key(key: object) -> str:
    return str(key).strip().lower().replace("_", " ")


def _normalize_row(row: dict[str, str]) -> Product:
    # Supports old CSV formats so existing files can still be read.
    keymap = {
        "productid": "ProductID",
        "id": "ProductID",
        "bookid": "ProductID",
        "productname": "ProductName",
        "product name": "ProductName",
        "coffee name": "ProductName",
        "coffee": "ProductName",
        "name": "ProductName",
        "title": "ProductName",
        "price": "Price",
        "amount": "Price",
        "author": "Price",
        "stock": "Stock",
        "stocks": "Stock",
        "total stocks": "Stock",
        "quantity": "Stock",
        "sold": "Sold",
        "borrowed": "Sold",
    }
    normalized = {"ProductID": "", "ProductName": "", "Price": "0.00", "Stock": "0", "Sold": "0"}

    for key, value in row.items():
        if key is None:
            continue
        mapped = keymap.get(_normalize_key(key))
        if mapped:
            normalized[mapped] = str(value or "").strip()

    normalized["Price"] = f"{max(0.0, _safe_float(normalized['Price'])):.2f}"
    normalized["Stock"] = str(max(0, _safe_int(normalized["Stock"])))
    normalized["Sold"] = str(max(0, _safe_int(normalized["Sold"])))
    return normalized


def _ensure_valid_ids(products: list[Product]) -> None:
    used_ids = set()
    next_id = 1

    for product in products:
        raw_id = _safe_int(product.get("ProductID", 0))
        if raw_id <= 0 or raw_id in used_ids:
            while next_id in used_ids:
                next_id += 1
            raw_id = next_id
        used_ids.add(raw_id)
        product["ProductID"] = str(raw_id)


def read_products() -> list[Product]:
    products: list[Product] = []
    if CSV_FILE.exists():
        with open(CSV_FILE, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                normalized = _normalize_row(row)
                if normalized["ProductName"]:
                    products.append(normalized)

    _ensure_valid_ids(products)
    return products


def write_products(products: list[Product]) -> None:
    _ensure_valid_ids(products)
    products.sort(key=lambda item: _safe_int(item.get("ProductID", 0)))

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=PRODUCT_FIELDS)
        writer.writeheader()
        writer.writerows(products)


def next_product_id(products: list[Product]) -> int:
    highest = 0
    for product in products:
        highest = max(highest, _safe_int(product.get("ProductID", 0)))
    return highest + 1


def read_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("\n  Value cannot be empty.")


def read_non_negative_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("\n  Value must be zero or greater.")
                continue
            return value
        except ValueError:
            print("\n  Invalid number. Please try again.")


def read_non_negative_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value < 0:
                print("\n  Value must be zero or greater.")
                continue
            return value
        except ValueError:
            print("\n  Invalid number. Please try again.")


def read_positive_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value <= 0:
                print("\n  Value must be greater than 0.")
                continue
            return value
        except ValueError:
            print("\n  Invalid number. Please try again.")


def authenticate_owner() -> bool:
    print("\n  Owner authentication required.")
    for attempt in range(1, OWNER_PASSWORD_ATTEMPTS + 1):
        password = input("  Enter owner password: ").strip()
        if password == OWNER_PASSWORD:
            print("\n  Access granted.\n")
            return True

        remaining = OWNER_PASSWORD_ATTEMPTS - attempt
        if remaining > 0:
            print(f"\n  Incorrect password. Attempts left: {remaining}")
        else:
            print("\n  Incorrect password. Returning to role selection.\n")

    return False


def display_products(products: list[Product]) -> None:
    print(f"\n  {'ID':<5}{'PRODUCT':<26}{'PRICE':>10}{'STOCK':>10}{'SOLD':>10}")
    print("  " + "-" * 61)
    for product in products:
        price = _safe_float(product.get("Price", 0))
        stock = _safe_int(product.get("Stock", 0))
        sold = _safe_int(product.get("Sold", 0))
        print(
            f"  {product.get('ProductID', ''):<5}"
            f"{product.get('ProductName', '')[:25]:<26}"
            f"{price:>10.2f}{stock:>10}{sold:>10}"
        )
    print()


def display_customer_products(products: list[Product]) -> None:
    available_products = [item for item in products if _safe_int(item.get("Stock", 0)) > 0]

    if not available_products:
        print("\n  No available products right now.\n")
        return

    print(f"\n  {'ID':<5}{'COFFEE':<26}{'PRICE':>10}{'AVAILABLE':>12}")
    print("  " + "-" * 53)
    for product in available_products:
        print(
            f"  {product.get('ProductID', ''):<5}"
            f"{product.get('ProductName', '')[:25]:<26}"
            f"{_safe_float(product.get('Price', 0)):>10.2f}"
            f"{_safe_int(product.get('Stock', 0)):>12}"
        )
    print()


def view_products() -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return
    display_products(products)


def view_customer_products() -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return
    display_customer_products(products)


def add_product() -> None:
    products = read_products()

    name = read_non_empty("  Enter product name: ")
    price = read_non_negative_float("  Enter price: ")
    stock = read_non_negative_int("  Enter stock quantity: ")

    product = {
        "ProductID": str(next_product_id(products)),
        "ProductName": name,
        "Price": f"{price:.2f}",
        "Stock": str(stock),
        "Sold": "0",
    }
    products.append(product)
    write_products(products)
    print(f"\n  Product added: {name} (ID {product['ProductID']}).\n")


def _find_product_by_id(products: list[Product], product_id: str) -> Product | None:
    for product in products:
        if product.get("ProductID") == product_id:
            return product
    return None


def _get_ranked_sales(products: list[Product]) -> list[Product]:
    sold_products = [item for item in products if _safe_int(item.get("Sold", 0)) > 0]
    ranked = sorted(
        sold_products,
        key=lambda item: (
            _safe_int(item.get("Sold", 0)),
            _safe_int(item.get("Sold", 0)) * _safe_float(item.get("Price", 0)),
        ),
        reverse=True,
    )
    return ranked


def write_sales_csv(products: list[Product]) -> None:
    ranked = _get_ranked_sales(products)

    with open(SALES_FILE, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SALES_FIELDS)
        writer.writeheader()

        for index, item in enumerate(ranked, start=1):
            units_sold = _safe_int(item.get("Sold", 0))
            unit_price = _safe_float(item.get("Price", 0))
            writer.writerow(
                {
                    "Rank": index,
                    "ProductID": item.get("ProductID", ""),
                    "ProductName": item.get("ProductName", ""),
                    "UnitPrice": f"{unit_price:.2f}",
                    "UnitsSold": units_sold,
                    "Revenue": f"{units_sold * unit_price:.2f}",
                    "StockLeft": _safe_int(item.get("Stock", 0)),
                }
            )


def edit_product() -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return

    display_products(products)
    product_id = input("  Enter product ID to edit: ").strip()
    product = _find_product_by_id(products, product_id)

    if not product:
        print(f"\n  Product ID {product_id} not found.\n")
        return

    current_name = product["ProductName"]
    current_price = _safe_float(product["Price"])
    current_stock = _safe_int(product["Stock"])

    new_name = input(f"  New name [{current_name}]: ").strip()
    if new_name:
        product["ProductName"] = new_name

    while True:
        new_price_raw = input(f"  New price [{current_price:.2f}]: ").strip()
        if not new_price_raw:
            break
        try:
            new_price = float(new_price_raw)
            if new_price < 0:
                print("\n  Value must be zero or greater.")
                continue
            product["Price"] = f"{new_price:.2f}"
            break
        except ValueError:
            print("\n  Invalid number. Please try again.")

    while True:
        new_stock_raw = input(f"  New stock [{current_stock}]: ").strip()
        if not new_stock_raw:
            break
        try:
            new_stock = int(new_stock_raw)
            if new_stock < 0:
                print("\n  Value must be zero or greater.")
                continue
            product["Stock"] = str(new_stock)
            break
        except ValueError:
            print("\n  Invalid number. Please try again.")

    write_products(products)
    print(f"\n  Product ID {product_id} updated.\n")


def delete_product() -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return

    display_products(products)
    product_id = input("  Enter product ID to delete: ").strip()
    product = _find_product_by_id(products, product_id)

    if not product:
        print(f"\n  Product ID {product_id} not found.\n")
        return

    confirm = input(f"  Delete '{product['ProductName']}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("\n  Delete cancelled.\n")
        return

    updated_products = [item for item in products if item.get("ProductID") != product_id]
    write_products(updated_products)
    print(f"\n  Product ID {product_id} deleted.\n")


def restock_product() -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return

    display_products(products)
    product_id = input("  Enter product ID to restock: ").strip()
    product = _find_product_by_id(products, product_id)

    if not product:
        print(f"\n  Product ID {product_id} not found.\n")
        return

    add_qty = read_positive_int("  Enter quantity to add: ")
    current_stock = _safe_int(product.get("Stock", 0))
    product["Stock"] = str(current_stock + add_qty)

    write_products(products)
    print(
        f"\n  Restocked {product['ProductName']} by {add_qty}. "
        f"New stock: {product['Stock']}.\n"
    )


def buy_product(customer_name: str | None = None) -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return

    if not customer_name:
        customer_name = read_non_empty("  Enter customer name: ")

    display_customer_products(products)
    product_id = input("  Enter coffee ID to buy: ").strip()
    product = _find_product_by_id(products, product_id)

    if not product:
        print(f"\n  Coffee ID {product_id} not found.\n")
        return

    stock = _safe_int(product.get("Stock", 0))
    if stock <= 0:
        print("\n  Product is out of stock.\n")
        return

    while True:
        qty_raw = input(f"  Enter quantity to buy (1-{stock}): ").strip()
        try:
            qty = int(qty_raw)
            if qty <= 0:
                print("\n  Quantity must be at least 1.")
                continue
            if qty > stock:
                print(f"\n  Only {stock} in stock.")
                continue
            break
        except ValueError:
            print("\n  Invalid number. Please try again.")

    product["Stock"] = str(stock - qty)
    product["Sold"] = str(_safe_int(product.get("Sold", 0)) + qty)
    write_products(products)
    write_sales_csv(products)

    price = _safe_float(product.get("Price", 0))
    total = qty * price
    print(
        f"\n  Purchase complete: {customer_name} bought "
        f"{qty} x {product['ProductName']} = {total:.2f}\n"
    )


def best_selling_summary() -> None:
    products = read_products()
    if not products:
        print("\n  No products found.\n")
        return

    ranked = _get_ranked_sales(products)
    if not ranked:
        write_sales_csv(products)
        print("\n  No sales data yet. Let customers buy products first.\n")
        return

    write_sales_csv(products)

    total_units = sum(_safe_int(item.get("Sold", 0)) for item in ranked)
    total_revenue = sum(
        _safe_int(item.get("Sold", 0)) * _safe_float(item.get("Price", 0))
        for item in ranked
    )

    print("\n  BEST-SELLING PRODUCTS")
    print("  " + TABLE_LINE)
    print(f"  {'RANK':<6}{'PRODUCT':<26}{'UNITS SOLD':>12}{'REVENUE':>14}{'STOCK LEFT':>15}")
    print("  " + TABLE_LINE)

    for index, item in enumerate(ranked[:5], start=1):
        units_sold = _safe_int(item.get("Sold", 0))
        revenue = units_sold * _safe_float(item.get("Price", 0))
        stock_left = _safe_int(item.get("Stock", 0))
        print(
            f"  {index:<6}{item.get('ProductName', '')[:25]:<26}"
            f"{units_sold:>12}{revenue:>14.2f}{stock_left:>15}"
        )

    top = ranked[0]
    print("  " + TABLE_LINE)
    print(f"  Total units sold : {total_units}")
    print(f"  Total revenue    : {total_revenue:.2f}")
    print(
        "  Best seller      : "
        f"{top.get('ProductName', 'N/A')} "
        f"({top.get('Sold', '0')} units)"
    )
    print()


def show_owner_menu() -> None:
    print("=" * MENU_WIDTH)
    print("           OWNER PORTAL")
    print("=" * MENU_WIDTH)
    print("  1. View Products")
    print("  2. Add Product")
    print("  3. Edit Product")
    print("  4. Delete Product")
    print("  5. Restock Product")
    print("  6. Best-Selling Summary")
    print("  7. Back to Role Selection")
    print("=" * MENU_WIDTH)


def show_customer_menu(customer_name: str) -> None:
    print("=" * MENU_WIDTH)
    print(f"      CUSTOMER PORTAL - {customer_name[:18]}")
    print("=" * MENU_WIDTH)
    print("  1. View Coffee Menu")
    print("  2. Buy Coffee")
    print("  3. View Best-Selling Products")
    print("  4. Back to Role Selection")
    print("=" * MENU_WIDTH)


def show_role_menu() -> None:
    print("=" * MENU_WIDTH)
    print("        COFFEE SHOP SYSTEM")
    print("=" * MENU_WIDTH)
    print("  1. Enter as Owner")
    print("  2. Enter as Customer")
    print("  3. Exit")
    print("  Owner password default: admin123")
    print("=" * MENU_WIDTH)


def owner_portal() -> None:
    while True:
        show_owner_menu()
        choice = input("  Enter choice (1-7): ").strip()

        if choice == "1":
            view_products()
        elif choice == "2":
            add_product()
        elif choice == "3":
            edit_product()
        elif choice == "4":
            delete_product()
        elif choice == "5":
            restock_product()
        elif choice == "6":
            best_selling_summary()
        elif choice == "7":
            print("\n  Returning to role selection...\n")
            break
        else:
            print("\n  Invalid option. Try again.\n")

        input("Press Enter to continue...")
        clear_screen()


def customer_portal() -> None:
    customer_name = read_non_empty("  Enter customer name: ")
    clear_screen()

    while True:
        show_customer_menu(customer_name)
        choice = input("  Enter choice (1-4): ").strip()

        if choice == "1":
            view_customer_products()
        elif choice == "2":
            buy_product(customer_name)
        elif choice == "3":
            best_selling_summary()
        elif choice == "4":
            print("\n  Returning to role selection...\n")
            break
        else:
            print("\n  Invalid option. Try again.\n")

        input("Press Enter to continue...")
        clear_screen()


def main() -> None:
    while True:
        show_role_menu()
        choice = input("  Enter choice (1-3): ").strip()

        if choice == "1":
            clear_screen()
            if authenticate_owner():
                owner_portal()
        elif choice == "2":
            clear_screen()
            customer_portal()
        elif choice == "3":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  Invalid option. Try again.\n")

        input("Press Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    clear_screen()
    main()
