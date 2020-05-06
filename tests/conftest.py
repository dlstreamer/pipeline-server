import pytest
import subprocess
import json
import psutil
import time
import requests
from collections import namedtuple
import os
import sys

TIMEOUT=30
MAX_CONNECTION_ATTEMPTS = 5
class VAServingService:

    VASERVING_ARGS=["python3", "-m","vaserving"]

    def __del__(self):
        if (self._process):
            self._process.kill()

    def kill_all(self):
        for proc in psutil.process_iter():
            if "vaserving" in proc.cmdline():
                proc.kill()
            
    def __init__(self):    

        self.kill_all()
        self.host = "http://localhost:8080"

        self._process = subprocess.Popen(VAServingService.VASERVING_ARGS,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         bufsize=1,
                                         universal_newlines=True)
       
        self._process.poll()
        while self._process.returncode is None:
            next_line = self._process.stderr.readline()
            try:
                if next_line:
                    message = json.loads(next_line)
                    if message["levelname"] == "ERROR":
                        raise Exception(next_line)
                    
                    if message["message"] == "Starting Tornado Server on port: 8080":
                        attempts = MAX_CONNECTION_ATTEMPTS
                        while (attempts):
                            try:
                                result = requests.get("http://localhost:8080",timeout=TIMEOUT)
                            except requests.ConnectionError as error:
                                time.sleep(1)
                                attempts-=1
                            else:
                                return
                        raise Exception("VA Serving Not Launched")
            except Exception as error:
                self._process.kill()
                self._process = None
                assert False, "VA Serving Not Launched"
                raise

            self._process.poll()
            
        if self._process.returncode != 0:
            assert False

            
    def get_models():
        pass


def pytest_addoption(parser):
    parser.addoption("--generate", action="store_true", help="generate expected results", default=False)
    parser.addoption("--framework", help="ffmpeg or gstreamer", choices=['ffmpeg','gstreamer'],default=os.environ["FRAMEWORK"])


def load_rest_api_test_cases(metafunc):

    known_frameworks = ['ffmpeg','gstreamer']
    
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"test_cases","rest_api")

    filenames = [(os.path.abspath(os.path.join(dir_path,fn)),os.path.splitext(fn)[0]) for fn in os.listdir(dir_path)
                 if os.path.isfile(os.path.join(dir_path,fn)) and os.path.splitext(fn)[1]=='.json']

    framework = metafunc.config.getoption("framework")

    filenames = [ filename for filename in filenames
                  if filename[1].split('_')[-1] == framework or
                  filename[1].split('_')[-1] not in known_frameworks]

    test_cases = []
    test_names = []
    generate = metafunc.config.getoption("generate")
    for filepath,testname in filenames:
        try:
            with open(filepath) as json_file:
                test_cases.append((json.load(json_file),filepath,generate))
                test_names.append(testname)
        except:
            pass
        
    return (test_cases,test_names)
        
def pytest_generate_tests(metafunc):

    test_cases,test_names = load_rest_api_test_cases(metafunc)
    if ("rest_api" in metafunc.function.__name__):
        metafunc.parametrize("test_case,test_filename,generate",test_cases,ids=test_names)
    
    print(metafunc.fixturenames)
    print(metafunc.function,flush=True)

@pytest.fixture(scope="session")
def service(request):
    proxy = VAServingService()
    yield proxy
    del proxy
        
