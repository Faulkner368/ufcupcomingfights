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
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


class ListFightsIntentHandler(AbstractRequestHandler):
    """Handler for List Fights Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ListFightsIntent")(handler_input)
        
    # Helper methods
    def get_ufc_events_data(self):
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
                fight_date_as_string = fight['event_dategmt']
                fight['event_dategmt'] = self.convert_str_to_date(fight_date_as_string)
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
    
    def get_fights_as_text(self, upcoming_fights, numbers_as_date_str, months):
        """
        Returns upcoming fights as a string to be spoken
        by Alexa. For example:
    
        Alexa: Here are a list of upcoming UFC fights... Adesanya vs Romero on the seventh of march 2020
        """
        
        speak_output = "Here are a list of upcoming UFC fights... "
        
        for fight in upcoming_fights:
            date = fight['event_dategmt']
            date_text = "{day} of {month} {year}".format(day=numbers_as_date_str[str(date.day)], month=months[str(date.month)], year=date.year)
            text = "{title} on the {date}, ".format(title=fight["title"].split(" - ")[1], date=date_text)
            speak_output += text
        
        return speak_output
        
    def get_numbers_as_date_str(self):
        """
        Returns dictionary value from key value pairs where the key is 
        a number digits (str) and the value is the corresponding
        word. For example:
        
        "7": "seventh"
        """
        
        file = open("numbers_as_date_str.json", "r")
        numbers_as_date_str = json.loads(file.read())
        return numbers_as_date_str
        
    def get_month_str_from_number(self):
        """
        Returns dictionary value month from key value pairs
        where the key is the number of month and the value is
        the corresponding string representation. For example:
        
        "5": "may"
        """
        
        file = open("months.json", "r")
        months = json.loads(file.read())
        return months

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        numbers_as_date_str = self.get_numbers_as_date_str()
        months = self.get_month_str_from_number()
        
        fights = self.get_ufc_events_data()
        upcoming_fights = self.upcoming_fights(fights)
        
        if len(upcoming_fights) < 1:
            speak_output = "Sorry, there is either no up coming fights or no data available"
        else:
            speak_output = self.get_fights_as_text(upcoming_fights, numbers_as_date_str, months)

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
sb.add_request_handler(ListFightsIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()