from http.server import BaseHTTPRequestHandler


class HTTPError(Exception):
    def __init__(self, code, reason):
        super(HTTPError, self).__init__(reason)
        self.code = code


class User(object):
    __slots__ = ('id_', 'name', 'email', 'age', 'sex')

    def __init__(self, id_, **kwargs):
        self.id_ = id_
        self.update(**kwargs)

    def update(self, name, email, age, sex):
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
            raise HTTPError(404, 'user({}) is not found'.format(id_))

    def update(self, id_, data):
        try:
            user = self.users[id_]
            user.update(**data)
        except KeyError:
            raise HTTPError(404, 'user({}) is not found'.format(id_))
        except (ValueError, TypeError) as e:
            raise HTTPError(400, str(e))


class HTTPHandler(BaseHTTPRequestHandler):
    controller = UserController()

    def do_GET(self):
        if self.patch == '/users/':
            users = self.controller.list()

        pass

