
def create_check_hash(user_email, user_password):
    from hashlib import sha256

    hasher = sha256()
    string = f"{user_email}+{user_password}"
    hasher.update(string.encode('utf-8'))

    return str(hasher.digest())

def create_password_hash(password):
    from hashlib import sha256

    hasher = sha256()
    hasher.update(password.encode('utf-8'))

    return str(hasher.digest())

def is_user_authorized(user_id, hashed):
    from hashlib import sha256
    from auth_prime.models import User_Table

    hasher = sha256()
    user_data = User_Table.objects.filter(user_id=user_id)
    
    if(len(user_data) < 1):
        return False
    else:
        user_data = user_data[0]

        if(hashed == create_check_hash(user_data.user_email, user_data.user_password)):
            return True
        else:
            return False

def is_admin_authorized(user_id, hashed):
    from hashlib import sha256
    from auth_prime.models import User_Table, Admin_Table

    hasher = sha256()
    user_data = User_Table.objects.filter(user_id=user_id)
    
    if(len(user_data) < 1):
        return False
    else:
        user_data = user_data[0]

        if(hashed == create_check_hash(user_data.user_email, user_data.user_password)):
            admin_data = Admin_Table.objects.filter(user_id=user_id)
            if(len(admin_data) > 0):
                return True
            else:
                return False
        else:
            return False