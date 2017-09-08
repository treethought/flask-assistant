from flask import current_app
from flask_assistant.responses.standard import _ApiAiResponse
from flask_assistant.responses.google import _GoogleData


class _IntegratedResponse(_ApiAiResponse):
    """docstring for _IntegratedResponse"""

    def __init__(self, speech, display_text=None, followup_event=None):
        super(_IntegratedResponse, self).__init__(speech=speech,
                                                  display_text=display_text, followup_event=followup_event)

    def google_required(self):
        if not self.google:
            raise NotImplementedError(
                'suggest response type requires Actions Integration')
        return True

    def suggest(self, *titles):
        for title in titles:
            self.google_data.suggestion(title)

        return self

    def link(self, destination, url):
        self.google_data.link_out(destination, url)
        return self


class tell(_IntegratedResponse):
    def __init__(self, speech, display_text=None, followup_event=None):
        super(tell, self).__init__(
            speech, display_text=display_text, followup_event=followup_event)

        if self.google:
            print('Integrating google into tell')
            self.google_data.simple_response(
                self.speech, self.display_text, False)
            self._response['data']['google'] = self.google_data._load_data()


class ask(_IntegratedResponse):
    def __init__(self, speech, display_text=None, followup_event=None):
        """Returns a response to the user and keeps the current session alive. Expects a response from the user.

        Arguments:
            speech {str} --  Text to be pronounced to the user / shown on the screen
        """
        super(ask, self).__init__(
            speech, display_text=None, followup_event=followup_event)

        if self.google:
            self.google_data.simple_response(
                self.speech, self.display_text, True)
            self._response['data']['google'] = self.google_data._load_data()

    def reprompt(self, prompt):  # TODO
        """Prompt used to ask user when there is no input from user."""
        # self._response['no_input_prompts'] = [{'text_to_speech': prompt}]
        # self.google._data

        return self


class event(_IntegratedResponse):
    """Triggers an event to invoke it's respective intent.

    When an event is triggered, speech, displayText and services' data will be ignored.
    """

    def __init__(self, event_name, **kwargs):
        super(event, self).__init__(speech=None)

        self._response['followupEvent'] = {

            "name": event_name,
            "data": kwargs
        }
        