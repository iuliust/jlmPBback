# -*- coding: utf-8 -*-

import random

from django.http import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.views import APIView
from channels import Channel

from callcenter.actions.leaderboard import generate_leaderboards
from callcenter.actions.score import get_global_scores
from callcenter.actions.achievements import get_achievements
from callcenter.actions.calls import handle_call
from callcenter.exceptions import CallerCreationError, CallerValidationError
from callcenter.models import *
from callcenter.serializers import UserSerializer, UserExtendSerializer, CallhubCredentialsSerializer


#################### WEBHOOKS ################################


# /webhook/note
class CallhubWebhookView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data['data']['agent']['username']
        number = request.data['data']['contact']
        now = timezone.now()

        handle_call(username, number, now)
        return Response(status=200)


#################### REST API ################################

# /api/test_websocket/
class TestSocketView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        Channel('send_message').send({'body': request.body})
        return Response(status=200)


# /api/simulate_call/
class SimulateCallView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        users = UserExtend.objects.all()
        nb = users.count()
        user = users[random.randint(0, nb - 1)]
        now = timezone.now()

        handle_call(user.agentUsername, None, now)

        return Response(status=200)


class SimulateAchievementView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        achievements = Achievement.objects.all()
        nb = achievements.count()
        achievement = achievements[random.randint(0, nb - 1)]

        message = {
            'type': 'achievement',
            'value': {
                'agentUsername': 'Jean-René',
                'achievement': {
                    'name': achievement.name,
                    'condition': achievement.condition,
                    'phi': achievement.phi,
                    'codeName': achievement.codeName
                }
            }
        }
        Channel('send_message').send(message)
        return Response(status=200)


# /api/current_user/achievements/
class UserAchievementsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):

        user = request.user
        data = get_achievements(user)

        return Response(data)


# /api/leaderboard/X/ avec X = alltime ou weekly ou daily
class LeaderboardsView(APIView):
    permission_classes = (permissions.AllowAny,)

    @method_decorator(cache_page(60))
    def get(self, request):
        alltime, weekly, daily = generate_leaderboards(50)

        data = {
            'alltime': alltime,
            'weekly': weekly,
            'daily': daily
        }

        print("recalculated")

        return Response(data)


# /api/basic_information/
class BasicInformationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response(get_global_scores())


class UserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_serializer(self, *args, **kwargs):
        return super(UserView, self).get_serializer(*args, **kwargs)

    def get_object(self):
        return self.request.user


class CallerInformationView(RetrieveAPIView, CreateModelMixin):
    serializer_class = UserExtendSerializer

    def get_object(self):
        try:
            return self.request.user.UserExtend
        except UserExtend.DoesNotExist:
            raise Http404

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def post(self, request, *args, **kwargs):
        try:
            # try accessing UserExtend related property to see if it exists
            userExtend = request.user.UserExtend
            raise CallerCreationError("Impossible de créer un agent si l'utilisateur en possède déjà un",
                                      code='already_exists')
        except UserExtend.DoesNotExist:
            return self.create(request, *args, **kwargs)


class AssociateExistingCallerAgentView(CreateAPIView):
    serializer_class = CallhubCredentialsSerializer

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            # try accessing UserExtend related property to see if it exists
            userExtend = request.user.UserExtend
            raise CallerValidationError("Impossible de lier un agent si l'utilisateur en possède déjà un",
                                        code='already_exists')
        except UserExtend.DoesNotExist:
            return super(CreateAPIView, self).create(request, *args, **kwargs)
