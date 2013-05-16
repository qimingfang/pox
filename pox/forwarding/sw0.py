from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time

log = core.getLogger()
_flood_delay = 0

class LearningSwitch (object):
  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Our table
    self.macToPort = {}

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)

    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    #log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))

  def _handle_PacketIn (self, event):
    packet = event.parsed
    print "in port is ", event.port
    log.debug("%i: %s -> %s", event.dpid,packet.src,packet.dst)
   
    if event.port == 4:
      msg = of.ofp_flow_mod()
      msg.match.in_port = event.port
      msg.idle_timeout = 10
      msg.hard_timeout = 30
      msg.actions.append(of.ofp_action_output(port=2))
      msg.actions.append(of.ofp_action_output(port=3))
      self.connection.send(msg)
      
    else:
      msg = of.ofp_flow_mod()
      msg.match.in_port = event.port
      msg.idle_timeout = 10
      msg.hard_timeout = 30
      msg.actions.append(of.ofp_action_output(port=4))
      self.connection.send(msg)
"""
    for actual_port in self.connection.features.ports:
      port = actual_port.port_no
      
      #print "my port", str(port)
      #print "event port", str(event.port)

      if port != event.port and port != 65534:
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30

        msg.actions.append(of.ofp_action_output(port=event.port))
        self.connection.send(msg)
"""

class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))
