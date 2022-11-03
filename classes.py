# classes.py

class Project:
    def __init__(self, id=None, owner=None):
        self.id = id
        self.owner = owner

# might not be necesary
class Domino:
    def __init__(self, api_host=None, api_key=None):
        self.api_host = api_host
        self.api_key = api_key