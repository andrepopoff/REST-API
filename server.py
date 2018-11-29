class User(object):
    __slots__ = ('id_', 'name', 'email', 'age', 'sex')

    def __init__(self, id_, name, email, age, sex):
        self.id_ = id_
        self.name = name
        self.email = email
        self.age = age
        self.sex = sex


class UserRef(object):
    __slots__ = ('id_', 'name', 'url')

    def __init__(self, id_, name, url):
        self.id_ = id_
        self.name = name
        self.url = url
        