import random

def draw_cards(num_draw: int = 1) -> list:
    """
    Shuffles a standard deck of 52 cards and draws a specified number of cards from the top.

    Parameters:
    - num_draw (int, optional): The number of cards to be drawn. Defaults to 1.

    Returns:
    - list: A list of drawn cards.
    """
    # Define the deck of cards
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck = [f"{rank} of {suit}" for suit in suits for rank in ranks]
    
    # Shuffle the deck
    random.shuffle(deck)
    
    # Draw the specified number of cards
    num_draw = min(num_draw, len(deck))  # Prevent drawing more cards than available
    drawn_cards = deck[:num_draw]
    
    return f"Drawing {num_draw} card(s) from the deck: {drawn_cards}"

if __name__ == "__main__":
    # Example usage
    num_draw = 5  # Number of cards to draw
    cards = draw_cards(num_draw)
    print(f"Drawn Cards: {cards}")
