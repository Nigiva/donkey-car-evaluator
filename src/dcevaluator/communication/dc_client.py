from loguru import logger
from dcevaluator.communication.basic_client import BasicClient
import json
import re

class DonkeyCarClient(BasicClient):

    def __init__(self, event_handler, host = "127.0.0.1", port = 9091):
        super().__init__(host, port)
        self.event_handler = event_handler

    def on_request_receive(self, request_string):
        super().on_request_receive(request_string)

        request = json.loads(self.replace_float_notation(request_string))

        if "msg_type" in request:
            msg_type = request["msg_type"]
            if msg_type == "scene_selection_ready":
                self.on_scene_selection_ready(request)
            elif msg_type == "scene_loaded":
                self.on_scene_loaded(request)
            elif msg_type == "car_loaded":
                self.on_car_loaded(request)
            elif request["msg_type"] == "telemetry":
                self.on_telemetry(request)
            else:
                logger.info(request_string)


    #############
    ### Event ###
    #############

    def on_scene_selection_ready(self, request):
        self.event_handler.on_scene_selection_ready(request)
    
    def on_scene_loaded(self, request):
        self.event_handler.on_scene_loaded(request)

    def on_car_loaded(self, request):
        self.event_handler.on_car_loaded(request)
        self.event_handler.car_is_ready = True

    def on_telemetry(self, request):
        self.event_handler.on_telemetry(request)
        logger.info("Node : " + str(request["activeNode"]) + " / distance2center (cte) : " + str(request["cte"]))

    def on_exit_scene(self, request):
        self.event_handler.on_exit_scene(request)

    def on_quit_app(self, request):
        self.event_handler.on_quit_app(request)

    def each_turn(self, request):
        self.event_handler.each_turn(request)

    def each_node(self, request):
        self.event_handler.each_node(request)

    def on_car_leaving_road(self, request):
        self.event_handler.on_car_leaving_road(request)


    ####################
    ### Send request ###
    ####################

    def send_get_protocol_version_request(self):
        """
        Ask for the version of the protocol. Will help know when changes are made to these messages.
        """
        request = dict()
        request["msg_type"] = "get_protocol_version"
        self.send_message(json.dumps(request))
    
    def send_get_scene_names_request(self):
        """
        Ask names of the scene you can load. (Menu only)
        """
        request = dict()
        request["msg_type"] = "get_scene_names"
        self.send_message(json.dumps(request))

    def send_load_scene_request(self, scene):
        """
        Asks the sim to load one of the scenes from the Menu screen. (Menu only)

        :param scene: generated_road | warehouse | sparkfun_avc | generated_track (or whatever list the sim returns from get_scene_names)
        """
        request = dict()
        request["msg_type"] = "load_scene"
        request["scene_name"] = str(scene)
        self.send_message(json.dumps(request))
    
    def send_car_config_request(self, body_style, body_r, body_g, body_b, car_name, font_size):
        """
        Once loaded, you may configure your car visual details (scene only)

        :param body_style: donkey | bare | car01 | cybertruck | f1
        :param body_r: string value of integer between 0-255
        :param body_g: string value of integer between 0-255
        :param body_b: string value of integer between 0-255
        :param car_name: string value car name to display over car. Newline accepted for multi-line.
        :param font_size: string value of integer between 10-100 to set size of car name text
        """
        request = dict()
        request["msg_type"] = "car_config"
        request["body_style"] = str(body_style)
        request["body_r"] = str(body_r)
        request["body_g"] = str(body_g)
        request["body_b"] = str(body_b)
        request["car_name"] = str(car_name)
        request["font_size"] = str(font_size)
        self.send_message(json.dumps(request))
    
    def send_cam_config_request(self, fov=100, fish_eye_x=0, fish_eye_y=0, img_w=160, img_h=120, img_d=3, img_enc="PNG", offset_x=0.0, offset_y=3.5, offset_z=0.0, rot_x=90.0):
        """
        Once the scene is loaded, you may configure your car camera sensor details.

        :param fov: string value of float between 10-200. Sets the camera field of view in degrees.
        :param fish_eye_x: string value of float between 0-1. Causes distortion warping in x axis.
        :param fish_eye_y: string value of float between 0-1. Causes distortion warping in y axis.
        :param img_w: string value of integer between 16-512. Sets camera sensor image width.
        :param img_h: string value of integer between 16-512. Sets camera sensor image height.
        :param img_d: string value of integer 1 or 3. Sets camera sensor image depth. In case of 1, you get 3 channels but all identicle with greyscale conversion done on the sim.
        :param img_enc: Image format of data JPG | PNG | TGA
        :param offset_x: string value of float. Moves the camera left and right axis.
        :param offset_y: string value of float. Moves the camera up and down.
        :param offset_z: string value of float. Moves the camera forward and back.
        :param rot_x: string value of float. Degrees. Rotates camera around X axis.
        """
        request = dict()
        request["msg_type"] = "cam_config"
        request["fov"] = str(fov)
        request["fish_eye_x"] = str(fish_eye_x)
        request["fish_eye_y"] = str(fish_eye_y)
        request["img_w"] = str(img_w)
        request["img_h"] = str(img_h)
        request["img_d"] = str(img_d)
        request["img_enc"] = str(img_enc)
        request["offset_x"] = str(offset_x)
        request["offset_y"] = str(offset_y)
        request["offset_z"] = str(offset_z)
        request["rot_x"] = str(rot_x)
        self.send_message(json.dumps(request))

    def send_car_control_request(self, angle, throttle, brake):
        """
        Send car control (angle/steering, throttle, brake)

        :param steering: string value of float between -1 to 1. Maps to full left or right, 16 deg from center.
        :param throttle: string value of float between -1 to 1. Full forward or reverse torque to wheels.
        :param brake: string value of float between 0 to 1.

        """
        request = dict()
        request["msg_type"] = "control"
        request["steering"] = str(angle)
        request["throttle"] = str(throttle)
        request["brake"] = str(brake)
        self.send_message(json.dumps(request))
    
    def send_reset_car_request(self):
        """
        Return the car to the start point.
        """
        request = dict()
        request["msg_type"] = "reset_car"
        self.send_message(json.dumps(request))
    
    def send_node_position_request(self, index):
        """
        Ask for a node_position packet
        :param index: node index.
        """
        request = dict()
        request["msg_type"] = "set_position"
        request["index"] = str(index)
        self.send_message(json.dumps(request))
    
    def send_exit_scene_request(self):
        """
        Leave the scene and return to the main menu screen.
        """
        request = dict()
        request["msg_type"] = "exit_scene"
        self.send_message(json.dumps(request))

    def send_quit_app_request(self):
        """
        Close the sim executable. (Menu only)
        """
        request = dict()
        request["msg_type"] = "quit_app"
        self.send_message(json.dumps(request))


    #############
    ### Utils ###
    #############

    @staticmethod
    def replace_float_notation(string):
        """
        Replace unity float notation for languages like
        French or German that use comma instead of dot.
        This convert the json sent by Unity to a valid one.
        Ex: "test": 1,2, "key": 2 -> "test": 1.2, "key": 2

        :param string: (str) The incorrect json string
        :return: (str) Valid JSON string
        """
        regex_french_notation = r'"[a-zA-Z_]+":(?P<num>[0-9,E-]+),'
        regex_end = r'"[a-zA-Z_]+":(?P<num>[0-9,E-]+)}'

        for regex in [regex_french_notation, regex_end]:
            matches = re.finditer(regex, string, re.MULTILINE)

            for match in matches:
                num = match.group('num').replace(',', '.')
                string = string.replace(match.group('num'), num)
        return string
