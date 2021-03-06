from tools import constants as con
from tools import variables as var
from tools import functions as fn
from tools import process as pro
from tools import logger as log
from tools import help as helper
from tools import git as _git
import shutil
import os

# This holds all the commands
# Must have (inp, params=[]) in the def all the time, even if not used
# Or (*stuff) if parameters don't matter

# To add a new command, simply make a new def block
# The name of the definition is the command

# The following commands don't require any parameter

def exit(*args):
    var.ALLOW_RUN = False

def restart(*args):
    var.RETRY = True

def clean(*args):
    for x, y in con.LOGGERS.items():
        logfile = getattr(var, y + "_FILE")
        log_ext = getattr(var, y + "_EXT")
        if x == "temp":
            notdone = []
            file = "{0}\\{1}.{2}".format(os.getcwd(), logfile, log_ext)
            f = open(file, "r")
            for line in f.readlines():
                line = line.replace("\n", "")
                if not line:
                    continue
                try:
                    shutil.rmtree(line)
                except OSError:
                    notdone.append(line)
            if notdone:
                ft = open(file, "w")
                ft.write("\n".join(notdone))
                ft.write("\n")
                ft.close()
                continue # prevent temp file from being deleted if it fails
            f.close()
        file = logfile + "." + log_ext
        if fn.IsFile.cur(file):
            os.remove(os.getcwd() + "\\" + file)
        for s in con.LANGUAGES.values():
            filel = s + "_" + file
            if fn.IsFile.cur(filel):
                os.remove(os.getcwd() + "\\" + filel)
    if fn.IsFile.cur(var.TEMP_REG + ".reg"):
        os.remove(var.TEMP_REG + ".reg")
    if fn.IsFile.cur("cfg.py"):
        os.remove(os.getcwd() + "/cfg.py")
    shutil.rmtree(os.getcwd() + '/__pycache__')
    shutil.rmtree(os.getcwd() + '/tools/__pycache__')
    var.ALLOW_RUN = False

# The following commands may or may not require additional parameters

def help(inp, params=[]):
    if helper.get_help(" ".join(params)):
        to_help = helper.__unhandled__
        type = "help"
        if params[0] in var.USERS:
            try:
                to_help = getattr(helper.Users, params[0])
            except AttributeError:
                pass
        elif params[0] in var.COMMANDS:
            try:
                to_help = getattr(helper.Commands, params[0])
            except AttributeError:
                pass
        else:
            try:
                to_help = getattr(helper, params[0])
            except AttributeError:
                pass
        if params[0] in var.USERS and params[0] in var.COMMANDS:
            try:
                to_help = getattr(helper.Users, params[0])
            except AttributeError:
                try:
                    to_help = getattr(helper.Commands, params[0])
                except AttributeError:
                    pass
        helping = to_help()
        if helping == '__unhandled__':
            helping = "HELP_NOT_FOUND"
            type = "error"
            var.ERROR = True
        elif params[0] in (var.USERS + var.COMMANDS):
            helping = "\n".join(helping)
        log.help(helping, type=type, form=params[0])

def copy(inp, params=[]):
    if params and " ".join(params) == "config":
        shutil.copy(os.getcwd() + "/config.py", os.getcwd() + "/config.py.example")

def run(inp, params=[]):
    if params:
        if params[0] == "silent":
            pro.run(params=" ".join(params[1:]), silent=True)
        elif params[0] == "extract":
            pro.extract()
        else:
            pro.run(params=" ".join(params))
    else:
        pro.run()

def do(inp, params=[]):
    done = False
    if params:
        if inp[:22] == "do call python3; exec(" and inp[-2:] == ");":
            done = True
            exec(inp[22:-2])
        elif inp[:27] == "do call run function; eval(" and inp[-2:] == ");":
            done = True
            eval(inp[27:-2])
        elif inp[:9] == "do print(" and inp[-2:] == ");":
            done = True
            try:
                prnt = str(eval(inp[9:-2]))
            except NameError:
                prnt = "NOT_DEFINED"
            log.logger(prnt, type="debug", write=False, form=inp[9:-2])
        elif inp[:18] == "do ask print; get(" and inp[-2:] == ");":
            done = True
            var.PRINT = inp[18:-2]
        elif inp == "do call help; get help;":
            done = True
            log.help("",
                     "Developper commands:",
                     "\n",
                     "'do call python3; exec(\"command\");'",
                     "'do call run function; eval(\"module.function\");'",
                     "'do print(\"string\");'",
                     "'do ask print; get(\"string\");")
    if not done:
        fn.no_such_command("do")

def git(inp, params=[]):
    if not var.GIT_LOCATION:
        log.logger("GIT_NOT_INST")
        return
    args = [var.GIT_LOCATION]
    if params:
        args.extend(params)
        for second in _git.__dict__.keys():
            if params[0] == second:
                getattr(_git, second)(args)
                return
    _git.do(args)