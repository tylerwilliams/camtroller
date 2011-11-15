import logging
import pprint
import urllib
import urllib2

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

CONTROL_ENDPOINT = "PANTILTCONTROL.CGI"
DIRECTIONS = enum("UP", "DOWN", "LEFT", "RIGHT")
logger = logging.getLogger(__name__)

class Camera(object):
    def __init__(self, host, username, password, port=80):
        global CONTROL_ENDPOINT
        self.endpoint = "http://%s:%s/%s" % (host, str(port), CONTROL_ENDPOINT)
        auth = urllib2.HTTPBasicAuthHandler()
        auth.add_password(None, self.endpoint, user=username, passwd=password)
        self.url_opener = urllib2.build_opener(auth)
        
    def _send_cmd(self, cmd):
        data = urllib.urlencode(cmd)
        try:
            logging.debug("POST %s, <== %s", self.endpoint, pprint.pformat(cmd))
            fh = self.url_opener.open(self.endpoint, data=data)
            logging.debug(fh.read())
        except Exception:
            logger.exception("something went wrong")
    
    def home(self):
        self._send_cmd( {'PanTiltSingleMove':'4'} )

    def pan(self, steps, direction):
        assert direction==DIRECTIONS.RIGHT or direction==DIRECTIONS.LEFT
        self.move(steps, direction, 0, 0)

    def tilt(self, steps, direction):
        self.move(0, 0, steps, direction)

    def go_to_preset(self, position):
        self._send_cmd({"PanTiltPresetPositionMove" : position})

    def clear_preset(self, position):
        self._send_cmd({"ClearPosition" : position})
    
    def set_preset(self, pan_pos, tilt_pos, pos_name, position):
        self._send_cmd({"PanTiltHorizontal" : pan_pos, "PanTiltVertical" : tilt_pos, "SetName" : pos_name, "SetPosition" : position})

    def move(self, pan_steps, pan_dir, tilt_steps, tilt_dir):
        if (pan_steps > 0 and pan_dir == DIRECTIONS.RIGHT):
            if (tilt_steps > 0 and tilt_dir == DIRECTIONS.UP):
                val = 2 # up right
            elif (tilt_steps > 0 and tilt_dir == DIRECTIONS.DOWN):
                val = 8 # down right
            else:
                val = 5 # right
        elif (pan_steps > 0 and pan_dir == DIRECTIONS.LEFT):
            if (tilt_steps > 0 and tilt_dir == DIRECTIONS.UP):
                val = 0 # up left
            elif (tilt_steps > 0 and tilt_dir == DIRECTIONS.DOWN):
                val = 6 # down left
            else:
                val = 3 # left
        else:
            if (tilt_steps > 0 and tilt_dir == DIRECTIONS.UP):
                val = 1 # up
            elif (tilt_steps > 0 and tilt_dir == DIRECTIONS.DOWN):
                val = 7 # down
        self._send_cmd({"PanSingleMoveDegree" : pan_steps, "TiltSingleMoveDegree" : tilt_steps, "PanTiltSingleMove" : val})

