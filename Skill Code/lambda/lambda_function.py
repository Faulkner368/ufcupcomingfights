# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import requests
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

numbers_as_ordinal = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eigth", 9: "ninth",
                    10: "tenth", 11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth", 15: "fifteenth", 16: "sixteenth",
                    17: "seventeenth", 18: "eighteenth", 19: "nineteenth", 20: "twentieth", 21: "twenty first", 22: "twenty second",
                    23: "twenty third", 24: "twenty fourth", 25: "twenty fifth", 26: "twenty sixth", 27: "twenty seventh", 28: "twenty eighth",
                      29: "twenty ninth", 30: "thirtieth", 31: "thirty first"}

months = {1: "january", 2: "february", 3: "march", 4: "april", 5: "may", 6: "june",
          7: "july", 8: "august", 9: "september", 10: "october", 11: "november", 12: "december"}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to upcoming fights, ask me to list fights"
        reprompt = "Ask me to list fights"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt)
                .response
        )


class listFightsIntentHandler(AbstractRequestHandler):
    """Handler for List Fights Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ListFightsIntent")(handler_input)
        
    # Helper methods
    def get_ufc_events_data(self) -> list:
    """
    Returns a list of past and future fights as
    a list of objects. The object attributes are:

    ['id', 'title', 'subtitle', 'event_dategmt', 'url_name']
    """
    
    url = "http://api.ufc.com/bars/events.json"

    response = requests.get(url)

    if response.status_code == 200:
        fights = response.json()
        for fight in fights:
            fight_data_as_string = fight['event_dategmt']
            fight['event_dategmt'] = convert_str_to_date("", fight_data_as_string)
        return fights
    else:
        return False

    def convert_str_to_date(self, date_as_string):
        """
        Converts a datetime string to a datetime object and returns
        the datetime object.
        """
    
        return datetime.datetime.strptime(date_as_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    def upcoming_fights(self, fights):
        """
        Returns only the future fights from a list of fight objects
        """
    
        upcoming_fights = []
        for fight in fights:
            if fight['event_dategmt'] > datetime.datetime.now():
                upcoming_fights.append(fight)
    
        return upcoming_fights
    
    def get_fights_as_text(self, fights):
        """
        Returns upcoming fights as a string to be spoken
        by Alexa. For example:
    
        Alexa: Here are a list of upcoming UFC fights... Adesanya vs Romero on the seventh of march 2020
        """
        
    
        speak_out = "Here are a list of upcoming UFC fights... "
    
        for fight in upcoming_fights:
            date = fight['event_dategmt']
            date_text = "{day} of {month} {year}".format(day=numbers_as_ordinal[date.day], month=months[date.month], year=date.year)
            text = "{title} on the {date}, ".format(title=fight["title"].split(" - ")[1], date=date_text)
            speak_out += text
        
        return speak_out

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        fights = get_ufc_events_data()
        upcoming_fights = upcoming_fights(fights)
        speak_out = get_fights_as_text(upcoming_fights)

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say list fights to me and I will list upcoming fights"
        reprompt = "Ask me to list fights and I will list all upcoming fights"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ListFightsIntentIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()