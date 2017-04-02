import redis

from django.conf import settings
from channels import Channel

from melenchonPB.redis import redis_pool

from .map import getCallerLocation, getCalledLocation, randomLocation
from .phi import credit_phi_from_call
from .score import get_global_scores, update_scores
from .achievements import update_achievements
from ..models import UserExtend, Call


def validate_with_last_call(user, call_time):
    """Make sure call has been made at least MIN_DELAY seconds after the previous one
    
    :param userExtend: the userExtend making the call 
    :param call_time: 
    :return: 
    """

    userExtend = user.UserExtend

    r = redis.StrictRedis(connection_pool=redis_pool)
    timestamp = call_time.timestamp()
    last_call = float(r.getset('lastcall:user:%f' % userExtend.id, timestamp) or 0)

    return (
        last_call is None or (timestamp - last_call > settings.MIN_DELAY),
        last_call
    )


def notify_call(userExtend, called_number):
    """Notify all browsers of the call
    
    :param user_extend: 
    :param called_number: 
    :return: 
    """

    # Latitude et longitude de l'appelant
    callerLat, callerLng = getCallerLocation(userExtend)

    # Latitude et longitude de l'appellé
    if called_number is not None:
        calledLat, calledLng = getCalledLocation(called_number)
    else:
        calledLat, calledLng = randomLocation()

    if userExtend is None:
        id = None
        agentUsername = None
    else:
        id = userExtend.id
        agentUsername = userExtend.agentUsername

    global_scores = get_global_scores()

    message = {
        'type': 'call',
        'value': {
            'call': {
                'caller': {
                    'lat': callerLat,
                    'lng': callerLng,
                    'id': id,
                    'agentUsername': agentUsername},
                'target': {
                    'lat': calledLat,
                    'lng': calledLng}
            },
            'updatedData': global_scores

        }
    }

    Channel('send_message').send(message)


def handle_call(username, called_number, time):
    try:
        user = UserExtend.objects.get(agentUsername=username).user  # On le récupère
    except UserExtend.DoesNotExist:
        # unknown agent username: notify only then return
        notify_call(None, called_number)
        return

    validated, last_call = validate_with_last_call(user, time)

    if validated:
        # On crédite les phis que gagne le user
        Call.objects.create(user=user, date=time)
        credit_phi_from_call(user, time, last_call)
        update_achievements(user)
        notify_call(user.UserExtend, called_number)
        update_scores(user)
