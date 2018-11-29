class User(object):
    __slots__ = ('id_', 'name', 'email', 'age', 'sex')
    
    def __init__(self, id_, name, email, age, sex):
        self.id_ = id_
        self.name = name
        self.email = email
        self.age = age
        self.sex = sex