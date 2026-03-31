def view_sales_history() -> None:
    sales_history_path = Path(__file__).parent / "sales_history.csv"
    sales_fields = ["OrderID", "CustomerName", "ProductName", "Price", "Quantity", "AmountPaid"]
    if not sales_history_path.exists() or os.stat(sales_history_path).st_size == 0:
        print("\n  No sales history found.\n")
        return
    # Read and fix header if missing
    with open(sales_history_path, newline="", encoding="utf-8") as f:
        first_line = f.readline()
        if not first_line.strip() or not all(h in first_line for h in sales_fields):
            # File has no header, so re-read with header manually
            f.seek(0)
            rows = list(csv.reader(f))
            if not rows or not any(rows):
                print("\n  No sales history found.\n")
                return
            # Insert header and rewrite file
            with open(sales_history_path, "w", newline="", encoding="utf-8") as fw:
                writer = csv.writer(fw)
                writer.writerow(sales_fields)
                writer.writerows(rows)
            # Now read as DictReader
            with open(sales_history_path, newline="", encoding="utf-8") as fr:
                reader = csv.DictReader(fr)
                rows = list(reader)
        else:
            f.seek(0)
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            print("\n  No sales history found.\n")
            return
        print("\n  SALES HISTORY")
        print("  " + "-" * 80)
        print(f"  {'OrderID':<36}{'Customer':<15}{'Product':<15}{'Price':>8}{'Qty':>5}{'Paid':>10}")
        print("  " + "-" * 80)
        for row in rows:
            print(f"  {row['OrderID']:<36}{row['CustomerName']:<15}{row['ProductName']:<15}{row['Price']:>8}{row['Quantity']:>5}{row['AmountPaid']:>10}")
        print("  " + "-" * 80 + "\n")
import csv
import os
from pathlib import Path


# Type alias for a coffee product
CoffeeProduct = dict[str, str]


COFFEE_CSV = Path(__file__).parent / "coffee.csv"
SALES_CSV = Path(__file__).parent / "sales.csv"
COFFEE_FIELDS = ["ProductID", "ProductName", "Price", "Stock", "Sold"]
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
OWNER_PASSWORD = os.environ.get("COFFEESHOP_OWNER_PASSWORD", "admin123")
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


def _normalize_row(row: dict[str, str]) -> CoffeeProduct:
    # Supports old CSV formats so existing files can still be read.
    keymap = {
        "productid": "ProductID",
        "id": "ProductID",
        "productname": "ProductName",
        "product name": "ProductName",
        "coffee name": "ProductName",
        "coffee": "ProductName",
        "name": "ProductName",
        "price": "Price",
        "amount": "Price",
        "stock": "Stock",
        "stocks": "Stock",
        "total stocks": "Stock",
        "quantity": "Stock",
        "sold": "Sold",
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


def _ensure_valid_ids(coffees: list[CoffeeProduct]) -> None:
    used_ids = set()
    next_id = 1

    for coffee in coffees:
        raw_id = _safe_int(coffee.get("ProductID", 0))
        if raw_id <= 0 or raw_id in used_ids:
            while next_id in used_ids:
                next_id += 1
            raw_id = next_id
        used_ids.add(raw_id)
        coffee["ProductID"] = str(raw_id)



def read_coffees() -> list[CoffeeProduct]:
    coffees: list[CoffeeProduct] = []
    if COFFEE_CSV.exists():
        with open(COFFEE_CSV, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                normalized = _normalize_row(row)
                if normalized["ProductName"]:
                    coffees.append(normalized)
    _ensure_valid_ids(coffees)
    return coffees



def write_coffees(coffees: list[CoffeeProduct]) -> None:
    _ensure_valid_ids(coffees)
    coffees.sort(key=lambda item: _safe_int(item.get("ProductID", 0)))
    with open(COFFEE_CSV, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=COFFEE_FIELDS)
        writer.writeheader()
        writer.writerows(coffees)



def next_coffee_id(coffees: list[CoffeeProduct]) -> int:
    highest = 0
    for coffee in coffees:
        highest = max(highest, _safe_int(coffee.get("ProductID", 0)))
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



def display_coffees(coffees: list[CoffeeProduct]) -> None:
    print(f"\n  {'ID':<5}{'COFFEE':<26}{'PRICE':>10}{'STOCK':>10}{'SOLD':>10}")
    print("  " + "-" * 61)
    for coffee in coffees:
        price = _safe_float(coffee.get("Price", 0))
        stock = _safe_int(coffee.get("Stock", 0))
        sold = _safe_int(coffee.get("Sold", 0))
        print(
            f"  {coffee.get('ProductID', ''):<5}"
            f"{coffee.get('ProductName', '')[:25]:<26}"
            f"{price:>10.2f}{stock:>10}{sold:>10}"
        )
    print()



def display_available_coffees(coffees: list[CoffeeProduct]) -> None:
    available_coffees = [item for item in coffees if _safe_int(item.get("Stock", 0)) > 0]
    if not available_coffees:
        print("\n  No available coffee right now.\n")
        return
    print(f"\n  {'ID':<5}{'COFFEE':<26}{'PRICE':>10}{'AVAILABLE':>12}")
    print("  " + "-" * 53)
    for coffee in available_coffees:
        print(
            f"  {coffee.get('ProductID', ''):<5}"
            f"{coffee.get('ProductName', '')[:25]:<26}"
            f"{_safe_float(coffee.get('Price', 0)):>10.2f}"
            f"{_safe_int(coffee.get('Stock', 0)):>12}"
        )
    print()



def view_coffees() -> None:
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    display_coffees(coffees)



def view_available_coffees() -> None:
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    display_available_coffees(coffees)



def add_coffee() -> None:
    coffees = read_coffees()
    name = read_non_empty("  Enter coffee name: ")
    price = read_non_negative_float("  Enter price: ")
    stock = read_non_negative_int("  Enter stock quantity: ")
    coffee = {
        "ProductID": str(next_coffee_id(coffees)),
        "ProductName": name,
        "Price": f"{price:.2f}",
        "Stock": str(stock),
        "Sold": "0",
    }
    coffees.append(coffee)
    write_coffees(coffees)
    print(f"\n  Coffee added: {name} (ID {coffee['ProductID']}).\n")



def _find_coffee_by_id(coffees: list[CoffeeProduct], coffee_id: str) -> CoffeeProduct | None:
    for coffee in coffees:
        if coffee.get("ProductID") == coffee_id:
            return coffee
    return None



def _get_ranked_sales(coffees: list[CoffeeProduct]) -> list[CoffeeProduct]:
    sold_coffees = [item for item in coffees if _safe_int(item.get("Sold", 0)) > 0]
    ranked = sorted(
        sold_coffees,
        key=lambda item: (
            _safe_int(item.get("Sold", 0)),
            _safe_int(item.get("Sold", 0)) * _safe_float(item.get("Price", 0)),
        ),
        reverse=True,
    )
    return ranked



def write_sales_csv(coffees: list[CoffeeProduct]) -> None:
    ranked = _get_ranked_sales(coffees)
    with open(SALES_CSV, "w", newline="", encoding="utf-8") as csv_file:
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



def edit_coffee() -> None:
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    display_coffees(coffees)
    coffee_id = input("  Enter coffee ID to edit: ").strip()
    coffee = _find_coffee_by_id(coffees, coffee_id)
    if not coffee:
        print(f"\n  Coffee ID {coffee_id} not found.\n")
        return
    current_name = coffee["ProductName"]
    current_price = _safe_float(coffee["Price"])
    current_stock = _safe_int(coffee["Stock"])
    new_name = input(f"  New name [{current_name}]: ").strip()
    if new_name:
        coffee["ProductName"] = new_name
    while True:
        new_price_raw = input(f"  New price [{current_price:.2f}]: ").strip()
        if not new_price_raw:
            break
        try:
            new_price = float(new_price_raw)
            if new_price < 0:
                print("\n  Value must be zero or greater.")
                continue
            coffee["Price"] = f"{new_price:.2f}"
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
            coffee["Stock"] = str(new_stock)
            break
        except ValueError:
            print("\n  Invalid number. Please try again.")
    write_coffees(coffees)
    print(f"\n  Coffee ID {coffee_id} updated.\n")



def delete_coffee() -> None:
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    display_coffees(coffees)
    coffee_id = input("  Enter coffee ID to delete: ").strip()
    coffee = _find_coffee_by_id(coffees, coffee_id)
    if not coffee:
        print(f"\n  Coffee ID {coffee_id} not found.\n")
        return
    confirm = input(f"  Delete '{coffee['ProductName']}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("\n  Delete cancelled.\n")
        return
    updated_coffees = [item for item in coffees if item.get("ProductID") != coffee_id]
    write_coffees(updated_coffees)
    print(f"\n  Coffee ID {coffee_id} deleted.\n")



def restock_coffee() -> None:
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    display_coffees(coffees)
    coffee_id = input("  Enter coffee ID to restock: ").strip()
    coffee = _find_coffee_by_id(coffees, coffee_id)
    if not coffee:
        print(f"\n  Coffee ID {coffee_id} not found.\n")
        return
    add_qty = read_positive_int("  Enter quantity to add: ")
    current_stock = _safe_int(coffee.get("Stock", 0))
    coffee["Stock"] = str(current_stock + add_qty)
    write_coffees(coffees)
    print(
        f"\n  Restocked {coffee['ProductName']} by {add_qty}. "
        f"New stock: {coffee['Stock']}.\n"
    )



def buy_coffee(customer_name: str | None = None) -> None:
    import uuid
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    if not customer_name:
        customer_name = read_non_empty("  Enter customer name: ")
    display_available_coffees(coffees)
    coffee_id = input("  Enter coffee ID to buy: ").strip()
    coffee = _find_coffee_by_id(coffees, coffee_id)
    if not coffee:
        print(f"\n  Coffee ID {coffee_id} not found.\n")
        return
    stock = _safe_int(coffee.get("Stock", 0))
    if stock <= 0:
        print("\n  Coffee is out of stock.\n")
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
    coffee["Stock"] = str(stock - qty)
    coffee["Sold"] = str(_safe_int(coffee.get("Sold", 0)) + qty)
    write_coffees(coffees)
    write_sales_csv(coffees)
    price = _safe_float(coffee.get("Price", 0))
    total = qty * price
    # Record sales history
    sales_history_path = Path(__file__).parent / "sales_history.csv"
    order_id = str(uuid.uuid4())
    sales_fields = ["OrderID", "CustomerName", "ProductName", "Price", "Quantity", "AmountPaid"]
    write_header = not sales_history_path.exists() or os.stat(sales_history_path).st_size == 0
    # Check if file exists and has header, if not, write header
    if not sales_history_path.exists() or os.stat(sales_history_path).st_size == 0:
        with open(sales_history_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sales_fields)
            writer.writeheader()
            writer.writerow({
                "OrderID": order_id,
                "CustomerName": customer_name,
                "ProductName": coffee["ProductName"],
                "Price": f"{price:.2f}",
                "Quantity": qty,
                "AmountPaid": f"{total:.2f}"
            })
    else:
        # Check if header is present
        with open(sales_history_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
        if not all(h in first_line for h in sales_fields):
            # Insert header at the top
            with open(sales_history_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(sales_history_path, "w", encoding="utf-8") as f:
                f.write(",".join(sales_fields) + "\n" + content)
        with open(sales_history_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sales_fields)
            writer.writerow({
                "OrderID": order_id,
                "CustomerName": customer_name,
                "ProductName": coffee["ProductName"],
                "Price": f"{price:.2f}",
                "Quantity": qty,
                "AmountPaid": f"{total:.2f}"
            })
    print(
        f"\n  Purchase complete: {customer_name} bought "
        f"{qty} x {coffee['ProductName']} = {total:.2f}\n"
    )



def best_selling_summary() -> None:
    coffees = read_coffees()
    if not coffees:
        print("\n  No coffee found.\n")
        return
    ranked = _get_ranked_sales(coffees)
    if not ranked:
        write_sales_csv(coffees)
        print("\n  No sales data yet. Let customers buy coffee first.\n")
        return
    write_sales_csv(coffees)
    total_units = sum(_safe_int(item.get("Sold", 0)) for item in ranked)
    total_revenue = sum(
        _safe_int(item.get("Sold", 0)) * _safe_float(item.get("Price", 0))
        for item in ranked
    )
    print("\n  BEST-SELLING COFFEE")
    print("  " + TABLE_LINE)
    print(f"  {'RANK':<6}{'COFFEE':<26}{'UNITS SOLD':>12}{'REVENUE':>14}{'STOCK LEFT':>15}")
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
    print("  1. View Coffee")
    print("  2. Add Coffee")
    print("  3. Edit Coffee")
    print("  4. Delete Coffee")
    print("  5. Restock Coffee")
    print("  6. Best-Selling Summary")
    print("  7. View Sales History")
    print("  8. Back to Role Selection")
    print("=" * MENU_WIDTH)



def show_customer_menu(customer_name: str) -> None:
    print("=" * MENU_WIDTH)
    print(f"      CUSTOMER PORTAL - {customer_name[:18]}")
    print("=" * MENU_WIDTH)
    print("  1. View Coffee Menu")
    print("  2. Buy Coffee")
    print("  3. View Best-Selling Coffee")
    print("  4. Back to Role Selection")
    print("=" * MENU_WIDTH)


def show_role_menu() -> None:
    print("=" * MENU_WIDTH)
    print("        COFFEE SHOP SYSTEM")
    print("=" * MENU_WIDTH)
    print("  1. Enter as Owner")
    print("  2. Enter as Customer")
    print("  3. Exit")
    print("=" * MENU_WIDTH)



def owner_portal() -> None:
    while True:
        show_owner_menu()
        choice = input("  Enter choice (1-8): ").strip()
        if choice == "1":
            view_coffees()
        elif choice == "2":
            add_coffee()
        elif choice == "3":
            edit_coffee()
        elif choice == "4":
            delete_coffee()
        elif choice == "5":
            restock_coffee()
        elif choice == "6":
            best_selling_summary()
        elif choice == "7":
            view_sales_history()
        elif choice == "8":
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
            view_available_coffees()
        elif choice == "2":
            buy_coffee(customer_name)
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
