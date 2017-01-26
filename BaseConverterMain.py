"""
Created by Zac Patel on 1/19/17
Github: https://github.com/zbpatel/AlexaBaseConverter
Please give attribution if branching off my code.
DO NOT publish or commericalize this code without my permission.
"""

# import for default (amazon) behavior
from __future__ import print_function

# this string is meant to be used as a reference to find the character that
# corresponds to a given value 0-32
BASE_STRING = "0123456789abcdefghijklmnopqrstuvwxyz"

# logic for handling the base conversion
def base_converter_intent_handler(intent):
    """
    Central logic method to handle intent requests for the UserWarning
    This method will handle the BASECONVERTERINTENT, which is currently the only intent
    At the end of this method, a completed response will be returned
    """
    num_to_convert, init_base, final_base = pull_bases_from_intent(intent)

    if init_base < 1 or init_base > 9:
        title = "Failed to Convert Base"
        output = "Failed to convert, because your initial base is not between 1 and 10."
        reprompt_text = ""
        should_end_session = False
    elif final_base < 1 or final_base > 32:
        title = "Failed to Convert Base"
        output = "Failed to convert, because your final base is not between 1 and 32."
        reprompt_text = ""
        should_end_session = False
    else:
        converted_num = int()
        title = "Base Converted"
        output = num_to_convert + " in base " + final_base + " is " + converted_num
        reprompt_text = ""
        should_end_session = True

    session_attributes = ""
    return build_response(session_attributes, build_speechlet_response(title, output, reprompt_text, should_end_session))

# separating the method to pull bases from an intent so that we only need one converter handler
def pull_bases_from_intent(intent):
    """
    Given a BASECONVERTERINTENT, pulls the number to convert, the initial base (if specified)
    and the final base. (and returns them to the user)
    """
    # pulling the various user inputs from the intent
    # note, we don't conver the actual number to an int, because
    # we are going to use the int method later to convert it to its first base
    num_to_convert = intent["to_convert"]["value"]
    # note, init_base cannot be greater than 10, because it is unclear if AMAZON.NUMBER
    # handles number in base > 10

    # we don't specify an exception type here because we aren't doing anything with that info
    try:
        init_base = int(intent["init_base"]["value"])
    except: 
        init_base = 10

    final_base = int(intent["final_base"]["value"])

    return num_to_convert, init_base, final_base

# Note: for this method, num should be a string (to allow for bases higher than 32)
def is_in_base(num_str, base):
    """
    Returns True if the num is a valid number in base base
    (Returns False otherwise)

    Handles bases up to 32
    """
    for i in range(0, len(num_str)):
        if num_str[i] > base:
            return False
        i += 1

    return True

# Converts a number in non-base 10 to base 10
def convertToTen(num, base):
    """
    converts an integer in base 2-10 to base 10
    """
    # checking that the base is an integer (and not a string / double)
    # this isn't really necessary because base should never be int anyways, but its good practice
    assert base.isinstance(int)

    converted_num, position = 0, 1

    # note we don't check that the number is in the proper base, because we do that elsewhere
    while num > 10:
        converted_num += (num % 10) * base ** position
        num /= 10
        
    return converted_num



# --------------- Helpers that build all of the responses ----------------------

# Turns the various info in a response into an alexa readable response
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """
    Amazon provided method that handles the construction of speech responses
    """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

# constructs a larger response including session attributes
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """
    Prompts the user for a response if they don't say anything when starting the session
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Tell me a number, and I can convert it to any base up to 32."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me a number, and a base between 2 and 32, and I can convert it."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "" # if the session ends / base has been converted properly the user doesn't need a end message
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    # using the pull_bases_from_intent method allows us to handle everything through one intent
    if intent_name == "BASECONVERTERINTENT":
        return base_converter_intent_handler(intent)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.[amzn1.ask.skill.287421b7-ee96-4331-b4bd-7db736530333]"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
