"""
PS 57 - Vehicle Rental Management System
Language : Python 3
Concepts : OOP, Lists, Dictionaries, File Handling

Data is saved in vehicles.txt in this format (one vehicle per line):
    id|type|model|rate|status|customer|days
For a vehicle that is available, customer and days are left empty.
"""

import os

FILE_NAME = "vehicles.txt"
DISCOUNT_DAYS = 7      # 7 or more days -> discount
DISCOUNT_RATE = 0.10   # 10 percent


class Vehicle:
    def __init__(self, vid, vtype, model, rate, available=True):
        self.id = vid
        self.type = vtype
        self.model = model
        self.rate = rate
        self.available = available

    def status(self):
        return "Available" if self.available else "Rented"

    def __str__(self):
        return f"ID: {self.id} | {self.type} | {self.model} | Rs. {self.rate}/day | {self.status()}"


class Rental:
    """Keeps the rental details of one vehicle."""

    def __init__(self, vehicle_id, customer, days, bill):
        self.vehicle_id = vehicle_id
        self.customer = customer
        self.days = days
        self.bill = bill


class RentalShop:
    def __init__(self):
        self.vehicles = []   # list of Vehicle objects
        self.rentals = {}    # dictionary: vehicle id -> Rental
        self.load_data()

    # ---------------- file handling ----------------
    def load_data(self):
        if not os.path.exists(FILE_NAME):
            return  # first run, nothing to load

        with open(FILE_NAME, "r") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split("|")
                if len(parts) < 5:
                    continue  # skip broken lines

                vid, vtype, model, rate, status = parts[:5]
                vehicle = Vehicle(vid, vtype, model, int(rate), status == "Available")
                self.vehicles.append(vehicle)

                # if the vehicle was rented, rebuild its rental record
                if status == "Rented" and len(parts) >= 7:
                    customer = parts[5]
                    days = int(parts[6])
                    bill = self.calculate_bill(vehicle.rate, days)
                    self.rentals[vid] = Rental(vid, customer, days, bill)

    def save_data(self):
        with open(FILE_NAME, "w") as f:
            for v in self.vehicles:
                line = f"{v.id}|{v.type}|{v.model}|{v.rate}|{v.status()}"
                if v.id in self.rentals:
                    r = self.rentals[v.id]
                    line += f"|{r.customer}|{r.days}"
                f.write(line + "\n")

    # ---------------- helpers ----------------
    def next_id(self):
        # IDs start from V1, so find the biggest number and add 1
        biggest = 0
        for v in self.vehicles:
            number = int(v.id[1:])
            if number > biggest:
                biggest = number
        return "V" + str(biggest + 1)

    def find_vehicle(self, vid):
        for v in self.vehicles:
            if v.id.upper() == vid.upper():
                return v
        return None

    def calculate_bill(self, rate, days):
        total = rate * days
        if days >= DISCOUNT_DAYS:
            total = total - total * DISCOUNT_RATE
        total = round(total, 2)
        if total == int(total):   # show 9450 instead of 9450.0
            total = int(total)
        return total

    # ---------------- main features ----------------
    def add_vehicle(self, vtype, model, rate):
        vid = self.next_id()
        vehicle = Vehicle(vid, vtype, model, rate)
        self.vehicles.append(vehicle)
        self.save_data()
        print("Vehicle added.", vehicle)

    def rent_vehicle(self, vid, customer, days):
        vehicle = self.find_vehicle(vid)

        if vehicle is None:
            print(f"Vehicle {vid} not found.")
            return
        if not vehicle.available:
            print(f"Vehicle {vehicle.id} is not available.")
            return
        if days < 1:
            print("Days must be 1 or more.")
            return

        bill = self.calculate_bill(vehicle.rate, days)
        vehicle.available = False
        self.rentals[vehicle.id] = Rental(vehicle.id, customer, days, bill)
        self.save_data()

        if days >= DISCOUNT_DAYS:
            print(f"{vehicle.id} rented to {customer} for {days} days. "
                  f"10% discount applied. Bill: Rs. {bill}")
        else:
            print(f"{vehicle.id} rented to {customer} for {days} days. Bill: Rs. {bill}")

    def return_vehicle(self, vid):
        vehicle = self.find_vehicle(vid)

        if vehicle is None:
            print(f"Vehicle {vid} not found.")
            return
        if vehicle.available:
            print(f"Vehicle {vehicle.id} was not rented.")
            return

        vehicle.available = True
        del self.rentals[vehicle.id]
        self.save_data()
        print(f"{vehicle.id} returned. Status: Available")

    def show_available(self):
        found = False
        for v in self.vehicles:
            if v.available:
                print(v)
                found = True
        if not found:
            print("No vehicles available right now.")

    def show_all(self):
        if len(self.vehicles) == 0:
            print("No vehicles in the shop yet.")
            return
        for v in self.vehicles:
            line = str(v)
            if v.id in self.rentals:
                r = self.rentals[v.id]
                line += f" | Customer: {r.customer}, {r.days} days, Bill: Rs. {r.bill}"
            print(line)


# ---------------- input helpers ----------------
def get_number(message):
    """Keep asking until the user types a whole number."""
    while True:
        value = input(message).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid number.")


def get_text(message):
    while True:
        value = input(message).strip()
        if value != "":
            return value
        print("This cannot be empty.")


def main():
    shop = RentalShop()

    while True:
        print("\n===== Vehicle Rental Management System =====")
        print("1. Add vehicle")
        print("2. Rent vehicle")
        print("3. Return vehicle")
        print("4. View available vehicles")
        print("5. View all vehicles")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            vtype = get_text("Type: ")
            model = get_text("Model: ")
            rate = get_number("Rate per day: ")
            if rate <= 0:
                print("Rate must be more than 0.")
            else:
                shop.add_vehicle(vtype, model, rate)

        elif choice == "2":
            vid = get_text("Vehicle ID: ")
            customer = get_text("Customer: ")
            days = get_number("Days: ")
            shop.rent_vehicle(vid, customer, days)

        elif choice == "3":
            vid = get_text("Vehicle ID: ")
            shop.return_vehicle(vid)

        elif choice == "4":
            shop.show_available()

        elif choice == "5":
            shop.show_all()

        elif choice == "6":
            print("Data saved. Goodbye!")
            break

        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()