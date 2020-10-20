from nameko.rpc import rpc
from nameko_redis import Redis
import config as cfg
import jwt
import hashlib
import uuid

class Auth():
    """Microservice for user authentication"""
    # Vars

    name = 'auth'
    db = Redis('redis')

   # Logic

    def _is_valid(self, login, password):
        """Checking login/password
        :returns: True if user is valid"""
        try:
            user_data = self.db.hgetall(login)
            salt = user_data['salt']
            input_hash = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
            return input_hash == user_data['hash']
        except:
            return False

   # API

    @rpc
    def register(self, login, password):
        """Computing hash and saving password into db"
        :returns: True if user was register and False otherwise"""
        # Ensure that user is not already registered
        if self.db.hgetall(login) == {}:
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
            self.db.hmset(login, {
                'salt': salt,
                'hash': hashed_password
            })
            return True
        else:
            return False

    @rpc
    def login(self, login, password):
        """Logging in user, getting JWT
        :params: login, password
        :returns: JWT or False if user is not valid"""
        if self._is_valid(login, password):
            return jwt.encode({ 'login': login }, cfg.JWT_SECRET, cfg.JWT_ALGORITHM)    
        else:
            return False

    @rpc 
    def check_jwt(self, jwt_token):
        """Validating jwt
        :returns: user login and False if token is not valid"""
        try:
            payload = jwt.decode(jwt_token, cfg.JWT_SECRET, algorithms=cfg.JWT_ALGORITHM)
        except jwt.DecodeError:
            return False
        return payload['login']
