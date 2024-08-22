import time
import chess
import chess.pgn
import chess.svg
from PIL import Image
import cairosvg
import requests
import genanki
import base64


def determine_turn(fen):
    # Split the FEN string into its components
    fields = fen.split()

    # The second field in the FEN string indicates whose turn it is
    turn = fields[1]

    if turn == 'w':
        return "White"
    elif turn == 'b':
        return "Black"
    else:
        return "Invalid FEN string"


def format_solution(solution_moves, fen):
    # FEN string for the starting position

    # Create a board from the FEN string
    board = chess.Board(fen)

    # Convert moves to SAN and apply them
    san_moves = []
    for move in solution_moves:
        # Convert to a move object
        move_obj = chess.Move.from_uci(move)

        # Convert to SAN
        san_move = board.san(move_obj)
        san_moves.append(san_move)

        # Apply the move on the board
        board.push(move_obj)

    # Print the SAN moves
    correct_moves = []
    for san_move in san_moves:
        correct_moves.append(san_move)
    return correct_moves


def pgn_to_fen(pgn):
    # Split the moves by space
    moves = pgn.split()

    # Create a new chess board
    board = chess.Board()

    # Play the moves on the board
    for move in moves:
        board.push_san(move)

    # Print the final board position

    # Optionally, get the FEN notation of the final position
    fen = board.fen()
    return fen


def get_anki_data_from_api(puzzle_link):
    # Define the API endpoint and game ID (you can replace this with the specific ID you want)
    api_url = puzzle_link

    # Send a GET request to the API
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        puzzle_data_response = response.json()

        # Extract the PGN from the response
        pgn = puzzle_data_response['game']['pgn']
        solution = puzzle_data_response['puzzle']['solution']
        themes = puzzle_data_response['puzzle']['themes']

        return pgn, solution, themes
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
        return None


def generate_chess_position_png(pgn, puzzle_id):
    # Split the moves by space
    moves = pgn.split()

    # Create a new chess board
    board = chess.Board()

    # Play the moves on the board
    last_move = None
    for move in moves:
        last_move = board.push_san(move)

    # Export the board to an SVG string
    svg_data = chess.svg.board(board, lastmove=last_move, size=1000, colors={'square dark': "#76808e", "square light": "#A0AEC0"})
    print(svg_data)

    # Convert the SVG string to PNG using cairosvg and save it as an image
    cairosvg.svg2png(bytestring=svg_data, write_to=f"images/{puzzle_id}.png")


puzzle_urls = [
    "https://lichess.org/api/puzzle/ATSSe", "https://lichess.org/api/puzzle/5kHIg",
    "https://lichess.org/api/puzzle/PD1fP", "https://lichess.org/api/puzzle/MLiqa",
    "https://lichess.org/api/puzzle/uTR5C", "https://lichess.org/api/puzzle/54qbb",
    "https://lichess.org/api/puzzle/YMCyG"
    ]

# Define the Anki Model
my_model = genanki.Model(
    1607392319,
    'Genanki Chess Cards',
    fields=[
        {'name': 'Position'},
        {'name': 'Side to Move'},
        {'name': 'Solution'},
        {'name': 'Themes'},
        {'name': 'Lichess Link'},
        {'name': 'FEN'}
    ],
    templates=[
        {
            'name': 'Genanki Chess Card',

            'qfmt': '''{{Position}}
            <br>
            <br>
            <span class='play'>{{Side to Move}} to Play</span>''',  # How the front of the card will look

            'afmt': '''
            {{FrontSide}}

            <hr id=answer>

            Solution: <b>{{Solution}}</b>
            <hr>
            Themes: <i>{{Themes}}</i>
            <br>
            Lichess: <u><a href={{Lichess Link}}>{{FEN}}</a></u>''',  # How the back of the card will look
        },
    ])

# Create the Deck
my_deck = genanki.Deck(
    2059400111,
    'Lichess Tactics')


# Save the Deck to a File
genanki.Package(my_deck).write_to_file('output.apkg')

for puzzle in puzzle_urls:

    puzzle_data = get_anki_data_from_api(puzzle)
    time.sleep(1)

    pgn_data = puzzle_data[0]
    fen_data = pgn_to_fen(pgn_data)
    solution_data = puzzle_data[1]
    formatted_solution = format_solution(solution_data, fen_data)
    themes_data = puzzle_data[2]
    puzzle_id = puzzle[-5:]

    generate_chess_position_png(pgn_data, puzzle_id=puzzle_id)

    # Path to the image you want to add
    image_path = f'images/{puzzle_id}.png'

    # Read and encode the image in base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Create an img tag with the base64-encoded string
    img_tag = f'<img src="data:image/png;base64,{encoded_string}">'

    anki_card = {'Position': f'{img_tag}', 'Side to Move': determine_turn(fen_data), 'Solution': ', '.join(formatted_solution),
                 'Themes': ', '.join(themes_data), 'Lichess Link': 'https://lichess.org/training/' + puzzle_id,
                 'FEN': fen_data}

    # Step 1: Structure Your Data
    data = anki_card

    print(anki_card, pgn_data)

    # Step 4: Create a Note and Add It to the Deck
    my_note = genanki.Note(
        model=my_model,
        fields=[data['Position'], data['Side to Move'], data['Solution'], data['Themes'], data['Lichess Link'],
                data['FEN']])

    my_deck.add_note(my_note)

    time.sleep(1)

# Save the Deck to a File
genanki.Package(my_deck).write_to_file('lichess_tactics.apkg')

