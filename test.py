import random

def random_crop():
    crops = {
        "Potato": 7,
        "Cabbage": 10, 
        "Tomato": 12, 
        "Sweetcorn": 13, 
        "Watermelon": 18, 
        "Poison Ivy": 22, 
        "Strawberry": 23, 
        "Jangerberry": 24, 
        "Swamp Mushroom": 25, 
        "Hops": 26, 
        "Low-level herb": 28, 
        "Med-level herb": 31, 
        "High-level herb": 34, 
        "Limpwurt": 35, 
        "Giant seaweed": 37, 
        "Grapes": 40, 
        "Pink roses": 44, 
        "White lily": 48 
    }
    return random.choice(list(crops.items()))

# Example usage:
crop, xp = random_crop()
print(f"You harvested {crop} and gained {xp} XP!")