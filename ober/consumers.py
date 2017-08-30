import json, logging

from django.apps import apps
from django.conf import settings
from django.http import HttpResponse
from channels import Group
from channels.generic import BaseConsumer
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http


logger = logging.getLogger('ober.routing')




def broadcast(group, message, event_type=settings.OBER_EVENTS_BROADCAST):
  """
  send a message dict
  """
  #logger.debug('BROADCASTING to channel %s, msg %s' % (group,message))
  message.update({
    '_broadcast_group': group,
    '_event_type': event_type
  })
  Group(group).send({
    "text": json.dumps(message),
  })


@channel_session_user
def ws_receive(message):
  # ASGI WebSocket packet-received and send-packet message types
  # both have a "text" key for their textual data.
  Group("pulse-staff").send({
    "text": message.content['text']
  })

  print 'receive %s' % message.content['text']

  

# Connected to websocket.connect
@channel_session_user_from_http
def ws_connect(message):
  logger.debug('connect to channels (user:{0}, role:{1})'.format(message.user.username, message.user.is_staff))
    
  if message.user.is_staff:
    Group("pulse-staff").add(message.reply_channel)
    broadcast("pulse-staff", {
      'welcome': 'welcome to the stuff staff channel.'
    }, event_type=settings.OBER_EVENTS_CONNECT)

  # send per user channel:
  if message.user.is_authenticated:
    Group("pulse-%s" % message.user.username ).add(message.reply_channel)
    broadcast("pulse-%s" % message.user.username, {
      'welcome': 'welcome to your own channel, {0}.'.format(message.user.username)
    }, event_type=settings.OBER_EVENTS_CONNECT)

  # global lite channel disabled
  Group("pulse").add(message.reply_channel)
  broadcast("pulse", {'welcome': 'welcome to the lite notification channel. Public notifications are here.'})

# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
  logger.debug('disconnect to channels (user:{0}, role:{1})'.format(message.user.username, message.user.is_staff))
    
  if message.user.is_staff:
    Group("pulse-staff").discard(message.reply_channel)

  if message.user.is_authenticated:
    Group("pulse-%s" % message.user.username).discard(message.reply_channel)

  Group("pulse").discard(message.reply_channel)

