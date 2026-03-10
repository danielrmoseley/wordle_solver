import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import random
from collections import Counter

# --- App Initialization ---
# Initialize the Dash app without external stylesheets, will add dynamically
app = dash.Dash(__name__)
server = app.server

# --- Word List Preparation ---
# Load the word list from a local file. This list should contain all possible Wordle guesses.
try:
    with open('wordle_words.txt', 'r') as f:
        all_five_letter_words = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    # Fallback if the file is missing
    all_five_letter_words = ["apple", "braid", "rates", "hasty", "nasty"]

# For the initial state, we can use the same comprehensive list.
common_five_letter_words = all_five_letter_words

# --- Core Wordle Logic Functions ---

def get_initial_word():
    """
    Selects a good starting word for Wordle.
    A strong starting word has common, unique letters. 'rates' is a popular choice.
    """
    return "rates"

def filter_word_list(word_list, guesses):
    """
    Filters the word list based on the history of guesses and their results (clues).
    This function is designed to be accurate, especially with duplicate letters.
    """
    greens = {}  # Position -> Correct Letter
    yellows = {} # Letter -> List of incorrect positions
    blacks = set() # Set of letters confirmed not to be in the word

    # Aggregate clues from all past guesses
    for guess, result in guesses:
        # A temporary dictionary for green letters in the current guess
        temp_greens = {i: letter for i, (letter, status) in enumerate(zip(guess, result)) if status == 'G'}
        
        for i, (letter, status) in enumerate(zip(guess, result)):
            if status == 'G':
                greens[i] = letter
            elif status == 'Y':
                if letter not in yellows:
                    yellows[letter] = []
                yellows[letter].append(i)
            elif status == 'B':
                # A letter is only black if it's not green in the same guess
                if letter not in temp_greens.values():
                    blacks.add(letter)

    # Refine blacks: A letter can't be black if it's been identified as green or yellow.
    for letter in list(greens.values()) + list(yellows.keys()):
        if letter in blacks:
            blacks.remove(letter)
            
    # Refine yellows: A letter confirmed in a green position is no longer just a 'yellow' clue.
    for letter in greens.values():
        if letter in yellows:
            del yellows[letter]
            
    # --- Filter the word list based on aggregated clues ---
    filtered_list = []
    for word in word_list:
        valid = True
        
        # 1. Green Check: The word must contain all green letters at their correct positions.
        for pos, letter in greens.items():
            if word[pos] != letter:
                valid = False
                break
        if not valid: continue

        # 2. Yellow Check: The word must contain all yellow letters, but not in the positions where they were yellow.
        for letter, wrong_positions in yellows.items():
            if letter not in word or any(word[pos] == letter for pos in wrong_positions):
                valid = False
                break
        if not valid: continue
        
        # 3. Black Check: The word must not contain any black-listed letters.
        for letter in blacks:
            if letter in word:
                valid = False
                break
        if not valid: continue

        # 4. Duplicate Letter Count Check: The word must have at least as many instances of a letter as have been clued (greens + yellows).
        all_clued_letters = list(greens.values()) + list(yellows.keys())
        for letter in set(all_clued_letters):
            if word.count(letter) < all_clued_letters.count(letter):
                valid = False
                break
        if not valid: continue

        filtered_list.append(word)
        
    return filtered_list

def get_next_guess(word_list):
    """
    Determines the best next word to guess from the remaining possibilities.
    It scores words based on the frequency of their letters in the remaining list.
    """
    if not word_list:
        return None
    if len(word_list) <= 2:
        return random.choice(word_list)

    letter_counts = Counter("".join(word_list))
    best_word = ""
    max_score = -1
    
    # Score each word in the remaining list to find the most informative guess
    for word in word_list:
        score = sum(letter_counts[letter] for letter in set(word))
        if score > max_score:
            max_score = score
            best_word = word
            
    return best_word

# --- Application Layout ---

# Header section for the title, description, and settings button
header = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Wordle Solver", className="fw-bold text-center mb-3 display-5"), width=10),
        dbc.Col(dbc.Button(html.I(className="bi bi-gear-fill"), id="settings-button", color="link", size="lg", className="text-decoration-none"), width=2, className="text-end"),
    ], className="align-items-center"),
    html.P("Find the best guess to solve your Wordle puzzle.", className="text-center text-muted fs-6"),
], className="py-4 border-bottom")

# Main interactive card for user input
input_card = dbc.Card(
    dbc.CardBody([
        html.H5("Enter Your Guess", className="card-title fw-semibold mb-3"),
        dbc.Input(id='current-guess', type='text', maxLength=5, placeholder="e.g., RATES", className="mb-3 fs-3 text-center text-uppercase font-monospace form-control-lg"),
        html.H6("Result for each letter:", className="text-muted fw-normal small mb-2"),
        dbc.Row([dbc.Col(dbc.Button("B", id=f"result-{i}", color="secondary", className="w-100 fw-bold")) for i in range(5)], className="mb-3 g-2"),
        dbc.Button('Submit Guess', id='submit-button', color="primary", size="lg", className="w-100 fw-bold", disabled=True),
    ]),
    className="shadow rounded-2 mb-4 border-0",
)

# Card to display the history of guesses
history_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Guess History", className="card-title fw-semibold mb-3"),
                html.Div(id='guess-history', style={'minHeight': '300px', 'maxHeight': '400px', 'overflowY': 'auto'}),
            ]
        ),
        dbc.CardFooter(
            dbc.Row(
                [
                    dbc.Col(
                        # The reset button is moved to the bottom right of this card
                        dbc.Button(
                            'Reset Game',
                            id='reset-button',
                            color="danger",
                            size="sm",
                            className="float-end fw-semibold",
                        ),
                        width=12,
                    )
                ]
            )
        ),
    ],
    className="shadow rounded-2 mb-4 border-0",
)

# Assemble the main app layout
app.layout = dbc.Container(
    [
        # Dynamic theme link
        html.Link(id='theme-link', rel='stylesheet', href=dbc.themes.SPACELAB),
        # Bootstrap Icons
        html.Link(rel='stylesheet', href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"),
        header,
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Next Best Guess", className="card-title fw-semibold mb-3"),
                                    html.H2(id='next-guess-display', className="text-center text-info fw-bold font-monospace"),
                                ]
                            ),
                            className="shadow rounded-2 mb-4 border-0",
                        ),
                        html.Hr(),
                        input_card,
                    ],
                    md=6,
                ),
                dbc.Col(history_card, md=6),
            ],
            className="g-4",
        ),
        # Hidden div to store the game state across callbacks
        dcc.Store(
            id='game-state',
            data={
                'word_list': common_five_letter_words,
                'guesses': [],
                'next_guess': get_initial_word(),
            },
        ),
        # Store for theme mode
        dcc.Store(id='theme-store', data='light'),
        # Settings modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Settings")),
                dbc.ModalBody(
                    dbc.Form([
                        dbc.Label("Theme"),
                        dbc.Switch(id="theme-toggle", label="Dark Mode", value=False),
                    ])
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-settings", className="ml-auto")
                ),
            ],
            id="settings-modal",
            is_open=False,
        ),
    ],
    fluid=True,
    className="py-4 px-4 min-vh-100",
    style={"backgroundColor": "var(--bs-body-bg)"}
)


# --- Application Callbacks ---

# Callback to enable/disable the submit button based on input length
@app.callback(
    Output('submit-button', 'disabled'),
    Input('current-guess', 'value')
)
def toggle_submit_button(guess_value):
    """Disables the submit button if the input word is not 5 letters long."""
    return not (guess_value and len(guess_value) == 5 and guess_value.isalpha())

# Callbacks to handle cycling through button colors (B -> Y -> G)
for i in range(5):
    @app.callback(
        Output(f"result-{i}", 'children'),
        Output(f"result-{i}", 'color'),
        Input(f"result-{i}", 'n_clicks'),
        prevent_initial_call=True
    )
    def cycle_color(n_clicks):
        """Cycles through Black (B), Yellow (Y), and Green (G) for result buttons."""
        if n_clicks % 3 == 1:
            return "Y", "warning"
        elif n_clicks % 3 == 2:
            return "G", "success"
        else:
            return "B", "secondary"

# Main callback to update the game state based on user actions (submit or reset)
@app.callback(
    Output('game-state', 'data'),
    Output('next-guess-display', 'children'),
    Output('guess-history', 'children'),
    Output('current-guess', 'value'),
    Input('submit-button', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    State('game-state', 'data'),
    State('current-guess', 'value'),
    *[State(f"result-{i}", 'children') for i in range(5)]
)
def update_game(submit_clicks, reset_clicks, game_state, current_guess, *results):
    """
    This is the main callback that drives the game. It handles submitting a new guess
    or resetting the game, updating the word list and suggestions accordingly.
    """
    ctx = callback_context
    if not ctx.triggered:
        button_id = 'No-input'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle game reset
    if button_id == 'reset-button':
        initial_state = {
            'word_list': common_five_letter_words,
            'guesses': [],
            'next_guess': get_initial_word(),
        }
        return initial_state, initial_state['next_guess'], [], ""

    # Handle guess submission
    if button_id == 'submit-button' and current_guess:
        result = "".join(results)
        new_guesses = game_state['guesses'] + [[current_guess.lower(), result]]
        
        new_word_list = filter_word_list(game_state['word_list'], new_guesses)
        next_guess = get_next_guess(new_word_list) if new_word_list else "No words match!"

        if result == 'GGGGG':
            next_guess = f"Wordle solved in {len(new_guesses)} guesses!"

        updated_game_state = {
            'word_list': new_word_list,
            'guesses': new_guesses,
            'next_guess': next_guess,
        }

        # Create the visual history of guesses
        history_items = []
        for guess, res in reversed(new_guesses):
            history_items.append(
                dbc.Row([
                    dbc.Col(html.Span(guess.upper(), className="font-monospace fs-5")),
                    dbc.Col([
                        html.Span(f" {r} ", className=f"text-white bg-{('success' if r=='G' else 'warning' if r=='Y' else 'dark')} me-1 rounded") 
                        for r in res
                    ], className="text-end")
                ], className="mb-1 align-items-center")
            )
        
        return updated_game_state, next_guess, history_items, ""
    
    # Default state on initial load
    return game_state, game_state['next_guess'], [], ""

# Callback to toggle the settings modal
@app.callback(
    Output("settings-modal", "is_open"),
    Input("settings-button", "n_clicks"),
    Input("close-settings", "n_clicks"),
    State("settings-modal", "is_open"),
)
def toggle_modal(settings_clicks, close_clicks, is_open):
    """Toggles the settings modal open or closed based on button clicks."""
    if settings_clicks or close_clicks:
        return not is_open
    return is_open

# Callback to update the theme store and link based on toggle
@app.callback(
    Output('theme-store', 'data'),
    Output('theme-link', 'href'),
    Input('theme-toggle', 'value'),
)
def update_theme(toggle_value):
    """Updates the theme store and stylesheet href."""
    if toggle_value:
        return 'dark', dbc.themes.DARKLY
    else:
        return 'light', dbc.themes.FLATLY

# --- Run the Application ---
if __name__ == '__main__':
    app.run(debug=False)
