"""Add test user (run once): python seed_test_user.py → rahul.nitjsr67@gmail.com / Test@123"""
import sys
import config
config.load_env()
from db import init_db, create_user, get_user_by_email
from auth_utils import hash_password

TEST_EMAIL = "rahul.nitjsr67@gmail.com"
TEST_PASSWORD = "Test@123"


def main():
    init_db()
    if get_user_by_email(TEST_EMAIL):
        print(f"User {TEST_EMAIL} already exists. Use password: {TEST_PASSWORD}")
        return
    user_id = create_user(TEST_EMAIL, hash_password(TEST_PASSWORD))
    if user_id:
        print(f"Test user created. Log in at http://localhost:5000 with:")
        print(f"  Email:    {TEST_EMAIL}")
        print(f"  Password: {TEST_PASSWORD}")
    else:
        print("User already exists or creation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
