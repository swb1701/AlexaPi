"""
Skill to handle speech commands to be executed on the Raspberry Pi.  This
is a modified version of the sample colors skill.
"""

#Scott Bennett, 1/17

from __future__ import print_function
import boto3
import json

sqs=boto3.client('sqs')
queue='PLACE-SQS-QUEUE-URL-HERE'

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
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
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Sally -- A Friend for Alexa. "
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask Sally something."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for working with Sally. "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

#handle speak command
def speak_intent(intent, session):
    card_title="Speak"
    session_attributes = {}
    should_end_session = True
    if 'Phrase' in intent['slots']:
        phrase=intent['slots']['Phrase']['value']
        speech_output = "I will speak "+phrase
        command={"cmd":"speak","text":phrase,"delay":5}
        sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))
        reprompt_text = "What else can I do for you?"
    else:
        speech_output = "I need a phrase to speak"
        reprompt_text = "Try asking me to say a phrase"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))      

#handle enrolling a face
def index_intent(intent, session):
    card_title="Index a Face"
    session_attributes = {}
    should_end_session = False
    if 'Name' in intent['slots']:
        name=intent['slots']['Name']['value']
        speech_output = name+" I'll take your photo, hold still"
        reprompt_text = None
        command={"cmd":"index_face","name":name}
        sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))            
    else:
        speech_output = "I'll need a name for the person whose photo I'm taking"
        reprompt_text = "Try asking me to enroll a name"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))      

#handle recognizing a face
def recognize_intent(intent, session):
    card_title="Recognize a Face"
    session_attributes = {}
    should_end_session = True
    speech_output = "Just a minute"
    command={"cmd":"search_faces"}
    sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))    
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

#handle finding a face in the image
def find_face_intent(intent, session):
    card_title="Locate a Face"
    session_attributes = {}
    should_end_session = True
    speech_output = "OK, I'll try to locate a face"
    command={"cmd":"detect_faces"}
    sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))    
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

#take a photo
def photo_intent(intent, session):
    card_title="Take a Photo"
    session_attributes = {}
    should_end_session = True
    speech_output = "OK, I'll take a photo"
    command={"cmd":"snap"}
    sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))    
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

#clear the screen
def clear_intent(intent, session):
    card_title="Clear Screen"
    session_attributes = {}
    should_end_session = True
    speech_output = "OK"
    command={"cmd":"clear_screen"}
    sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))    
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))  

#show the enrolled faces
def show_faces_intent(intent, session):
    card_title="Show Faces"
    session_attributes = {}
    should_end_session = True
    speech_output = "OK"
    command={"cmd":"show_faces"}
    sqs.send_message(QueueUrl=queue,MessageBody=json.dumps(command))    
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

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
    if intent_name == "SpeakIntent":
        return speak_intent(intent, session)
    elif intent_name == "IndexIntent":
        return index_intent(intent, session)
    elif intent_name == "RecognizeIntent":
        return recognize_intent(intent, session)
    elif intent_name == "FindFaceIntent":
        return find_face_intent(intent, session)
    elif intent_name == "PhotoIntent":
        return photo_intent(intent, session)
    elif intent_name == "ClearIntent":
        return clear_intent(intent, session)
    elif intent_name == "ShowFacesIntent":
        return show_faces_intent(intent, session)
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
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
