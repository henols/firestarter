
Import("env")
board = env.GetProjectOption("board")
env.Replace(PROGNAME="firestarter_%s" % board)
