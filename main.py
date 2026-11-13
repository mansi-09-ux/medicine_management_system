import csv
import json
import os
from datetime import datetime
MEDICINE_FILE = "medicines.csv"
SALES_FILE = "sales.csv"
SUPPLIER_FILE = "suppliers.csv"
ALERT_FILE = "alerts.json"
ADMIN_FILE = "admin.json"
class MedicineManagement:
    def create_files(self):
        files = {
            MEDICINE_FILE: ["ID", "Name", "Category", "Quantity", "Price", "Expiry_Date"],
            SALES_FILE: ["Medicine_ID", "Name", "Quantity", "Total", "Date"],
            SUPPLIER_FILE: ["ID", "Name", "Phone", "Medicine_ID"]
        }

        for filename, headers in files.items():
            if not os.path.exists(filename):
                with open(filename, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

        if not os.path.exists(ALERT_FILE):
            with open(ALERT_FILE, "w") as f:
                json.dump({"alerts": []}, f, indent=4)

        if not os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, "w") as f:
                json.dump({
                    "username": "admin",
                    "password": "admin123"
                }, f, indent=4)

    def read_csv(self, filename):
        with open(filename, "r", newline="") as f:
            return list(csv.DictReader(f))

    def save_csv(self, filename, fields, data):
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)

    # 1. ADMIN LOGIN
    def admin_login(self):
        with open(ADMIN_FILE, "r") as f:
            admin = json.load(f)

        username = input("Enter username: ")
        password = input("Enter password: ")

        if username == admin["username"] and password == admin["password"]:
            print("Login successful!")
            return True

        print("Invalid username or password!")
        return False
    def add_medicine(self):
        med_id = input("Enter Medicine ID: ")
        medicines = self.read_csv(MEDICINE_FILE)

        if any(m["ID"] == med_id for m in medicines):
            print("Medicine ID already exists!")
            return

        name = input("Enter Medicine Name: ")
        category = input("Enter Category: ")

        try:
            quantity = int(input("Enter Quantity: "))
            price = float(input("Enter Price: "))
            expiry = input("Enter Expiry Date (YYYY-MM-DD): ")
            datetime.strptime(expiry, "%Y-%m-%d")

            if quantity < 0 or price < 0:
                print("Quantity and price cannot be negative!")
                return

        except ValueError:
            print("Invalid input!")
            return

        medicines.append({
            "ID": med_id,
            "Name": name,
            "Category": category,
            "Quantity": str(quantity),
            "Price": str(price),
            "Expiry_Date": expiry
        })

        self.save_csv(
            MEDICINE_FILE,
            ["ID", "Name", "Category", "Quantity", "Price", "Expiry_Date"],
            medicines
        )
        print("Medicine added successfully!")
    def view_medicines(self):
        medicines = self.read_csv(MEDICINE_FILE)

        if not medicines:
            print("No medicines found!")
            return

        for med in medicines:
            print(med)
    def search_medicine(self):
        search = input("Enter medicine ID or name: ").lower()
        medicines = self.read_csv(MEDICINE_FILE)

        found = False

        for med in medicines:
            if search == med["ID"].lower() or search in med["Name"].lower():
                print(med)
                found = True

        if not found:
            print("Medicine not found!")
    def update_medicine(self):
        med_id = input("Enter Medicine ID: ")
        medicines = self.read_csv(MEDICINE_FILE)

        for med in medicines:
            if med["ID"] == med_id:
                name = input("Enter new name (blank to keep): ")
                category = input("Enter new category (blank to keep): ")
                if name:
                    med["Name"] = name
                if category:
                    med["Category"] = category

                self.save_csv(
                    MEDICINE_FILE,
                    ["ID", "Name", "Category", "Quantity", "Price", "Expiry_Date"],
                    medicines
                )
                print("Medicine updated!")
                return

        print("Medicine not found!")

    def delete_medicine(self):
        med_id = input("Enter Medicine ID: ")
        medicines = self.read_csv(MEDICINE_FILE)
        updated = [m for m in medicines if m["ID"] != med_id]
        if len(updated) == len(medicines):
            print("Medicine not found!")
            return
        self.save_csv(
            MEDICINE_FILE,
            ["ID", "Name", "Category", "Quantity", "Price", "Expiry_Date"],
            updated
        )
        print("Medicine deleted!")
    def restock_medicine(self):
        med_id = input("Enter Medicine ID: ")
        medicines = self.read_csv(MEDICINE_FILE)

        try:
            amount = int(input("Enter additional quantity: "))
            if amount <= 0:
                print("Enter a positive quantity!")
                return
        except ValueError:
            print("Invalid quantity!")
            return

        for med in medicines:
            if med["ID"] == med_id:
                med["Quantity"] = str(int(med["Quantity"]) + amount)

                self.save_csv(
                    MEDICINE_FILE,
                    ["ID", "Name", "Category", "Quantity", "Price", "Expiry_Date"],
                    medicines
                )
                print("Stock restocked successfully!")
                return

        print("Medicine not found!")
    def check_expiry(self):
        medicines = self.read_csv(MEDICINE_FILE)
        alerts = []
        today = datetime.today().date()

        for med in medicines:
            expiry = datetime.strptime(
                med["Expiry_Date"], "%Y-%m-%d"
            ).date()

            days = (expiry - today).days

            if days < 0:
                message = "EXPIRED"
            elif days <= 7:
                message = "Expires within 7 days"
            elif days <= 30:
                message = "Expires within 30 days"
            else:
                continue

            print(med["Name"], "-", message)

            alerts.append({
                "medicine": med["Name"],
                "message": message
            })

        with open(ALERT_FILE, "w") as f:
            json.dump({"alerts": alerts}, f, indent=4)

        if not alerts:
            print("No expiry alerts!")
    def low_stock(self):
        medicines = self.read_csv(MEDICINE_FILE)
        found = False

        for med in medicines:
            if int(med["Quantity"]) <= 10:
                print(med["Name"], "-", med["Quantity"], "left")
                found = True

        if not found:
            print("All medicines have sufficient stock!")

    # 10. MEDICINE BILLING
    def medicine_billing(self):
        med_id = input("Enter Medicine ID: ")
        medicines = self.read_csv(MEDICINE_FILE)

        try:
            quantity = int(input("Enter quantity to sell: "))
            if quantity <= 0:
                print("Enter a positive quantity!")
                return
        except ValueError:
            print("Invalid quantity!")
            return

        for med in medicines:
            if med["ID"] == med_id:

                if int(med["Quantity"]) < quantity:
                    print("Insufficient stock!")
                    return

                total = quantity * float(med["Price"])
                med["Quantity"] = str(int(med["Quantity"]) - quantity)

                self.save_csv(
                    MEDICINE_FILE,
                    ["ID", "Name", "Category", "Quantity", "Price", "Expiry_Date"],
                    medicines
                )

                with open(SALES_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        med_id,
                        med["Name"],
                        quantity,
                        total,
                        datetime.now().strftime("%Y-%m-%d")
                    ])

                print("\n========== MEDICINE BILL ==========")
                print("Medicine:", med["Name"])
                print("Quantity:", quantity)
                print("Price:", med["Price"])
                print("Total Amount: Rs.", total)
                print("===================================")
                return

        print("Medicine not found!")
    def sales_report(self):
        sales = self.read_csv(SALES_FILE)

        if not sales:
            print("No sales records found!")
            return

        total_sales = 0

        for sale in sales:
            total_sales += float(sale["Total"])
            print(sale)

        print("Total Sales: Rs.", total_sales)
    def supplier_management(self):
        suppliers = self.read_csv(SUPPLIER_FILE)

        print("1. Add Supplier")
        print("2. View Suppliers")
        choice = input("Enter choice: ")

        if choice == "1":
            sid = input("Enter Supplier ID: ")

            if any(s["ID"] == sid for s in suppliers):
                print("Supplier ID already exists!")
                return

            name = input("Enter Supplier Name: ")
            phone = input("Enter Phone Number: ")
            med_id = input("Enter Medicine ID: ")

            medicines = self.read_csv(MEDICINE_FILE)
            if not any(m["ID"] == med_id for m in medicines):
                print("Medicine ID not found!")
                return

            suppliers.append({
                "ID": sid,
                "Name": name,
                "Phone": phone,
                "Medicine_ID": med_id
            })

            self.save_csv(
                SUPPLIER_FILE,
                ["ID", "Name", "Phone", "Medicine_ID"],
                suppliers
            )
            print("Supplier added!")

        elif choice == "2":
            if not suppliers:
                print("No suppliers found!")
            else:
                for supplier in suppliers:
                    print(supplier)
        else:
            print("Invalid choice!")
    def dashboard(self):
        medicines = self.read_csv(MEDICINE_FILE)
        sales = self.read_csv(SALES_FILE)
        total_items = len(medicines)
        total_stock = sum(int(m["Quantity"]) for m in medicines)
        expired = 0
        low_stock = 0
        today = datetime.today().date()
        for med in medicines:
            expiry = datetime.strptime(
                med["Expiry_Date"], "%Y-%m-%d"
            ).date()
            if expiry < today:
                expired += 1
            if int(med["Quantity"]) <= 10:
                low_stock += 1
        total_sales = sum(float(s["Total"]) for s in sales)
        print("\n========== DASHBOARD ==========")
        print("Different Medicines:", total_items)
        print("Total Stock:", total_stock)
        print("Expired Medicines:", expired)
        print("Low Stock Medicines:", low_stock)
        print("Total Sales: Rs.", total_sales)
        print("================================")
    def menu(self):
        self.create_files()
        print("===== ADMIN LOGIN =====")
        if not self.admin_login():
            return
        while True:
            print("\n========================================")
            print("     SMART MEDICINE MANAGEMENT SYSTEM")
            print("========================================")
            print("1. Add Medicine")
            print("2. View All Medicines")
            print("3. Search Medicine")
            print("4. Update Medicine")
            print("5. Delete Medicine")
            print("6. Restock Medicine")
            print("7. Check Expiry Alerts")
            print("8. Low Stock Alerts")
            print("9. Medicine Billing")
            print("10. Sales Report")
            print("11. Supplier Management")
            print("12. Dashboard Summary")
            print("13. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_medicine()
            elif choice == "2":
                self.view_medicines()
            elif choice == "3":
                self.search_medicine()
            elif choice == "4":
                self.update_medicine()
            elif choice == "5":
                self.delete_medicine()
            elif choice == "6":
                self.restock_medicine()
            elif choice == "7":
                self.check_expiry()
            elif choice == "8":
                self.low_stock()
            elif choice == "9":
                self.medicine_billing()
            elif choice == "10":
                self.sales_report()
            elif choice == "11":
                self.supplier_management()
            elif choice == "12":
                self.dashboard()
            elif choice == "13":
                print("Thank you for using the system!")
                break
            else:
                print("Invalid choice!")
obj = MedicineManagement()
obj.menu()
