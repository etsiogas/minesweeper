#!/usr/bin/env python3

from __future__ import division
from random import randint
import pygame, time, os, sys

if len(sys.argv) != 3:
	print("""Usage: python3 minesweeper.py [cells] [mines] where
	cells: number of cells that determines the size of the game's window (cells x cells)
	mines: number of mines""")
	sys.exit()
	
# Input arguments
CELLS = int(sys.argv[1])
MINES = int(sys.argv[2])

if MINES > CELLS * CELLS // 2:
	print("Too many mines!")
	sys.exit()
	
colors = {
	0: (192, 192, 192),
	'silver': (192, 192, 192),
	1: (0, 0, 255),
	'blue': (0, 0, 255),
	2: (0, 128, 0),
	'green': (0, 128, 0),
	3: (255, 0, 0),
	'red': (255, 0, 0),
	4: (128, 0, 128),
	'purple': (128, 0, 128),
	5: (255, 140, 0),
	'orange': (255, 140, 0),
	6: (0, 139, 139),
	'cyan': (0, 139, 139),
	7: (255, 255, 0),
	'yellow': (255, 255, 0),
	8: (0, 0, 0),
	'black': (0, 0, 0),
	9: (128, 128, 128),
	'grey': (128, 128, 128),
}

# Constants (pixel units)
MARGIN = 3
TOP_MARGIN = 60
WIDTH = 20	# of a single cell
HEIGHT = 20	# of a single cell

# Size of game's window
WINDOW_SIZE = [CELLS * (WIDTH + MARGIN) + MARGIN,
	CELLS * (HEIGHT + MARGIN) + MARGIN + TOP_MARGIN]
	
class Cell:
	def __init__(self):
		self.mines = 0
		self.flagged = False
		self.revealed = False
		self.color = colors[0]
		
def reset():
	global grid, flags, start, done, win, fail, info, timer, icon_size, lives
	
	grid = []
	flags = start = 0
	done = win = fail = False
	info = "Mines: " + str(MINES)
	timer = "Time: 00:00"
	icon_size = (WIDTH - 2, HEIGHT - 2)
	lives = 0
	
	for row in range(CELLS):
		grid.append([])
		
		for col in range(CELLS):
			grid[row].append( Cell() )
			
def insertMines(first_row, first_col):
	mines = 0
	
	while(mines < MINES):
		row = randint(0, CELLS - 1)
		col = randint(0, CELLS - 1)
		
		if( ( abs(row - first_row) <= 1 and abs(col - first_col) <= 1 ) or
			grid[row][col].mines == -1 ):
				continue
				
		grid[row][col].mines = -1
		mines += 1
		
		for x, y in [(row + i, col + j) for i in (-1, 0, 1) for j in (-1, 0, 1)]:
			if 0 <= x < CELLS and 0 <= y < CELLS and grid[x][y].mines != -1:
				grid[x][y].mines += 1
				grid[x][y].color = colors[grid[x][y].mines]
				
def revealEmpty(row, col):
	grid[row][col].revealed = True
	
	for x, y in [(row + i, col + j) for i in (-1, 0, 1) for j in (-1, 0, 1)]:
		if 0 <= x < CELLS and 0 <= y < CELLS and \
			grid[x][y].mines != -1 and not grid[x][y].revealed:
				if grid[x][y].mines == 0:
					revealEmpty(x, y)
				elif not grid[x][y].flagged:
					grid[x][y].revealed = True
					
# Initialize pygame
pygame.init()
font = pygame.font.SysFont('arial', 25)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minesweeper")
clock = pygame.time.Clock()
reset()

# Load icons
mine = pygame.image.load('mine.png')
flag = pygame.image.load('flag.png')
cancel = pygame.image.load('cancel.png')

mine = pygame.transform.scale(mine, icon_size)
flag = pygame.transform.scale(flag, icon_size)
cancel = pygame.transform.scale(cancel, icon_size)

# Game loop
while not done:
	screen.fill(colors['black'])
	
	screen.blit( font.render(timer, True, colors['silver']),
		(WINDOW_SIZE[0] // 2 - font.size(timer)[0] // 2, TOP_MARGIN // 2) )
		
	screen.blit( font.render(info, True, colors['silver']),
		(WINDOW_SIZE[0] // 2 - font.size(info)[0] // 2, 0) )
		
	# Check mouse/keyboard event
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_SPACE:
				reset()
			elif event.key == pygame.K_ESCAPE:
				done = True
		elif win or fail:
			continue
		elif event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			
			# Mouse clicked in free space
			if pos[1] <= TOP_MARGIN:
				continue
				
			col = pos[0] // (WIDTH + MARGIN)
			row = (pos[1] - TOP_MARGIN) // (HEIGHT + MARGIN)
			
			# left click
			if event.button == 1 and not grid[row][col].flagged:
				if not start:
					start = time.time()
					insertMines(row, col)
					
				if grid[row][col].mines == -1:
					if(lives > 0):
						grid[row][col].flagged = True
						flags += 1
						lives -= 1
					else:
						fail = True
						break
						
				if not grid[row][col].revealed:
					if grid[row][col].mines == 0:
						revealEmpty(row, col)
					else:
						grid[row][col].revealed = True
						
			# right click
			elif event.button == 3 and not grid[row][col].revealed:
				grid[row][col].flagged = not grid[row][col].flagged
				flags = (flags - 1, flags + 1)[grid[row][col].flagged]
				
	# Draw everything
	unrevealed = 0
	
	for row in range(CELLS):
		for col in range(CELLS):
			pygame.draw.rect(screen, colors['grey'],
				[(MARGIN + WIDTH) * col + MARGIN,
					(MARGIN + HEIGHT) * row + MARGIN + TOP_MARGIN, WIDTH, HEIGHT])
			if not grid[row][col].revealed:
				unrevealed += 1
			if grid[row][col].flagged:
				x = col * (MARGIN + WIDTH) + MARGIN + \
					( WIDTH - flag.get_width() ) // 2
				y = row * (MARGIN + HEIGHT) + MARGIN + TOP_MARGIN + \
					( WIDTH - flag.get_width() ) // 2
				screen.blit( flag, (x, y) )
				
				if fail and grid[row][col].mines != -1:
					x = col * (MARGIN + WIDTH) + MARGIN + \
						( WIDTH - cancel.get_width() ) // 2
					y = row * (MARGIN + HEIGHT) + MARGIN + TOP_MARGIN + \
						( WIDTH - cancel.get_width() ) // 2
					screen.blit( cancel, (x, y) )
					
			elif fail and grid[row][col].mines == -1:
				x = col * (MARGIN + WIDTH) + MARGIN + \
					( WIDTH - mine.get_width() ) // 2
				y = row * (MARGIN + HEIGHT) + MARGIN + TOP_MARGIN + \
					( WIDTH - mine.get_width() ) // 2
				screen.blit( mine, (x, y) )
				
			elif grid[row][col].revealed:
				pygame.draw.rect(screen, colors['silver'],
					[(MARGIN + WIDTH) * col + MARGIN,
						(MARGIN + HEIGHT) * row + MARGIN + TOP_MARGIN, WIDTH, HEIGHT])
						
				if grid[row][col].mines > 0:
					x = (MARGIN + WIDTH) * col + MARGIN + 3
					y = (MARGIN + HEIGHT) * row + MARGIN + TOP_MARGIN - 4
					screen.blit( font.render( str(grid[row][col].mines), True,
						grid[row][col].color ), (x, y) )
						
	info = "Mines: " + str(MINES - flags)
	
	now = int(time.time() - start)
	minutes = "%02d" % (now // 60)
	seconds = "%02d" % (now % 60)
	
	if(MINES == unrevealed):
		win = True
		info = "Congratulations!"
	elif fail:
		info = "Oops! Press space to try again!"
	elif start:
		timer = "Time: " + str(minutes) + ':' + str(seconds)
		
  # Limit to 60 frames per second
	clock.tick(60)
	
  # Update the screen with current drawings
	pygame.display.flip()
	
# Without this line the program may 'hang' on exit
pygame.quit()
