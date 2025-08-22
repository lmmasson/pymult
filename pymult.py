# Example file showing a circle moving on screen
import pygame
import random
import time
from enum import IntEnum

# configuration
TIMEOUT=4
TIME_DISPLAY_ANSWER_GOOD=0.5
TIME_DISPLAY_ANSWER_BAD=2
MAX_ROUND=20

# A*B
A_MIN=2
A_MAX=10

B_MIN=0
B_MAX=10

# constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GRAY = (150, 150, 150)
DGRAY = (100, 100, 100)
DBROWN= (150, 100, 50)
BROWN = (200, 150, 100)
MIN=1
MAX=99
NB_COL=10


FONTSIZE_QUESTION=150
FONTSIZE_SCORE=100
FONTSIZE_TIME=100

KMARGIN=2

# global variables
KEYBOARD_X=0
KEYBOARD_Y=0

KRADIUS=0


class R(IntEnum):
    NONE = 0
    OK = 1
    BAD = 2

# pygame setup
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
XMARGIN= screen.get_width() / 100
YMARGIN= screen.get_height() / 100
KRADIUS=int(screen.get_height()/100)
clock = pygame.time.Clock()
running = True
results = []
dt = 0

score_good=0
score_bad=0

but_width=0
but_height=0

t0=time.monotonic()
timeout=0

def display_result(question:dict[int, int, int], result) -> None:
	# compute size of origninal text
	st=str(question['a'])+"x"+str(question['b'])+"=?"
	font = pygame.font.SysFont(None, FONTSIZE_QUESTION)
	img = font.render(st, True, BLACK)
	w=img.get_width()

	# Real text to display
	st=str(question['a'])+"x"+str(question['b'])+"="+str(question['r'])
	font = pygame.font.SysFont(None, FONTSIZE_QUESTION)
	img = font.render(st, True, BLACK)
	if result == R.OK:
		screen.fill("green")
		waittime=TIME_DISPLAY_ANSWER_GOOD
	else:
		screen.fill("red")
		waittime=TIME_DISPLAY_ANSWER_BAD
	# Center the text on the screen
	img_x = (screen.get_width() - w) / 2 
	screen.blit(img, (img_x, YMARGIN))
	pygame.display.flip()
	time.sleep(waittime)
	# flush events
	pygame.event.clear()

def draw_screen(t:int, question, score_good:int, score_bad:int, left:int):
	global KEYBOARD_Y

	#update KEYBOARD_Y to manage screen rotation
	KEYBOARD_Y=int(screen.get_height()*0.25)

	st=str(question['a'])+"x"+str(question['b'])+"=?"

	screen.fill("black")
	#Display Time
	font = pygame.font.SysFont(None, FONTSIZE_TIME)
	img = font.render(str(t), True, CYAN)
	screen.blit(img, (screen.get_width()-img.get_width()-XMARGIN, YMARGIN))
	h=img.get_height()

	#Display number of questions left
	font = pygame.font.SysFont(None, FONTSIZE_TIME)
	img = font.render(str(min(left, MAX_ROUND-score_good)), True, BLUE)
	screen.blit(img, (screen.get_width()-img.get_width()-XMARGIN, YMARGIN+h+YMARGIN))

	# Display question
	font = pygame.font.SysFont(None, FONTSIZE_QUESTION)
	img = font.render(st, True, WHITE)
	w=img.get_width()
	# Center the text on the screen
	img_x = (screen.get_width() - w) / 2 
	screen.blit(img, (img_x, YMARGIN))
	
	# Display score
	font = pygame.font.SysFont(None, FONTSIZE_SCORE)

	# score bad
	s=str(score_bad)
	img = font.render(s, True, RED)
	w=img.get_width()
	h=img.get_height()
	x= screen.get_width() - w - XMARGIN
	y= KEYBOARD_Y - h - YMARGIN
	screen.blit(img, (x, y))

	# "/" character
	s= "/"
	img = font.render(s, True, WHITE)
	w=img.get_width()
	x-= w + XMARGIN
	screen.blit(img, (x, y))

	# score good
	s = str(score_good)
	img = font.render(s, True, GREEN)
	w=img.get_width()
	x-= w + XMARGIN
	screen.blit(img, (x, y))


def draw_keyboard():
	global but_width
	global but_height
	global KEYBOARD_X
	global KEYBOARD_Y

	#Draw keyboard
	for i in range(0, NB_COL):
		nb_lines=int((MAX-MIN+1)/NB_COL)+1
		but_width=int(screen.get_width()/NB_COL)
		but_height=int((screen.get_height()-KEYBOARD_Y)/nb_lines)
		for j in range(0, nb_lines):
			rect=pygame.Rect(KEYBOARD_X+i*but_width+KMARGIN, KEYBOARD_Y+j*but_height+KMARGIN, but_width-KMARGIN, but_height-KMARGIN)
			if i % 2:
				if j % 2:
					pygame.draw.rect(screen, DGRAY, rect, 0, KRADIUS)
				else:
					pygame.draw.rect(screen, GRAY, rect, 0, KRADIUS)
			else:
				if j % 2:
					pygame.draw.rect(screen, DBROWN, rect, 0, KRADIUS)
				else:
					pygame.draw.rect(screen, BROWN, rect, 0, KRADIUS)
			font = pygame.font.SysFont(None, min(but_width, but_height))
			img = font.render(str(i+j*NB_COL), True, WHITE)
			w=img.get_width()
			h=img.get_height()
			# Center the text in the button
			img_x = KEYBOARD_X + i * but_width + KMARGIN + (but_width - w) / 2 
			img_y = KEYBOARD_Y + j * but_height + KMARGIN + (but_height - h) / 2
			screen.blit(img, (img_x, img_y))
			#screen.blit(img, (KEYBOARD_X+i*but_width+(but_width/10), KEYBOARD_Y+j*but_height+(but_height/10)))

def manage_events():
	global running

	res=-1
	# Poll for events
	for event in pygame.event.get():
		# Quit or press escape to exit
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
		# Touchscreen or mouse down event
		elif event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:	
			if event.type == pygame.FINGERDOWN:
				x = int(event.x * screen.get_width())
				y = int(event.y * screen.get_height())
			else:
				x, y = event.pos
			if y>KEYBOARD_Y and x>KEYBOARD_X:
				res_x=int((x-KEYBOARD_X)/but_width)
				res_y=int((y-KEYBOARD_Y)/but_height)
				res=res_x+res_y*NB_COL
		#elif event.type == pygame.FINGERUP:
		#	pass
	return res

# init first question:
for a in range(A_MIN, A_MAX):
	for b in range(B_MIN, B_MAX):
		results.append({ 'a': a, 'b': b, 'r': a * b })

#for i in range(0, MAX_ROUND):
	# Randomly select a question
#	question = random.choice(_results)
#	results.append(question)
#	_results.remove(question)

# shuffle questions
random.shuffle(results)
results=results[:MAX_ROUND]

question=random.choice(results)

# main loop
while running:
	# Compute time t
	t=TIMEOUT-int(time.monotonic()-t0)

	# Display question
	draw_screen(t, question, score_good, score_bad, len(results))
	# Draw keyboard
	draw_keyboard()

	if t<=0:
		# timeout
		result=R.BAD
	else:
		res = manage_events()
		if res == -1:
			result = R.NONE
		elif res == question["r"]:
			result = R.OK
		else:
			result = R.BAD

	if result == R.NONE:
		# No answer yet, continue
		pygame.display.flip()
	else:
		# answer received
		if result == R.OK:
			# good answer, screen flash green
			score_good+=1
			# pop the question from the list
			results.remove(question)
		else:
			score_bad+=1
		
		display_result(question, result)

		# initiliaze next question
		if len(results)==0:
			# no more questions, end game
			running = False
		elif score_good >= MAX_ROUND:
			# reach max round, end game
			running = False
		else:
			question=random.choice(results)
			t=TIMEOUT
			t0=time.monotonic()
		
	dt = clock.tick(60) / 1000


# End of game. Display final score
running=True
while running:
	screen.fill("black")

	# Display "Fin"
	st="Fin"
	font = pygame.font.SysFont(None, 90)
	img = font.render(st, True, WHITE)
	screen.blit(img, (0,0))

	# Display Note/20
	if score_good==0:
		note=0
	else:
		note=(score_good-score_bad)/score_good*20
		note=round(note, 2)
	s=str(note)+' / 20'	
	img = font.render(s, True, WHITE)
	screen.blit(img, (0, 100))

	# Print score good and bad
	font = pygame.font.SysFont(None, 90)
	s = str(score_good)
	img = font.render(s, True, GREEN)
	screen.blit(img, (20, 200))
	s= "/"
	img = font.render(s, True, WHITE)
	screen.blit(img, (screen.get_width()/2, 200))
	s=str(score_bad)
	img = font.render(s, True, RED)
	screen.blit(img, (screen.get_width()-200, 200))


	
	pygame.display.flip()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

pygame.quit()