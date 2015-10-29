"""
Create and manipulate wiremock sessions in python.
Create Json mappings for stubbing and verification.
"""
from subprocess import Popen, CREATE_NEW_CONSOLE, PIPE
from os import path
import requests
import json

__author__ = 'thaffenden'


class Wiremock(object):
    """
    All configurable items for the wiremock session should be configurable.
    """

    def __init__(self, port="8080", standalone_path=".\\Wiremock\\",
                 version="1.57", arguments=None):
        # Set the path in your project to the directory containing the
        # wiremock .jar
        self.wiremock_dir = standalone_path
        # Pass any additional arguments you may want to use, the full list
        # can be found at: http://wiremock.org/running-standalone.html
        if arguments is None:
            arguments = '--root-dir {}'.format(standalone_path)

        # Specify the port you want to run wiremock on. Defaults to Wiremock's
        # default 8080
        self.wiremock_port = port

        # URLs for wiremock interaction
        self.base_url = "http://localhost:{}".format(self.wiremock_port)

        # Shell command to start wiremock
        self.wiremock = str("java -jar {d}wiremock-{a}-standalone.jar "
                            "--port {b} {c}".format(a=version,
                                                    b=self.wiremock_port,
                                                    c=arguments,
                                                    d=self.wiremock_dir))

        self.wiremock_process = True

    def start(self, status_print=True):
        """
        Set status print to False in the call to this method is you don't
        want the wiremock details output to the console
        :param status_print:
        :return:
        """
        self.wiremock_process = Popen(self.wiremock, stdout=PIPE,
                                      creationflags=CREATE_NEW_CONSOLE)
        if status_print:
            # The below print statements are for the Wiremock title print like
            # running wiremock as it's usual stand alone would.
            print("\n{}\n".format(self.wiremock))
            print(str(r" /$$      /$$ /$$                     /$$      /$$    "
                      r"                 /$$"))
            print(str(r"| $$  /$ | $$|__/                    | $$$    /$$$    "
                      r"                | $$"))
            print(str(r"| $$ /$$$| $$ /$$  /$$$$$$   /$$$$$$ | $$$$  /$$$$  /$"
                      r"$$$$$   /$$$$$$$| $$   /$$"))
            print(str(r"| $$/$$ $$ $$| $$ /$$__  $$ /$$__  $$| $$ $$/$$ $$ /$$"
                      r"__  $$ /$$_____/| $$  /$$/"))
            print(str(r"| $$$$_  $$$$| $$| $$  \__/| $$$$$$$$| $$  $$$| $$| $$"
                      r"  \ $$| $$      | $$$$$$/"))
            print(str(r"| $$$/ \  $$$| $$| $$      | $$_____/| $$\  $ | $$| $$"
                      r"  | $$| $$      | $$_  $$"))
            print(str(r"| $$/   \  $$| $$| $$      |  $$$$$$$| $$ \/  | $$|  $"
                      r"$$$$$/|  $$$$$$$| $$ \  $$"))
            print(str(r"|__/     \__/|__/|__/       \_______/|__/     |__/ \__"
                      r"____/  \_______/|__/  \__/"))
            print("\nPort: {}".format(self.wiremock_port))

    def stop(self):
        """
        Kill wiremock process by sending empty post to the shutdown url
        :return:
        """
        requests.post(url="{}/__admin/shutdown".format(self.base_url))
        print(str("Wiremock Session Terminated"))

    def reset(self):
        """
        Reset the current use mappings for when mapping creation is needed
        on the fly
        :return:
        """
        requests.post(url="{}/__admin/mappings/reset".format(self.base_url))

    def save(self):
        """
        Save the mappings created while Wiremock was running.
        :return:
        """
        requests.post(url="{}/__admin/mappings/save".format(self.base_url))

    def get(self, url, params=None):
        """
        Post a get to the specified URL. Pass the extension after local host
        as the url argument.
        Literally just a pass-through for the requests module get function, so
        you don't have to import requests into the main project file as well.
        :param url:
        :param params:
        :return:
        """
        return requests.get(url="{a}{b}".format(a=self.base_url, b=url),
                            params=params)

    def add_fixed_delay(self, delay_ms):
        """
        Add a fixed delay to the response times. Times in MS.
        :param delay_ms:
        :return:
        """
        delay_json = {'fixedDelay': delay_ms}
        requests.post(url="{}/__admin/socket-delay".format(self.base_url),
                      json=delay_json)

    def create_mapping_file(self, request_method, url, response_headers,
                            status, response_body, file_name=None):
        """
        Create a JSON mapping file in wiremock's mapping directory (using the
        directory specified in __init__) for verification without having the
        mappings created prior.
        The response may contain a number of items, so should be passed a
        dictionary of everything required in the response.
        :param request_method:
        :param url:
        :param response_dict:
        :param file_name:
        :return:
        """
        j_file = json.dumps({"request": {"url": '{}'.format(url),
                                         "method": '{}'.format(
                                             request_method)},
                             "response": {"status": status,
                                          "headers": response_headers,
                                          "body": response_body}},
                            sort_keys=True, indent=4)

        if file_name is None:
            file_name = "mapping.json".format()

        json_path = path.abspath(r"{a}mappings\{b}".format(a=self.wiremock_dir,
                                                           b=file_name))

        with open(json_path, 'w') as json_file:
            json_file.write(j_file)

        print("Mapping File Created: {}".format(json_path))
