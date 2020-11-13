from nameko_mongodb import MongoDatabase
from nameko.rpc import rpc
from nameko.web.handlers import http
import json
from datetime import datetime


class Logger:
    """Microservice for system logging"""
    # Vars

    name = 'logger'
    db = MongoDatabase()

    # Logic

    def _save_log(self, log):
        collection = self.db["logs"]
        collection.insert_one(
                {"date": log['time'], "service": log["service"], "method": log["method"], 
                "arguments": log["args"], "state": log["state"], "message": log["message"]}
            )

    # API

    @rpc
    def log(self, service, method, arguments, state, message):
        """
        Args:
            service (str) - service's name,
            method (str) - method's name,
            arguments (json serializable!! list in case of many, None or single arg) - method's arguments,
            state (str) - error or OK
            message (str) - info about log
        """
        log = {"time": str(datetime.now()), "service": service, "method": method, "args": arguments,
         "state": state, "message": message}
        self._save_log(log)

    @http('GET', '/full_logs')
    def get_logs_handler(self, request):
        cursor = self.db["logs"].find(
            {}, {"_id": 0,})
        logs = list()
        for row in cursor:
            logs.append(row)
        return 200, json.dumps(logs)

    @http('GET', '/short_logs')
    def get_logs_handler(self, request):
        cursor = self.db["logs"].find(
            {}, {"_id": 0, "arguments": 0})
        logs = list()
        for row in cursor:
            logs.append(row)
        return 200, json.dumps(logs)