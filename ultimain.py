import sys
#import main,main_win
print(sys.platform)
if sys.platform == "win32":
    import main_win
    main_win.main()
elif sys.platform == "linux" or sys.platform == "linux2":
    import main
    main.main()
