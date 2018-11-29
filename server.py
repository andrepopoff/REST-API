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

    def __init__(self, user):
        self.id_ = user.id_
        self.name = user.name
        self.url = '/users/{}'.format(user.id_)


class UserController(object):
    def __init__(self):
        self.users = {}
        self.last_id = 0

    def create(self, data):
        """
        Creates a new user
        """
        id_ = self.last_id
        self.last_id += 1
        data['id_'] = id_

        user = User(**data)
        self.users[id_] = user
        return UserRef(user)

    def list(self):
        """
        Get list of users (sorted by id)
        """
        users_ids = sorted(self.users)
        users_refs = []

        for id_ in users_ids:
            try:
                users_refs.append(self.users[id_])
            except KeyError:
                pass

        return users_refs

    def delete(self, id_):
        """
        Deletes users by id
        """
        try:
            del self.users[id_]
        except KeyError:
            pass
        