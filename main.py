from string import ascii_uppercase
from random import choice
from copy import copy


width = 24
height = 12

directions = [
    (1,-1),
    (1,0),
    (1,1),
    (0,1),
    (-1,1),
    (-1,0),
    (-1,-1),
    (0,-1),
]

PLACEHOLDER = '.'


# given a string s and letter ch, find where ch is located in s, and return a list of indices of these locations
def find_all_idx(s, ch):
    return [i for i, c in enumerate(s) if c == ch]


def getWordPositionsFromUsedLocation(word, grid, location, ndx):
    wordPositions = []
    x, y = location
    length = len(word)
    if ndx < 0 or ndx >= length:
        raise IndexError("ndx should be integer from 0 to len(word) - 1, cannot be negative. params: word=" + word + " ndx=" + ndx)
    if grid[y][x] != word[ndx]:
        raise RuntimeError("the indexed letter for this word should match the letter at the relevant position in the grid. Params: word="  + word + " ndx=" + ndx + " location=" + location  + " grid=" + grid)
    for d in directions:
        xD, yD = d
        # change x, y to the start of the word
        x = x - ndx * xD
        y = y - ndx * yD
        letterLocations = [ (x + xD * i, y + yD * i) for i in range(length) ]
        locationsInBounds = [ l[0] >= 0 and l[1] >= 0 and l[0] < width and l[1] < height for l in letterLocations ]
        if False in locationsInBounds:
            # print(f"Skipped, out of puzzle bounds. Direction {d}, location {location}, word {word}")
            continue
        gridLocations = [ grid[l[1]][l[0]] for l in letterLocations ]        
        letterMatches = [ word[i] == l or PLACEHOLDER == l for i, l in enumerate(gridLocations) ]
        if False in letterMatches:
            # print(f"Skipped, bad overlap with another word. Direction {d}, location {location}, word {word}")
            continue
        wordPositions.append( (x, y, (xD, yD)) )
    return wordPositions


def getWordPositionsFromEmptyLocation(word, grid, location):
    wordPositions = []
    x, y = location
    length = len(word)
    
    for d in directions:
        xD, yD = d
        letterLocations = [ (x + xD * i, y + yD * i) for i in range(length) ]
        locationsInBounds = [ l[0] >= 0 and l[1] >= 0 and l[0] < width and l[1] < height for l in letterLocations ]
        if False in locationsInBounds:
            # print(f"Skipped, out of puzzle bounds. Direction {d}, location {location}, word {word}")
            continue
        gridLocations = [ grid[l[1]][l[0]] for l in letterLocations ]        
        letterMatches = [ word[i] == l or PLACEHOLDER == l for i, l in enumerate(gridLocations) ]
        if False in letterMatches:
            # print(f"Skipped, bad overlap with another word. Direction {d}, location {location}, word {word}")
            continue
        wordPositions.append( (x, y, (xD, yD)) )
    return wordPositions


# find all the positions that this word can go in
# the position data contains an x and y coordinate, and a direction for the word 
def findWordPositions(word, puzzle):
    positions = []
    for y, line in enumerate(puzzle):
        for x, letter in enumerate(line):
            if letter == PLACEHOLDER:
                for p in getWordPositionsFromEmptyLocation(word, puzzle, (x, y)):
                    positions.append(p)
            else:
                for n in find_all_idx(word, letter):
                    for p in getWordPositionsFromUsedLocation(word, puzzle, (x, y), n):
                        positions.append(p)                
    return positions


# place a word within the puzzle, using starting position data
# the position data contains an x and y coordinate, and a direction for the word 
def placeWord(word, position, puzzle):
    tmp_puzzle = copy(puzzle)
    x, y, direction = position
    xD, yD = direction
    for l in word:
        tmp_puzzle[y][x] = l
        y += yD
        x += xD
    return tmp_puzzle


# make the puzzle using the list of words
def makePuzzle(words):
    puzzle = []
    # start with a puzzle filled with placeholder symbols. These will be changed over time.
    for _ in range(height):
        line = [PLACEHOLDER for _ in range(width)]
        puzzle.append(line)
    
    # sort the words from biggest to smallest
    words = sorted(words, key=lambda x: len(x))
    # check the words are not too long to fit into the puzzle
    if len(words[-1]) > height and len(words[-1]) > width:
        raise RuntimeError("word {} too long to fit in puzzle of dimensions {}x{}".format(words[-1], width, height))
    
    # keep track of which words have not been placed in the puzzle yet
    available_words = [x for x in words]
    # keep a stack (a type of list) of copies of the puzzle, one copy for each time we place a word
    puzzle_stack = []
    # leave the original puzzle unchanged, and only work with copies of the puzzle
    puzzle_state = copy(puzzle)
    # get the first word to place
    current_word = available_words[-1]
    
    while len(available_words):
        # get all the positions the word can go in. A position has an x, y location, and a direction for the word
        positions = findWordPositions(current_word, puzzle_state)
        # check if the word can actually be placed anywhere. If not, then something is wrong
        if not len(positions):
            # failsafe - if it is not possible to place this list of words into a workable puzzle
            if not len(puzzle_stack):
                raise RuntimeError("Cannot create a puzzle using this word list with these puzzle dimensions?")
            # go backwards, and try different placings for the words
            available_words.append(current_word)
            current_word, puzzle_state = puzzle_stack.pop()
            # skip back to start of loop
            continue
        # get a random position
        p = choice(positions)
        # place the word, then put a puzzle copy into the stack with the latest word placed
        puzzle_state = placeWord(current_word, p, puzzle_state)
        puzzle_stack.append( (current_word, puzzle_state) )
        
        # drop the latest used word.
        available_words.pop()
        if not len(available_words):
            continue
        # get the next word
        current_word = available_words[-1]

    # replace the placeholders in the puzzle with random letters
    for y in range(height):
        for x in range(width):
            if puzzle[y][x] == '.':
                puzzle[y][x] = choice(ascii_uppercase)
    return puzzle


# retrieve the list of words from the word list file
def getWords(fp):
    words = [x.upper().strip() for x in fp.readlines()]
    return words


# print the list of words to the Screen or Output
def showWords(words):
    for w in words:
        print(w)


# print the puzzle to the Screen or Output
def showPuzzle(puzzle):
    for row in puzzle:
        line = "".join(row)
        print(line)


with open("wordList.txt") as fp:
    words = getWords(fp)
if not len(words):
  print("There are no words to puzzle!")
else:
  puzzle = makePuzzle(words)
  print("")
  showWords(words)
  print("\n--------\n")
  showPuzzle(puzzle)
