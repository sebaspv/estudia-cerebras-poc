import time
import uuid


def short_uuid(length: int = 6):
    """
    Generates a truncated UUID with python's UUID library.
    Note that the maximum UUID length is 36.
    """
    return str(uuid.uuid1())[: length + 1]


if __name__ == "__main__":
    print(short_uuid())  # should print with length of 6
    time.sleep(0.01)
    print(short_uuid(5))  # length of 5
