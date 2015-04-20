def welcome_back(arg):
	print("welcome_back function called with %s" % arg)

def see_you_later(arg):
	print("see_you_later function called with %s" % arg)

def weather_station():
	print("weather station function called")

def main(args):
    #Function chooser
    '''
    Run functions from command line.
    $python3 hue_control.py welcome 00:61:71:CC:52:C8 
    Runs the welcome_back function with that device_id
    Will weather still work if no second argument included? might have to make a separate call for that
    '''
    func_arg = {"-welcome":welcome_back,
            "-goodbye":see_you_later,
            "-weather":weather_station
            }
    try:
        func_arg[args[1]](args[2])
    except IndexError:
        try:
            func_arg[args[1]]()
        except IndexError:
            print('no valid args passed. running main program.')
            pass
    finally:
    	print("nothing working")


if __name__ == "__main__":
    import sys
    main(sys.argv)


