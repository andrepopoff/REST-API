import json
import functools

from http.server import BaseHTTPRequestHandler, HTTPServer


class HTTPError(Exception):
    def __init__(self, code, reason):
        super(HTTPError, self).__init__(reason)
        self.code = code


class User(object):
    __slots__ = ('id', 'name', 'email', 'age', 'sex')

    def __init__(self, id_, **kwargs):
        self.id = id_
        self.update(**kwargs)

    def update(self, name, email, age, sex):
        self.name = name
        self.email = email
        self.age = age
        self.sex = sex

    def toDict(self):
        return {k: getattr(self, k) for k in self.__slots__}


class UserRef(object):
    __slots__ = ('id', 'name', 'url')

    def __init__(self, user):
        self.id = user.id_
        self.name = user.name
        self.url = '/users/{}'.format(user.id_)


class UserController(object):
    def __init__(self):
        self.users = {}
        self.last_id = 0

    def __user_id_from_str(self, id_str):
        try:
            return int(id_str)
        except ValueError:
            raise HTTPError(404, 'user with id {} is not found'.format(id_str))

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

    def get(self, id_str):
        try:
            return self.users[self.__user_id_from_str(id_str)]
        except KeyError:
            raise HTTPError(404, 'user({}) is not found'.format(id_str))

    def delete(self, id_str):
        """
        Deletes users by id
        """
        try:
            del self.users[self.__user_id_from_str(id_str)]
        except KeyError:
            raise HTTPError(404, 'user({}) is not found'.format(id_str))

    def update(self, id_str, data):
        """
        Updates user by id
        """
        user = self.get(id_str)
        user.update(**data)


class HTTPHandler(BaseHTTPRequestHandler):
    controller = UserController()

    def do_GET(self):
        if self.path == '/users/':
            return self.process_request(self.controller.list)

        if self.path.startswith('/users/'):
            parts = self.path.split('/', 4)
            if len(parts) == 3:
                user_id = parts[2]
                return self.process_request(200, functools.partial(self.controller.get, user_id))

        self.not_found()

    def do_POST(self):
        if self.path == '/users/':
            self.process_request(201, functools.partial(self.call_with_body, self.controller.create))
        self.not_found()

    def do_PUT(self):
        user_id = self.get_user_id()
        if user_id is not None:
            update_user = functools.partial(self.controller.update, user_id)
            self.process_request(200, functools.partial(self.call_with_body, update_user))

        self.not_found()

    def do_DELETE(self):
        user_id = self.get_user_id()
        if user_id is not None:
            self.process_request(200, functools.partial(self.controller.update, user_id))

        self.not_found()

    def get_user_id(self):
        if self.path.startswith('/users/'):
            parts = self.path.split('/', 4)
            if len(parts) == 3:
                return parts[2]

    def get_data(self):
        """
        Gets request params from body
        """
        if self.headers['Content-Type'].startswith('application/json'):
            raise HTTPError(415, 'expected application/json')
        number_of_bytes = int(self.headers['Content-Length'])
        body = self.rfile.read(number_of_bytes)
        return json.loads(body, encoding='utf-8')

    def call_with_body(self, handler):
        try:
            data = self.get_data()
        except Exception as e:
            raise HTTPError(400, str(e))

        return handler(data)

    def process_request(self, status, handler):
        """
        Gets data from handler and writes as response
        """
        try:
            data = handler()
        except HTTPError as e:
            data = {'error': str(e)}
            status = e.code
        except Exception as e:
            data = {'error': str(e)}
            status = 500

        self.write_response(status, data)

    def write_response(self, status, data):
        """
        Formats response as json and writes
        """
        body = json.dumps(data, sort_keys=True, indent=4).encode('utf-8')
        self.send_response(status)
        self.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.headers['Content-Length'] = len(data)
        self.end_headers()
        self.wfile.write(body)

    def not_found(self):
        self.write_response(404, {'error': 'not found'})


def main():
    server_address = ('127.0.0.1', '8080')
    server = HTTPServer(server_address, HTTPHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
