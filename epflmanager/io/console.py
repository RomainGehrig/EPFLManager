import sys
import logging
import readline

import epflmanager.components as components

logger = logging.getLogger(__name__)

class NoChoiceException(Exception): pass
class UserQuitException(Exception): pass

class ConsoleManager(components.Component):
    """ Class to handle the IO of the console user """
    def __init__(self, printer=None, reader=None, error=None):
        # TODO test if they can be used (instance of TextIOWrapper?)
        self.printer = sys.stdout if printer is None else printer
        self.reader =  sys.stdin  if reader  is None else reader
        self._error =  sys.stderr if error   is None else error
        super(ConsoleManager, self).__init__("Console")

    def error(self, txt):
        self.print(txt, file=self._error)

    def warn(self, txt):
        self.print(txt)

    def info(self, txt):
        self.print(txt)

    def input(self, text, default=None):
        """ Ask the user for an input
            Can specify a default if only whitespace is entered"""
        inp = input(text)
        if default is not None and not inp.strip():
            inp = default

        return inp
        # self.reader.flush()
        # self.print(text, end="", flush=True)
        # return self.reader.readline()[:-1]

    def confirm(self, question, default=True):
        """ Ask for a simple Y/N question """
        possible_answers = { 'y': True, 'yes': True,
                             'n': False, 'no': False }

        # Add the information about defaulting options at the end of the question
        default_info = ""
        if isinstance(default, bool):
            default_info = "Y/n" if default else "y/N"
        else:
            default_info = "y/n"
        question = question + (" [%s]: " % default_info)

        answer = None
        while not isinstance(answer,bool):
            answer = self.input(question, default=default)
            if isinstance(answer,str) and answer.lower() in possible_answers:
                answer = possible_answers[answer.lower()]

            if not isinstance(answer,bool):
                self.warn("Please answer Y/N.")

        return answer

    def password(self, text="Password: "):
        import getpass

        return getpass.getpass(prompt=text)

    def print(self, *args, **kwargs):
        kwargs.update(file=self.printer)
        return print(*args,**kwargs)

    def choose_from(self, choices, msg=None, display_func=str, can_quit=True, auto_choice_if_unique=True):
        """ Return what the user chose """
        if not choices:
            raise NoChoiceException("No choice to do")
        if auto_choice_if_unique and len(choices) == 1:
            return choices[0]

        choices_dict = { str(i): choice for i,choice in enumerate(choices,start=1) }
        while(True):
            if msg is not None:
                self.print(msg)
            for i,choice in sorted(choices_dict.items()):
                self.print("[{i}] {choice}".format(i=i, choice=display_func(choice)))
            if can_quit:
                self.print("[q] Quit")

            selection = self.input("Choice: ")
            if selection in choices_dict:
                return choices_dict[selection]
            elif can_quit and selection == "q":
                logger.debug("User chose to quit")
                raise UserQuitException('User quitted')
            else: # Invalid selection
                self.print("Invalid selection. Please select a valid one.")
