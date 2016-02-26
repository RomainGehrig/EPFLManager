import sys
import logging
import readline

logger = logging.getLogger(__name__)

class NoChoiceException(Exception): pass
class UserQuitException(Exception): pass

class IOManager(object):
    def print(self, *args, **kwargs):
        raise NotImplemented('Must implement a print function')
    def info(self, txt):
        self.print(txt)
    def warn(self, txt):
        self.print(txt)
    def error(self, txt):
        self.print(txt)

class ConsoleManager(IOManager):
    """ Class to handle the IO of the console user """
    def __init__(self, printer=None, reader=None, error=None):
        # TODO test if they can be used (instance of TextIOWrapper?)
        self.printer = sys.stdout if printer is None else printer
        self.reader =  sys.stdin  if reader  is None else reader
        self.error =   sys.stderr if error   is None else error

    def input(self, text):
        return input(text)
        # self.reader.flush()
        # self.print(text, end="", flush=True)
        # return self.reader.readline()[:-1]

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
