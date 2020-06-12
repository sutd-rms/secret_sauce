import argparse, sys, os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "secretsauce.settings")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", "-e", help="Enter the email address to login with")
    parser.add_argument("--password", "-p", help="Enter the password to login with")
    parser.add_argument("--first_name", "-f", help="First name of the new superuser")
    parser.add_argument("--last_name", "-l", help="Last name of the new superuser")
    kwargs = {k: v for k, v in dict(parser.parse_args()._get_kwargs()).items() if v is not None}

    django.setup()
    from secretsauce.apps.account.models import User
    new_user = User.objects.create_superuser(**kwargs)
    print("New superuser created:", new_user.email)
    