import re
from datetime import datetime

class RegistrationValidator:
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        if not name or len(name.strip()) < 2:
            return False, "✗ Name must be at least 2 characters long"
        if len(name.strip()) > 100:
            return False, "✗ Name must be less than 100 characters"
        return True, "✓ Valid"

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        if not email:
            return False, "✗ Email is required"
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "✗ Invalid email format"
        return True, "✓ Valid"

    @staticmethod
    def validate_date_of_birth(dob: str) -> tuple[bool, str]:
        if not dob:
            return False, "✗ Date of birth is required"
        try:
            birth_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            if birth_date > today:
                return False, "✗ Date of birth cannot be in the future"
            age = (today - birth_date).days // 365
            if age > 150:
                return False, "✗ Invalid birth date (too old)"
            return True, "✓ Valid"
        except ValueError:
            return False, "✗ Invalid date format. Use YYYY-MM-DD"
