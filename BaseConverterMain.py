"""
Created by Zac Patel on 1/19/17
Github: https://github.com/zbpatel/AlexaBaseConverter
Please give attribution if branching off my code.
DO NOT publish or commericalize this code without my permission.
"""

# import for default (amazon) behavior
from __future__ import print_function

# this string is meant to be used as a reference to find the character that
# corresponds to a given value 0-36
BASE_STRING = "0123456789abcdefghijklmnopqrstuvwxyz"

# logic for handling the base conversion
# Intents that lead to this method: CONVERTBASEINTENT
def base_converter_intent_handler(intent):
    """
    Central logic method to handle intent requests for the UserWarning
    This method will handle the CONVERTBASEINTENT, which is currently the only intent
    At the end of this method, a completed response will be returned
    """
    num_to_convert, init_base, final_base = pull_bases_from_intent(intent)

    # constructing a special message if any of the input variables are bad
    # note, its not the most space efficient code to have, but having a large if/else  
    # allows for "contextualized" error messages that let the user know what to fix

    if num_to_convert == NO_INPUT or num_to_convert == INPUT_NOT_NUMBER:
        title = "Failed to Convert Base"
        output = "Sorry, I did not hear your number to convert." + num_to_convert
        card_output = output
        reprompt_text = "Please try again while providing me a number."
        should_end_session = False
    elif final_base == NO_INPUT or final_base == INPUT_NOT_NUMBER:
        title = "Failed to Convert Base"
        output = "Sorry, I did not hear your final base." + final_base
        card_output = output
        reprompt_text = "Please try again with a proper number for the final base."
        should_end_session = False
    elif init_base == INPUT_NOT_NUMBER:
        title = "Failed to Convert Base"
        output = "Sorry, I did not hear your initial base."
        card_output = output
        reprompt_text = "Please try again while providing me a number."
        should_end_session = False
    # If the numbers are integers, we check to see if they are within proper boundaries
    elif init_base < 1 or init_base > 10:
        title = "Failed to Convert Base"
        output = "I could not handle your request, because your initial base was not between 1 and 10."
        card_output = output
        reprompt_text = "Please try again with a base between 1 and 10."
        should_end_session = False
    elif final_base < 1 or final_base > 36:
        title = "Failed to Convert Base"
        output = "I could not handle your request, because your final base was not between 1 and 36."
        card_output = output
        reprompt_text = "Please try again with a base between 1 and 36."
        should_end_session = False
    elif not is_in_base(str(num_to_convert), init_base):
        title = "Failed to Convert Base"
        output = str(process_output(num_to_convert, init_base)) + " is not a valid base " + str(init_base) + " number."
        card_output = str(num_to_convert) + " is not a valid base " + str(init_base) + " number."
        reprompt_text = "Please try again with a base between 1 and 36."
        should_end_session = False
    else:
        # converting the number from init_base into base 10 using the int method
        converted_num = int(str(num_to_convert), init_base)

        # converting a number from base 10 into final_base
        converted_num = convert_from_ten(converted_num, final_base)
        # wow, isn't it exciting?  that's where all the magic happens

        title = "Base Converted"
        output = str(num_to_convert) + " in base " + str(final_base) + " is " + str(process_output(converted_num, final_base)) + "."
        card_output = str(num_to_convert) + " in base " + str(final_base) + " is " + str(converted_num) + "."

        reprompt_text = ""
        should_end_session = True

    session_attributes = ""
    return build_response(session_attributes, build_speechlet_response(title, output, card_output, reprompt_text, should_end_session))

# adds spaces between each letter in the word if the base is greater than 10
# this prevents Alexa from trying to read strings of letters as a weird sounding word
def process_output(converted_num, base):
    if base > 10:
        processed_num = ""
        for digit in str(converted_num):
            processed_num = processed_num + digit + " "

        # setting up a substring slice so we can pull the trailing space off easily
        adjust = len(processed_num) - 1
        return processed_num[:adjust]
    else: # no additional processing is needed if there are no letters in the converted num
        return str(converted_num)

# separating the method to pull bases from an intent so that we only need one converter handler
def pull_bases_from_intent(intent):
    """
    Given a CONVERTBASEINTENT, pulls the number to convert, the initial base (if specified)
    and the final base.

    Returns: num_to_convert as a string, init_base and final_base as integers
    """
    # Reading the input values as per the guidelines:
    # https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/handling-requests-sent-by-alexa#invalid-numeric-date-time-and-duration-slots

    # first, we must move to searching through the intent slots
    intent = intent["slots"]

    # pulling the values from the intent, and attempting to convert them to integers
    num_to_convert = process_num(intent["toConvert"]["value"])
    init_base = process_num(intent["initBase"]["value"])
    final_base = process_num(intent["finalBase"]["value"])

    # allowing the user to not specify an initial base, and have it defaytk to 10
    if init_base == NO_INPUT:
        init_base = 10
    return num_to_convert, init_base, final_base

# number processing error messages
NO_INPUT = "no input detected"
INPUT_NOT_NUMBER = "input is not a number"

# method to convert an intent value into an integer, and trap errors
def process_num(num):
    """
    Attempts to convert the provided num (as a string) into an integer
    if the input is "?" (what Alexa passes if there is no input), return NO_INPUT
    if the input errors when attempting to convert to an intger, return INPUT_NOT_NUMBER
    otherwise, return the number converted to an int
    """
    if num != "?" and num != None:
        try:
            num = int(num)
        except ValueError:
            return INPUT_NOT_NUMBER
        return num
    return NO_INPUT

# Note: for this method, num should be a string (to allow for bases higher than 10)
def is_in_base(num_str, base):
    """
    Returns True if the num is a valid number in base "base"
    (Returns False otherwise)

    Handles bases up to 36
    """
    # Creating a list of all the proper chars in the specified base by slicing our BASE_STRING
    chars_in_base = BASE_STRING[:base]
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
        return convert_from_ten(num / base, base, BASE_STRING[num % base] + conv)

# --------------- Helpers that build all of the responses ----------------------

# Turns the various info in a response into an alexa readable response

# Turns the various info in a response into an alexa readable response
def build_speechlet_response(title, output, card_text, reprompt_text, should_end_session):
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
            'title': title,
            'content': card_text
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
        'version': '1.0.D', # NOTE: update this with current app version
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

# Intents that lead to this method: when no intent is specified, AMAZON.HelpIntent
def get_welcome_response():
    """
    Prompts the user for a response if they don't say anything when starting the session
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Tell me a number, and a base up to 36, and I can convert it for you."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Would you like me to convert a number?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))

# Intents that lead to this method: AMAZON.CancelIntent
def handle_session_end_request():
    """
    Method that should build a string of text for the user that is given when the session ends
    in practice though, this method doesn't do anything because the user doesn't need a reprompt
    """
    card_title = "Session Ended"
    # if the session ends / base has been converted properly the user doesn't need a end message
    speech_output = "" #Thank you for using Base Converter."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, speech_output, None, should_end_session))

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

# Selects which behavior the skill will have based on starting intent
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    # using the pull_bases_from_intent method allows us to handle everything through one intent
    if intent_name == "CONVERTBASEINTENT":
        return base_converter_intent_handler(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
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
    if event['session']['application']['applicationId'] != "amzn1.ask.skill.287421b7-ee96-4331-b4bd-7db736530333":
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
