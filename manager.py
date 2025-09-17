import os, csv
from datetime import datetime
from validator import RegistrationValidator

REGISTRATION_FILE = "user_registrations.csv"
REQUIRED_FIELDS = ['Name', 'Email', 'Date_of_Birth', 'Registration_Date']

class RegistrationManager:
    def __init__(self, csv_file: str = REGISTRATION_FILE):
        self.csv_file = csv_file
        self.ensure_csv_exists()

    def ensure_csv_exists(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(REQUIRED_FIELDS)

    def add_registration(self, name, email, dob):
        name_valid, name_msg = RegistrationValidator.validate_name(name)
        email_valid, email_msg = RegistrationValidator.validate_email(email)
        dob_valid, dob_msg = RegistrationValidator.validate_date_of_birth(dob)

        if not all([name_valid, email_valid, dob_valid]):
            return {"success": False, "error": "Validation failed",
                    "details": [name_msg, email_msg, dob_msg]}

        if self.email_exists(email):
            return {"success": False, "error": "Email already registered"}

        registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([name.strip(), email.strip(), dob, registration_date])

        return {"success": True, "message": f"Registered {name}",
                "data": {"Name": name, "Email": email, "Date_of_Birth": dob, "Registration_Date": registration_date}}

    def get_all_registrations(self):
        if not os.path.exists(self.csv_file):
            return {"success": True, "count": 0, "data": []}
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            return {"success": True, "data": list(csv.DictReader(f))}

    def search_registrations(self, query: str):
        query = query.lower().strip()
        results = [r for r in self.get_all_registrations()["data"]
                   if query in r["Name"].lower() or query in r["Email"].lower()]
        return {"success": True, "count": len(results), "data": results}

    def email_exists(self, email: str) -> bool:
        return any(r["Email"].lower() == email.lower()
                   for r in self.get_all_registrations()["data"])
