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
        # converting the number from init_base into base 10 using the int method
        converted_num = int(num_to_convert, init_base)

        # converting a number from base 10 into final_base

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
    and the final base.

    Returns: num_to_convert as a string, init_base and final_base as integers
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
    # Creating a list of all the proper chars in the specified base by slicing our BASE_STRING
    chars_in_base = BASE_STRING[base]
    # Note: this algorithm isn't the most efficient, but it will gurantee that num_str is proper
    for i in range(0, len(num_str)):
        if not num_str[i] in chars_in_base:
            return False

    # Returning true only if num_str is proven not to be bad
    return True


def convert_from_ten(num, base, conv=""):
    """
    Converts a number from base 10 into a number of base base
    Takes in a string conv, which keeps track of the conversion process and is returned at the end

    I did this recursively for funsies, but you can do it iteratively by doing something like:
    conv = ""
    while num != 0:
        conv = BASE_STRING[num % base] + conv
        num /= base
    return conv
    """
    if num == 0:
        return conv
    else:
        return convert_from_ten(num / base, base, conv + BASE_STRING[num % base])

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

def build_response(session_attributes, speechlet_response):
    """
    constructs a larger response including session attributes
    """
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
    """
    Method that should build a string of text for the user that is given when the session ends
    in practice though, this method doesn't do anything because the user doesn't need a reprompt
    """
    card_title = "Session Ended"
    # if the session ends / base has been converted properly the user doesn't need a end message
    speech_output = ""
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
    if event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.[amzn1.ask.skill.287421b7-ee96-4331-b4bd-7db736530333]":
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
