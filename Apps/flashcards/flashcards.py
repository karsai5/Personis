#!/usr/bin/python

import Tkinter, tkFileDialog
import io
import random
import Personis
import Personis_base
from Personis_exceptions import AuthRequestedError
import Crypto

class InputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

cardsets = {} 
um = None

def select_card_file():
    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename()
    return file_path

def parse_card_file(file_path):
    add_cardset(file_path)
    try:
	f = io.open(file_path, 'r', encoding = "utf-8")
	process_card_file(f, file_path)
    except UnicodeDecodeError:
	f = io.open(file_path, 'r', encoding = "utf-16")
	process_card_file(f, file_path)

def process_card_file(f, cardset):
    for line in f:
	card = line.strip().split('\t', 1)
	if len(card) != 2:
	    msg = "Incorrectly formatted flashcard file: " + file_path + "\n"
	    msg = msg + "Line: " + line
	    raise InputError(msg)
	add_card_to_set(card, cardset)

def add_cardset(name):
    cardsets[name] = [] 

def add_card_to_set(card, cardset):
    cardsets[cardset].append(card)

def study(cardset, reverse = False):
    while(True):
	print "Would you like to study in (a)ctive or (p)assive mode?"
	ans = raw_input().strip().lower()
	if ans == 'a':
	    active = True
	    break
	elif ans == 'p':
	    active = False
	    break
	else:
	    print "I don't understand. Please type 'a' for active mode or 'p' for passive mode."

    context = ["flashcards"]

    # Check whether the context exists, if not, make it and the components we need
    (component_list, context_list, view_list, sub_list) = um.ask(context=[""], showcontexts=True)
    if "flashcards" not in context_list:
	new_context = Personis_base.Context(Identifier="flashcards", Description="Context for the flashcards app")
	um.mkcontext("", new_context)
    if "cardset" not in component_list:
	comp = Personis_base.Component(Identifier="cardset", Description="The cardset studied by the user", component_type="activity", value_type="string")
	um.mkcomponent(context=context, componentobj=comp)
    if "mode" not in component_list:
	comp = Personis_base.Component(Identifier="mode", Description="The mode of study (active or passive)", component_type="activity", value_type="string")
	um.mkcomponent(context=context, componentobj=comp)
    if "ncards" not in component_list:
	comp = Personis_base.Component(Identifier="ncards", Description="The number of cards studied", component_type="activity", value_type="string")
	um.mkcomponent(context=context, componentobj=comp)
    if "score" not in component_list:
	comp = Personis_base.Component(Identifier="score", Description="The score (number of correct cards)", component_type="activity", value_type="string")
	um.mkcomponent(context=context, componentobj=comp)

    ev = Personis_base.Evidence(evidence_type="implicit", source="flashcards app", value=cardset, comment="cardset")
    um.tell(context=context, componentid="cardset", evidence=ev)
    if active:
	mode = "active"
    else:
	mode = "passive"
    ev = Personis_base.Evidence(evidence_type="implicit", source="flashcards app", value=mode, comment="study mode")
    um.tell(context=context, componentid="mode", evidence=ev)

    score = 0

    if reverse:
	a = 1
	b = 0
    else:
	a = 0
	b = 1

    ncards = len(cardsets[cardset])
    # Draw all cards in a random order
    # Do not actually shuffle list or we can't report which cards are correct and incorrect
    indices = list(range(ncards))
    random.shuffle(indices)

    for i in indices:
	card = cardsets[cardset][i]
	print card[a].encode('utf-8')
	ans = raw_input().strip().lower()

	if active:
	    if ans == card[1]:
		print "Correct!"
		score += 1
	    else:
		print "Incorrect. The correct answer is:"
		print card[b].encode('utf-8')
	else:
	    print card[b].encode('utf-8')
	    print "Did you get it right? (y/n)"
	    ans = raw_input().strip().lower()

	    if ans == 'y':
		score += 1
	    elif ans == 'n':
		pass
	    else:
		print "Couldn't understand your answer, ignoring..."
		ncards -= 1
    
    ev = Personis_base.Evidence(evidence_type="implicit", source="flashcards app", value=ncards, comment="number of cards")
    um.tell(context=context, componentid="ncards", evidence=ev)
    ev = Personis_base.Evidence(evidence_type="implicit", source="flashcards app", value=score, comment="number of cards correct")
    um.tell(context=context, componentid="score", evidence=ev)

    print "Your score is %d/%d" % (score, ncards)

    ncards_comp = um.ask(context=context, view=["ncards"], resolver=dict(evidence_filter="all"))
    ncards_list = ncards_comp[0].evidencelist
    total_ncards = 0
    for item in ncards_list:
	total_ncards += item.value
    score_comp = um.ask(context=context, view=["score"], resolver=dict(evidence_filter="all"))
    score_list = score_comp[0].evidencelist
    total_score = 0
    for item in score_list:
	total_score += item.value

    print "Your total score to date is %d/%d" % (total_score, total_ncards)

def get_login_details():
    pass

def access_user_model(server=None, port=None, model=None):
    global um
    if server == None:
	server = raw_input("Please enter the Personis server hostname (default localhost): ")
	if server == "":
	    server = "localhost"
    if port == None:
	port = raw_input("Please enter the port number for the Personis serer (default 2005): ")
	if port == "" or int(port) == 0:
	    port = "2005"
    server = server + ":" + port
    if model == None:
	model = raw_input("Please enter the model name: ");

    try:
	um = Personis.Access(model=model, modelserver=server, app="flashcards", description="A simple flashcard study app")
    except AuthRequestedError as e:
	print e
	print "Please authorise the app and then run it again."
	exit()
    except:
	print "Unable to access user model %s on server %s" % (model, server)
	raise	

if __name__ == "__main__":
    # TODO: add command line arguments: flashcard set, server, port, model name

    access_user_model()

    path = raw_input("Please select a flashcard set to study: ")

#    path = select_card_file()
    try:
	parse_card_file(path)
    except InputError as err:
	print err.strerror
	raise

    study(path)
