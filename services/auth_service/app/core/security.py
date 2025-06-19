import uuid

def gen_token():
    """
    
    ログイントークンの発行

    Parameters
    ----------
        None

    Returns
    ----------
        token: uuid.UUID

    """

    return uuid.uuid4()
