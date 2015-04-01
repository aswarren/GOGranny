## \package GOError
# Custom error logging.  Can be turned off - in which case RuntimeExceptions are thrown
# rather than errors just being printed out.
# \author mullerb@musc.edu

import sys, time, os, datetime, traceback

## Singleton error logging class.  
class GOError:
    __state = {}
    NONE = 0
    FATAL = 1
    WARNING = 2
    DEBUG = 3

    ## Constructor (makes a new instance, but state is shared across all instances)
    # @param loglevel (default of 0):
    # \li 0 - turns off logging - raise RuntimeErrors/Warnings for fatal/warning messages (useful for code build on this library)
    # \li 1 - print only fatal messages
    # \li 2 - print warnings and fatal messages
    # \li 3 - debug mode - prints everything
    def __init__(self, loglevel=0):
        self.__dict__ = GOError.__state
        if self.__dict__ == {}:
            self.loglevel = int(loglevel)
            self.stdout_logging = (os.name == 'posix')
            # if a PercentMessage class is currently in process, then withhold
            # debug messages
            self.percentMessage = False


    def timenow(self):
        return time.strftime("[%H:%M:%S] ")


    ## Log a debug message
    # @param msg Debugging message to log
    def debug(self, msg, singleline=False):
        if self.loglevel==3 and not self.percentMessage:
            if self.stdout_logging and singleline:
                print "\r" + self.timenow() + "\033[32;1mdebug:\033[0m " + msg,
                sys.stdout.flush()
            elif self.stdout_logging:
                print self.timenow() + "\033[32;1mdebug:\033[0m " + msg
            else:
                print self.timenow() + "DEBUG: "+msg


    ## Log a warning message (bad, but not bad enough to stop the program)
    # @param error Error message to log
    # @param exception If true this method will print the last stacktrace as well
    def handleWarning(self, error, exception=False):
        if self.loglevel > 1:
            # We need a newline if we're printing percent messages
            if self.percentMessage:
                print
            if self.stdout_logging:
                print self.timenow() + "\033[33;1mwarning:\033[0m " + error
            else:
                print self.timenow() + "WARNING: "+error
            if exception:
                self.printExceptionStack()                
        elif self.loglevel == 0:
            raise RuntimeWarning, error


    ## Log a message concerning a fatal error that will cause this program to terminate.  The function then
    # terminates the program.
    # @param fatal The message containing a description of the fatal conditions.
    # @param exception If true this method will print the last stacktrace as well    
    def handleFatal(self, fatal, exception=False):
        if self.loglevel > 0:
            if self.stdout_logging:
                print self.timenow() + "\033[31;1mfatal:\033[0m " + fatal
            else:
                print self.timenow() + "FATAL: "+fatal
            if exception:
                self.printExceptionStack()
            sys.exit(1)
        else:
            raise RuntimeError, fatal


    ## Print the most recent exception's stacktrace
    def printExceptionStack(self):
        traceback.print_exc()
                        

                                                                                
## Class to handle percent logging to terminal.  Note that once you call update for the first time,
# GOError debug messages will be suppressed until you call finished.
# p = GOPercentMessage(totalsize)
# p.update() # run many times
# p.finished()
class GOPercentMessage:
    def __init__(self, size):
        self.size = float(size)
        self.start = None
        self.error = GOError()
        self.current = 0
        self.index = 0


    def update(self):
        if self.start is None:
            self.start = time.time()
        self.current += 1
        self.index += 1

        if self.size > 100000 and self.index != 10000:
            return
        if self.index == 10000:
            self.index = 0

        ratio = float(self.current) / self.size
        age = float(self.age())
        finish = self.prettyTime((age / ratio) - age) # age/ratio = total time
        line = "%s percent done at point %i (estimated finish in %s)" % (str(ratio * 100), self.current, finish)
        while len(line) < 70:
            line += "  "

        # *we* should be able to print debugs, no one else should
        self.error.percentMessage = False                            
        self.error.debug(line,True)
        self.error.percentMessage = True


    def age(self):
        return time.time() - self.start


    def prettyTime(self, seconds):
        seconds = int(seconds)
        return str(datetime.timedelta(seconds=seconds))


    def finished(self):
        self.error.percentMessage = False                
        self.error.debug("done")
        self.error.debug("finished in %s" % self.prettyTime(self.age()))
