# -*- coding: utf-8 -*-

#Python imports
from django.utils import timezone
from django.conf import settings
from django.db.models import F

import random

BASE_PHI = settings.BASE_PHI
PHI_ALEA = settings.PHI_ALEA
MULTIPLIER_RESET = settings.MULTIPLIER_RESET
PHI_FIRST_CALL = settings.PHI_FIRST_CALL
MULTIPLIER_GROWTH = settings.MULTIPLIER_GROWTH
MAX_MULTIPLIER = settings.MAX_MULTIPLIER


def credit_phi(userExtend, phis):
    # using an F-expression makes sure there's no race condition
    # see https://docs.djangoproject.com/en/1.10/ref/models/expressions/#avoiding-race-conditions-using-f
    userExtend.phi = F('phi') + phis * userExtend.phi_multiplier
    userExtend.save()


def credit_phi_from_call(user, time, last_call):
    if user is not None:
        userExtend = user.UserExtend

        if last_call is None: #Cas particulier où le user est nouveau
            credit_phi(
                userExtend,
                BASE_PHI + PHI_FIRST_CALL
            )
            userExtend.phi_multiplier = userExtend.phi_multiplier + MULTIPLIER_GROWTH
            userExtend.first_call_of_the_day = timezone.now()
            userExtend.save()

        else: #Cas général
            #ETAPE 1 : On vérifie si on doit reset le multiplier
            if (timezone.now().timestamp() - last_call > MULTIPLIER_RESET):
                userExtend.phi_multiplier = 1

            #ETAPE 2 : Le joueur gagne des phis
            credit_phi(
                userExtend,
                BASE_PHI + random.randint(-PHI_ALEA, PHI_ALEA)
            )

            #ETAPE 3 : On augmente le multiplier et on vérifie qu'il ne dépasse pas le max
            userExtend.phi_multiplier = min(userExtend.phi_multiplier + MULTIPLIER_GROWTH, MAX_MULTIPLIER)

            #ETAPE 4 : On regarde si on doit accorder le premier appel du jour
            if (timezone.now() - userExtend.first_call_of_the_day).seconds > 3600*24:
                credit_phi(
                    userExtend,
                    PHI_FIRST_CALL
                )
                userExtend.first_call_of_the_day = timezone.now()

            #On sauvegarde tout ça !
            userExtend.save()


def credit_phi_from_achievement(userExtend, achievement):
    credit_phi(userExtend, achievement.phi)
