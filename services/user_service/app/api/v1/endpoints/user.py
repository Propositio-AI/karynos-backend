from crud.User import read_user_by_email

def get_user(email:str = None):
    if email is not None:
        return read_user_by_email(email=email)
