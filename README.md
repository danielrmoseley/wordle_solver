# Wordle Solver

A smart, web-based tool to help you solve New York Times Wordle puzzles with optimal strategy. This app suggests the best next guess based on your previous attempts and their results.

## Features

- **Intelligent Word Filtering**: Uses advanced logic to eliminate impossible words based on your guesses
- **Optimal Recommendations**: Suggests the best next word to maximize information gain
- **Clean, Professional UI**: Beautiful light and dark mode support
- **Responsive Design**: Works seamlessly on desktop and tablet devices
- **Real-time Feedback**: Instantly updates suggestions as you input results

## How to Use

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/wordle_solver.git
   cd wordle_solver
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8050
   ```

### Using the App

1. **Start with the suggested word**: The app recommends "RATES" as the initial guess (a word with common, unique letters)

2. **Play the word in Wordle** and note the results for each letter:
   - **Green (G)**: Letter is in the correct position
   - **Yellow (Y)**: Letter is in the word but wrong position
   - **Black (B)**: Letter is not in the word

3. **Enter your guess**: Type the word you guessed into the input field

4. **Set the results**: Click each letter button to cycle through B → Y → G

5. **Submit**: Click "Submit Guess" to update the recommendation

6. **Repeat**: Follow each new suggestion until you solve the puzzle

7. **Reset**: Click "Reset Game" to start over

### Theme Toggle

Click the settings icon (⚙️) in the top right to toggle between light and dark modes.

## How the Logic Works

### Overview

The Wordle Solver uses a constraint-based filtering algorithm combined with information theory to suggest optimal guesses. Here's how it works:

### Step 1: Constraint Aggregation

After each guess, the app collects three types of information:

- **Greens (Correct Positions)**: Letters confirmed to be in specific positions
- **Yellows (Wrong Positions)**: Letters in the word but in wrong positions
- **Blacks (Not in Word)**: Letters confirmed not to be in the word

### Step 2: Word Filtering

The algorithm filters the remaining word list by applying these constraints:

```
For each candidate word:
  1. Green Check: All green letters must be at their correct positions
  2. Yellow Check: All yellow letters must be in the word but NOT at marked positions
  3. Black Check: The word must not contain any black-listed letters
  4. Duplicate Check: The word must have enough instances of each clued letter
```

#### Duplicate Letter Handling

Special care is taken with repeated letters. For example:
- If you guess "SPEED" and get G-B-Y-Y-G, the algorithm knows:
  - E is in positions 1 and 5 (both green)
  - E cannot be in position 3 (yellow conflict resolved)
  - D must appear elsewhere (it's not green, but marked yellow)

### Step 3: Optimal Word Scoring

Once the word list is filtered, the app selects the best next guess using a letter frequency score:

```
For each remaining candidate word:
  Score = sum of letter frequencies in remaining word list
  
Example: If the remaining words heavily feature K, L, and R,
then a word like "KLIER" scores higher than "AABBB"
```

This maximizes **information gain** — each guess is designed to eliminate the most possibilities regardless of whether it's the actual answer.

### Step 4: Early Guess Selection

When only 1-2 words remain, the algorithm switches strategy and picks from the remaining words directly, since any guess will likely solve the puzzle.

## Example Walkthrough

Let's say the answer is **ROBOT** (though you don't know this):

1. **Initial guess**: RATES
   - Result: B-B-Y-B-G (R is yellow, T is green)
   - Filtered words: ~200-300 remaining
   - Next suggestion: A word with common letters not yet tried

2. **Second guess**: You guess STONY
   - Result: B-G-B-B-Y (T is green at position 2, Y is yellow)
   - Filtered words: ~50-100 remaining
   - Next suggestion: Words with T at position 2, containing Y, and common letters

3. **Third guess**: You guess TOTAL
   - Result: G-B-G-B-G (T, T, L, R all green except O at position 2)
   - Filtered words: Very few remain
   - Next suggestion: ROBOT (the answer!)

## File Structure

```
wordle_solver/
├── app.py                    # Main Dash application
├── wordle_words.txt          # List of valid 5-letter words
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── Wordle Solver play 
    against itself.ipynb      # Jupyter notebook for analysis
```

## Technical Details

### Technology Stack

- **Framework**: Dash (Python web framework)
- **UI Components**: Dash Bootstrap Components
- **Styling**: Bootstrap 5 with custom themes

### Performance

- Filters ~13,000 word list in milliseconds
- Scores remaining words efficiently using Counter-based letter frequencies
- Real-time updates as you interact with the app

## Dependencies

See `requirements.txt` for the complete list:
- dash
- dash-bootstrap-components
- flask (included with Dash)

## Disclaimer

This solver is designed to help you learn optimal Wordle strategy. The New York Times Wordle terms of service should be respected — use this as a learning tool rather than pure automation.

## Future Enhancements

Potential improvements for future versions:
- Statistics tracking (guess distribution, solve rate)
- Historical word suggestions analysis
- Multiplayer mode
- API integration with actual Wordle game state

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests with improvements.

---

**Happy Wordle solving!** 🎮
