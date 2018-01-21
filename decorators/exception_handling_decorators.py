#
#python
#

import sys
import traceback

#
#catch and print all unhandled exceptions from basic handling methods
#

def print_exceptions(general_function):
    def general_function_wrapper(bot, update):
        try:
            return general_function(bot, update)
        except Exception:
            print(sys.exc_info()[1])
            print(traceback.print_tb(sys.exc_info()[2]))
    return general_function_wrapper
