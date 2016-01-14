import os
from flask import Flask, jsonify

class Driver:
    '''
        Holds the driver state so the flasked script can change behaviour based
        on what the user injects via HTTP
    '''
    name = None
    base_path = None

    def root(self, base_path):
        self.base_path = base_path

    def start(self, name):
        filename = os.path.join(self.base_path,
                                '{}.yaml'.format(name))

        if not os.path.exists(filename):
            return {"state": "error", "message": "Driver {} not found".format(filename)}

        self.name = name
        return {"driver": self.name, "state": "started"}

    def stop(self):
        if self.name == None:
            return {"driver": None, "state": None}

        message = {"driver": self.name, "state": "stopped"}
        self.name = None
        return message

    def state(self):
        if self.name == None:
            return {"driver": None, "state": None}

        return {"driver": self.name, "state": "running"}

driver_host = "proxapp"
driver_port = 5000
driver_endpoint = "http://{}:{}".format(driver_host, driver_port)
app = Flask(driver_host)
app.host = '127.0.0.1'
driver = Driver()

def register(context):
    driver.root(context.source_dir)
    context.app_registry.add(app, driver_host, driver_port)
    return context

# Links use https://tools.ietf.org/html/rfc6570 URI templates
# The data structure is close to JSON API http://jsonapi.org/
@app.route('/', defaults={"path": ""})
@app.route('/<path:path>/')
def index(path):
    return jsonify({"links": {"self": driver_endpoint,
                              "start": "{}/{{driver}}/start/".format(driver_endpoint),
                              "stop": "{}/stop/".format(driver_endpoint),
                              "state": "{}/state/".format(driver_endpoint)}})

@app.route('/state/')
def state():
    message = driver.state()
    print(message)
    return jsonify(message)

@app.route('/stop/')
def stop_driver():
    message = driver.stop()
    print(message)
    return jsonify(message)

@app.route('/<driver_name>/start/')
def start_driver(driver_name):
    message = driver.start(driver_name)
    print(message)
    return jsonify(message)