import os, json, random, discord
from pathlib import Path

save_file = os.path.join(os.path.dirname(__file__), "data/balatro.json")

deck_images = {
    "Red":          "https://static.wikia.nocookie.net/balatrogame/images/2/24/Red_Deck.png",
    "Blue":         "https://static.wikia.nocookie.net/balatrogame/images/2/24/Blue_Deck.png",
    "Yellow":       "https://static.wikia.nocookie.net/balatrogame/images/d/d7/Yellow_Deck.png",
    "Green":        "https://static.wikia.nocookie.net/balatrogame/images/1/12/Green_Deck.png",
    "Black":        "https://static.wikia.nocookie.net/balatrogame/images/2/20/Black_Deck.png",
    "Magic":        "https://static.wikia.nocookie.net/balatrogame/images/c/c3/Magic_Deck.png",
    "Nebula":       "https://static.wikia.nocookie.net/balatrogame/images/1/12/Nebula_Deck.png",
    "Ghost":        "https://static.wikia.nocookie.net/balatrogame/images/a/a1/Ghost_Deck.png",
    "Abandoned":    "https://static.wikia.nocookie.net/balatrogame/images/d/de/Abandoned_Deck.png",
    "Checkered":    "https://static.wikia.nocookie.net/balatrogame/images/a/a8/Checkered_Deck.png",
    "Zodiac":       "https://static.wikia.nocookie.net/balatrogame/images/2/20/Zodiac_Deck.png",
    "Painted":      "https://static.wikia.nocookie.net/balatrogame/images/8/8a/Painted_Deck.png",
    "Anaglyph":     "https://static.wikia.nocookie.net/balatrogame/images/a/ac/Anaglyph_Deck.png",
    "Plasma":       "https://static.wikia.nocookie.net/balatrogame/images/3/3c/Plasma_Deck.png",
    "Erratic":      "https://static.wikia.nocookie.net/balatrogame/images/1/17/Erratic_Deck.png",
}

seed_chars = [str(n) for n in range(10)] + [chr(n) for n in range(65, 91)]

# Serialized data
deck = "Red"
seed = ""


def save_data():
    with open(save_file, "w") as f:
        data = {
            "deck": deck,
            "seed": seed,
        }
        f.write(json.dumps(data))


def load_data():
    if Path(save_file):
        with open(save_file) as f:
            f_data = f.read()
            if f_data == "":
                return
            data = json.loads(f_data)

        global deck, seed
        deck = data["deck"]
        seed = data["seed"]


def create_new_seed() -> str:
    return "".join([random.choice(seed_chars) for _ in range(8)])


def create_embed(week: int) -> discord.Embed:
    embed = discord.Embed(
        title="Balatro: Golden Goblet",
        description=f"Week {week}\n\u200B",
        color=discord.Color.blue()
    )

    embed.set_image(url = deck_images[deck])
    embed.add_field(name="DECK", value=f"{deck} Deck")
    embed.add_field(name="SEED", value=seed)

    return embed


def randomize_setup():
    global deck, seed
    seed = create_new_seed()

    new_deck = deck
    while new_deck == deck:
        new_deck = random.choice(list(deck_images.keys()))
    
    deck = new_deck
