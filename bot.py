import discord
from discord.ext import tasks, commands
import random
import time
import json
import os

STATS_FILE = os.path.join(r"C:\Users\Conner Altizer\PythonCode\ModdiScape", "user_stats.json")
FLAVOR_TEXT_FILE = os.path.join(r"C:\Users\Conner Altizer\PythonCode\ModdiScape", "user_stat_flavor_text.json")
MODDI_FLAVOR_TEXT_FILE = os.path.join(r"C:\Users\Conner Altizer\PythonCode\ModdiScape", "moddi_stat_flavor_text.json")
COOLDOWN_TIME = 6 * 60 * 60 #6 hours in seconds
BOT_TOKEN = ""
AUTHORIZED_USER_ID = 0
SKILL_NAMES = ["Woodcutting", "Combat", "Fishing", "Mining", "Cooking", "Hunter", "Construction", "Prayer", "Crafting", "Thieving", "Farming"]
CHANNEL_ID = 0
RIVAL_USER_ID = 0

intents = discord.Intents.default()
intents.message_content = True
bot =  commands.Bot(command_prefix="!", intents=intents)



#load statistics from JSON
def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

#save statistics to JSON    
def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def user_exists(user_id):
    stats = load_stats()
    return str(user_id) in stats

def check_user_exists():
    def predicate(ctx):
        if user_exists(ctx.author.id):
            if ctx.author.id != RIVAL_USER_ID:
                update_display_name(str(ctx.author.id), ctx.author.display_name)
                return True
            else:
                return True
        else:
            create_user(ctx.author.id, ctx.author.display_name)
            return True
    return commands.check(predicate)

#checks if the channel the user is sending commands is the authorized channel for the bot, will result in True if no authorized channel is stated
def check_room_id(id):
    if id == CHANNEL_ID or CHANNEL_ID is None:
        return True
    else:
        return False
    
def create_user(user_id, user_name):
    stats = load_stats()
    user_id = str(user_id) #ensures ID is a string
    stats[user_id] = {
        "name" : user_name,
        "total_xp": 0,
        "skills": {
            "Woodcutting": 0,
            "Combat": 0,
            "Fishing": 0,
            "Mining": 0,
            "Cooking": 0,
            "Hunter": 0,
            "Construction": 0,
            "Prayer": 0,
            "Crafting": 0,
            "Thieving": 0,
            "Farming": 0
        },
        "last_used": 0,
        "last_trained_skill": "",
        "rubberchicken_success_xp": 0,
        "rubberchicken_failure_xp": 0,
        "number_of_times_trained": 0,
        "corporeal_beast_encounters": 0
    }
    save_stats(stats)

def get_user_data(user_id):
    stats = load_stats()
    return stats.get(str(user_id), None) #returns user data or None if not found

#Increases (or decreases) xp for a skill and saves it to the json file
def add_xp(user_id, skill, amount):
    stats = load_stats()
    
    stats[user_id]["skills"][skill] += amount
    if stats[user_id]["skills"][skill] < 0:
        stats[user_id]["skills"][skill] = 0
    stats[user_id]["total_xp"] = sum(stats[user_id]["skills"].values())

    save_stats(stats)

#Grabs a random number between 1 and the passed variable inclusive
def RNG(max):
    return random.randint(1, max)

#Pulls flavor text from a json file for the user's skill
def get_user_flavor_text(skill):
    try:
        with open(FLAVOR_TEXT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return random.choice(data.get(skill, ["You practice your skill in silence..."]))
    except FileNotFoundError:
        return "You try, but something feels off... (Missing user_stat_flavor_text.json)"


#Pulls flavor text from a json file for rival's skill
def get_rival_flavor_text(skill):
    try:
        with open(MODDI_FLAVOR_TEXT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return random.choice(data.get(skill, ["The rival did something..."]))
    except FileNotFoundError:
        return "The rival grows in power... (Missing rival_stat_flavor_text.json)"

#Pulls a random skill for the purpose of rival's xp    
def random_skill():
    return random.choice(SKILL_NAMES)

def random_crop():
    crops = {
        "Potatos": 7,
        "Cabbages": 10, 
        "Tomatos": 12, 
        "Sweetcorn": 13, 
        "Watermelons": 18, 
        "Poison Ivy plants": 22, 
        "Strawberries": 23, 
        "Jangerberries": 24, 
        "Swamp Mushrooms": 25, 
        "Hops": 26, 
        "Low-level Herbs": 28, 
        "Med-level Herbs": 31, 
        "High-level Herbs": 34, 
        "Limpwurts": 35, 
        "Giant Seaweed": 37, 
        "Grapes": 40, 
        "Pink Roses": 44, 
        "White Lilies": 48 
    }
    return random.choice(list(crops.items()))


def get_highest_skill(user_id):
    with open(STATS_FILE, "r") as file:
        user_data = json.load(file)

    user_skills = user_data[user_id]["skills"]
    highest_skill = max(user_skills, key=user_skills.get)

    return highest_skill

def get_top_users_per_skill():
    with open(STATS_FILE, "r") as file:
        user_data = json.load(file)

    top_users = {skill: {"name": None, "xp": 0} for skill in SKILL_NAMES}
    
    for skill in SKILL_NAMES:
        highest_xp = 0
        highest_user = None
        rival_xp = 0

        for user_id, data in user_data.items():
            xp = data["skills"].get(skill, 0)
            if user_id == str(RIVAL_USER_ID):
                rival_xp = xp
                continue
            
            if xp > highest_xp:
                highest_xp = xp
                highest_user = data["name"]

        if rival_xp > highest_xp:
            top_users[skill]["name"] = f"*{highest_user}"
            top_users[skill]["xp"] = highest_xp
        else:
            top_users[skill]["name"] = highest_user
            top_users[skill]["xp"] = highest_xp

    return top_users

def check_cooldown(user_id):
    user_data = get_user_data(user_id)
    current_time = time.time()
    
    if user_data and "last_used" in user_data:
        last_used = user_data.get("last_used", 0)
        remaining_time = COOLDOWN_TIME - (current_time - last_used)
        if remaining_time > 0:
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)
            last_skill = get_last_trained_skill(user_id)
            if last_skill == "Rubberchicken A":
                return False, f"You are fatigued from smacking Moddiply with a rubber chicken. You must rest for {hours} hours, {minutes} minutes, and {seconds} seconds."
            elif last_skill == "Rubberchicken B":
                return False, f"You are still recovering from being smacked with a rubber chicken. You must rest for {hours} hours, {minutes} minutes, and {seconds} seconds."
            elif last_skill == "Jumpscare":
                return False, f"You are still traumatized by the Corporeal Beast. You must rest for {hours} hours, {minutes} minutes, and {seconds} seconds."
            else:
                return False, f"You are fatigued from {last_skill}. You must rest for {hours} hours, {minutes} minutes, and {seconds} seconds."
        
    return True, None #No cooldown

def update_cooldown(user_id):
    stats = load_stats()
    stats[user_id]["last_used"] = time.time()

    save_stats(stats)

def update_number_times_trained(user_id):
    stats = load_stats()
    stats[user_id]["number_of_times_trained"] += 1

    save_stats(stats)

def update_corporeal_encounters(user_id):
    stats = load_stats()
    stats[user_id]["corporeal_beast_encounters"] += 1

    save_stats(stats)

def check_deny_list(user_id):
    if user_id == "166283676441772033":
        return False
    return True

def update_last_trained_skill(user_id, skill):
    stats = load_stats()
    stats[user_id]["last_trained_skill"] = skill

    save_stats(stats)
    return

def get_last_trained_skill(user_id):
    stats = load_stats()
    return stats[user_id]["last_trained_skill"]

def update_display_name(user_id, display_name):
    stats= load_stats()
    
    stats[user_id]["name"] = display_name
    save_stats(stats)

def get_highest_total_xp_user(ignore_user_id=None):
    with open(STATS_FILE, "r") as file:
        stats = json.load(file)

    filtered_users = {user_id: data for user_id, data in stats.items() if user_id != ignore_user_id}

    if not filtered_users:
        return None
    
    highest_xp_user_id = max(filtered_users, key=lambda user_id: filtered_users[user_id]["total_xp"])
    return highest_xp_user_id

def get_last_used_timestamp():
    try:
        with open(STATS_FILE, "r") as file:
            stats = json.load(file)

            last_used = max((user["last_used"] for user in stats.values() if "last_used" in user), default=0)
            return last_used
    except (FileNotFoundError, json.JSONDecodeError):
        return 0
    
def shorten_name(name, length):
    return name[:length] + "..." if len(name) > length else name
    
def compare_total_xp():
    stats = load_stats()

    rivaltotalxp = stats[str(RIVAL_USER_ID)]["total_xp"]
    usertotalxp = get_total_xp_all_users()
    if rivaltotalxp >= 1.2 * usertotalxp:
        print("Rival's total xp is 1.2x higher")
        return True
    elif usertotalxp >= 1.02 * rivaltotalxp:
        print("Rival's total xp is 1.02x lower")
        return False
    else:
        return None
    
def get_total_xp_all_users():
    total_xp = 0
    stats = load_stats()
    total_xp = sum(data["total_xp"] for user_id, data in stats.items() if user_id != str(RIVAL_USER_ID))
    return total_xp
    
def restart_daily_moddi(new_interval):
    daily_rival_increase.change_interval(hours=new_interval)


#Optional balance task to increase Moddi's xp if he doesn't have the highest and no one has participated in over 24 hours
@tasks.loop(hours=24)
async def daily_rival_increase():
    print("checking daily_rival_increase")
    last_used_time = get_last_used_timestamp()
    current_time = time.time()
    if current_time - last_used_time >= 86400:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            if get_highest_total_xp_user() != str(RIVAL_USER_ID):
                skill = random_skill()
                xp_gain = RNG(2000)
                add_xp(str(RIVAL_USER_ID), skill, xp_gain)
                print("triggered daily rival_increase")
                restart_daily_moddi(24)
                await channel.send(f"Moddiply takes advantage of the silence and power trains his {skill}. Moddiply gains {xp_gain} XP in {skill}.")
    else:
        restart_daily_moddi(1)
        return
    

#Command for training a skill
@bot.command()
@check_user_exists()
async def train(ctx, skill: str):
        
        if check_room_id(ctx.channel.id) == False:
            return
        
        user_id = str(ctx.author.id)
        if check_deny_list(user_id): #returns True if user is not on the deny list
            
            skill = skill.strip().lower().capitalize()
            if skill == "Random" or skill =="R":
                skill = random_skill()
            elif skill not in SKILL_NAMES:
                await ctx.send(f"Invalid skill! Choose from: {', '.join(SKILL_NAMES)}")
                return
            
            can_train, cooldown_message = check_cooldown(user_id)
            if not can_train:
                await ctx.send(f"{ctx.author.mention}, {cooldown_message}")
                return
            
            if RNG(100) == 1:
                update_last_trained_skill(user_id, "Jumpscare") #Updates stats json
                update_cooldown(user_id) #Updates stats json
                await ctx.send(f"https://imgur.com/a/3Z6s4Ei")
                return

            if skill == "Farming":
                result = RNG(100)
                if result <= 50:
                    crop, xp = random_crop()
                    rivalcrop, rivalxp = random_crop()

                    if crop in {"Potatos", "Cabbages", "Tomatos", "Sweetcorn", "Watermelons"}:
                        number_harvested = RNG(50)
                    elif crop in {"Poison Ivy plants", "Strawberries", "Jangerberries", "Swamp Mushrooms", "Hops", "Low-level Herbs", "Med-level Herbs", "High-level Herbs"}:
                        number_harvested = RNG(30)
                    else:
                        number_harvested = RNG(25)

                    if rivalcrop in {"Potatos", "Cabbages", "Tomatos", "Sweetcorn", "Watermelons"}:
                        rival_number_harvested = RNG(50)
                    elif rivalcrop in {"Poison Ivy plants", "Strawberries", "Jangerberries", "Swamp Mushrooms", "Hops", "Low-level Herbs", "Med-level Herbs", "High-level Herbs"}:
                        rival_number_harvested = RNG(30)
                    else:
                        rival_number_harvested = RNG(25)

                    if number_harvested == 1:
                        number_harvested = 2

                    xpgained = number_harvested * xp

                    if xpgained > 1000:
                        xpgained = 1000

                    if rival_number_harvested == 1:
                        number_harvested = 2

                    rivalxpgained = rival_number_harvested * rivalxp

                    if rivalxpgained > 1000:
                        rivalxpgained = 1000

                    add_xp(user_id, "Farming", xpgained) #Updates stats json
                    add_xp(str(RIVAL_USER_ID), "Farming", rivalxpgained) #Updates stats json
                    update_last_trained_skill(user_id, skill) #Updates stats json
                    update_cooldown(user_id) #Updates stats json
                    update_number_times_trained(user_id) #Updates stats json
                    await ctx.send(f"{ctx.author.mention} nurtures {number_harvested} {crop} to full growth and basks in a joyous harvest. You gained **{xpgained} XP** in Farming!. Unfortunately, Moddi thinks farming is a fierce competition with Mother Nature herself. In an attempt to flex on you, he plants {rival_number_harvested} {rivalcrop} in his allotment and doesn't leave until he gets the harvest. ModdiPly gains **{rivalxpgained} XP** in Farming!")
                    return
                elif result <= 53:
                    update_last_trained_skill(user_id, skill) #Updates stats json
                    update_cooldown(user_id) #Updates stats json
                    update_number_times_trained(user_id) #Updates stats json
                    await ctx.send(f"{ctx.author.mention} can't seem to grow anything but weeds. 0 Farming XP gained!")
                    return

            xpgained = RNG(1000)
            add_xp(user_id, skill, xpgained)
            flavor_text = get_user_flavor_text(skill)
            rival_skill = random_skill()
            rival_flavor_text = get_rival_flavor_text(rival_skill)
            rivalxp = RNG(1000)
            comparison_result = compare_total_xp()

            if comparison_result == True: #Rival's total xp is 1.2x higher than all user's xp combined
                print("Triggered moddiluck")
                rivalxp2 = RNG(1000)
                rivalxp = min(rivalxp, rivalxp2)
            elif comparison_result == False: #Rival's total xp is 1.02x lower than all user's xp combined
                print("Triggered rigged")
                rivalxp2 = RNG(1000)
                rivalxp = max(rivalxp, rivalxp2)

            add_xp(str(RIVAL_USER_ID), rival_skill, rivalxp) #Updates stats json

            await ctx.send(f"{ctx.author.mention}, {flavor_text}\nYou gained **{xpgained} XP** in {skill}! \nUnfortunately, {rival_flavor_text}\nModdi gains **{rivalxp} XP** in {rival_skill}")

            update_last_trained_skill(user_id, skill) #Updates stats json
            update_cooldown(user_id) #Updates stats json
            update_number_times_trained(user_id) #Updates stats json
            return
            
        else:
            await ctx.send(f"{ctx.author.mention}, You, specifically, are not allowed to participate, good day sir.")

#Shows the user's stats with the amount xp they have gained in each stat and altogether
@bot.command()
@check_user_exists()
async def stats(ctx):
        
    if check_room_id(ctx.channel.id) == False:
        return
    
    user_id = str(ctx.author.id)
    user_data = get_user_data(user_id)

    seperation_line = "-" * 26

    skills_text = seperation_line
    skills_text += "\n"
    skills_text += "\n".join([f"{skill.ljust(20)} {str(xp).rjust(5)}" for skill, xp in user_data["skills"].items()])
    await ctx.send(f"```{user_data['name']}'s Stats\n{seperation_line}\n{'Total XP'.ljust(20)} {str(user_data['total_xp']).rjust(5)}\n{skills_text}```")

#Show a list of skills and who the user is with the highest xp in that skill
@bot.command()
@check_user_exists()
async def ranks(ctx):

    if check_room_id(ctx.channel.id) == False:
        return

    top_users = get_top_users_per_skill()

    message = "```🏆 Skill Leaderboard 🏆\n"
    skill_width = 12
    name_width = 17
    xp_width = 6

    message += f"{'Skill'.ljust(15)}{'User'.ljust(18)}{'XP'.rjust(xp_width)}\n"
    message += "-" * (15 + 18 + xp_width) + "\n"

    for skill, info in top_users.items():
        if info["name"]:
            shortened_name = shorten_name(info["name"], 13)
            message += f"{skill.ljust(skill_width)} → {shortened_name.ljust(name_width)} {str(info['xp']).rjust(xp_width)}\n"

    # for skill, info in top_users.items():
    #     if info["name"]:
    #         shortened_name = shorten_name(info["name"])
    #         message += f"{skill.ljust(skill_width)}{shortened_name.ljust(name_width)}{str(info['xp']).rjust(xp_width)}\n"
    
    message += f"* = ModdiPly has the highest XP in the skill.```"
    await ctx.send(message)

@bot.command()
@check_user_exists()
async def leaderboard(ctx):

    if check_room_id(ctx.channel.id) == False:
        return

    stats = load_stats()

    sorted_users = sorted(stats.items(), key = lambda x: x[1]["total_xp"], reverse = True)

    message = "```🏆 XP Leaderboard 🏆\n"

    name_width = 29
    xp_width = 6

    message += f"{'User'.ljust(29)}{'XP'.rjust(xp_width)}\n"
    message += "-" * (35) + "\n"

    total_user_xp = 0

    for rank, (user_id, data) in enumerate(sorted_users, start = 1):
        user_name = shorten_name(data["name"], 25)
        total_xp = data["total_xp"]

        if user_id != "166283676441772033":
            total_user_xp += total_xp

        message += f"{user_name.ljust(name_width)}{str(total_xp).rjust(xp_width)}\n"

    message += "-" * (35) + "\n"
    message += f"{'Total Server XP'.ljust(name_width)}{str(total_user_xp).rjust(xp_width)}\n"
    message += "```"

    await ctx.send(message)

#Shows Moddiply's stats and total xp
@bot.command()
@check_user_exists()
async def moddistats(ctx):
    
    if check_room_id(ctx.channel.id) == False:
        return

    user_id = str(RIVAL_USER_ID)
    user_data = get_user_data(user_id)

    seperation_line = "-" * 26

    skills_text = seperation_line
    skills_text += "\n"
    skills_text += "\n".join([f"{skill.ljust(20)} {str(xp).rjust(5)}" for skill, xp in user_data["skills"].items()])
    await ctx.send(f"```{user_data['name']}'s Stats\n{seperation_line}\n{'Total XP'.ljust(20)} {str(user_data['total_xp']).rjust(5)}\n{skills_text}```")

#Flips a coin to remove xp from either Moddi or the user
@bot.command()
@check_user_exists()
async def rubberchicken(ctx):

    if check_room_id(ctx.channel.id) == False:
        return

    user_id = str(ctx.author.id)
    stats = load_stats()


    if check_deny_list(user_id): #returns True if user is not on the deny list
        can_train, cooldown_message = check_cooldown(user_id)
        if not can_train:
            await ctx.send(f"{ctx.author.mention}, {cooldown_message}")
            return 
        if stats[user_id]["total_xp"] == 0:
            await ctx.send(f"This action is unavailable until you have xp. Please try training a skill.")
            return
        xploss = RNG(1000)

        if RNG(2) == 1:
            skill = get_highest_skill(str(RIVAL_USER_ID))
            add_xp(str(RIVAL_USER_ID), skill, 0 - xploss)
            stats = load_stats()
            stats[user_id]["rubberchicken_success_xp"] += xploss
            save_stats(stats)
            update_last_trained_skill(user_id, "Rubberchicken A")
            await ctx.send(f"{ctx.author.mention}\nYou smack Moddiply with a rubber chicken. Moddiply loses **{xploss} XP** in {skill}!")
        else:
            skill = get_highest_skill(user_id)
            add_xp(user_id, skill, 0 - xploss)
            stats = load_stats()
            stats[user_id]["rubberchicken_failure_xp"] += xploss
            save_stats(stats)
            update_last_trained_skill(user_id, "Rubberchicken B")
            await ctx.send(f"{ctx.author.mention}\nModdiply successfully dodges your attack and thwaps you with a rubber chicken. You lose **{xploss} XP** in {skill}!")
        update_cooldown(user_id)
        return
    else:
        await ctx.send(f"{ctx.author.mention}, You, specifically, are not allowed to participate, good day sir.")

@bot.command()
async def reset(ctx):
    
    if check_room_id(ctx.channel.id) == False:
        return

    if ctx.author.id != AUTHORIZED_USER_ID:  #Change this after game to be modular
        return
    stats = {
        "166283676441772033": {
            "name": "Moddiply",
            "total_xp": 0,
            "skills": {
                "Woodcutting": 0,
                "Combat": 0,
                "Fishing": 0,
                "Mining": 0,
                "Cooking": 0,
                "Hunter": 0,
                "Construction": 0,
                "Prayer": 0,
                "Crafting": 0,
                "Thieving": 0,
                "Farming": 0
            },
            "last_used": 0,
            "last_trained_skill": "",
            "rubberchicken_success_xp": 0,
            "rubberchicken_failure_xp": 0,
            "number_of_times_trained": 0,
            "corporeal_beast_encounters": 0
        }
    }

    save_stats(stats)
    await ctx.send(f"{ctx.author.mention}, the stats file has been completely reset!")

@bot.command()
async def refresh(ctx):

    if check_room_id(ctx.channel.id) == False:
        return

    if ctx.author.id != AUTHORIZED_USER_ID:
        return
    
    stats = load_stats()
    for user_id in stats:
        stats[user_id]["last_used"] = 0

    await ctx.send(f"All cooldowns have been refreshed!")
    save_stats(stats)

@bot.command()
@check_user_exists()
async def fatigue(ctx):
    cooldown_status, cooldown_message = check_cooldown(str(ctx.author.id))
    if cooldown_status == True:
        await ctx.send(f"{ctx.author.mention}, you are well rested and ready to train!")
    else:
        await ctx.send(f"{ctx.author.mention}, {cooldown_message}")

@bot.command()
async def credits(ctx):
    #await ctx.send(f"Bot Development by **Mizu**\nProfile Picture by **Sarah**\nBot Testing conducted by **Mizu**, **Sarah**, **Kers**, and **ModdiPly**\nWriting by **Meow** and **PentaHybrid**\nGraphics by **Meow** and **PentaHybrid**")
    embed = discord.Embed(
        title="🎉 Bot Credits",
        description="Special thanks to everyone who contributed!",
        color=discord.Color.purple()  # You can change this color
    )

    embed.add_field(name="🛠️ Bot Development", value="**Mizu**", inline=False)
    embed.add_field(name="🖼️ Profile Picture", value="**Sarah**", inline=False)
    embed.add_field(name="🧪 Bot Testing", value="**Mizu**, **Sarah**, **Kers**, **ModdiPly**", inline=False)
    embed.add_field(name="✍️ Writing", value="**Meow**, **PentaHybrid**, **EngineerForGod**", inline=False)
    embed.add_field(name="🎨 Graphics", value="**Meow**, **PentaHybrid**", inline=False)
                    
    await ctx.send(embed=embed)

    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    daily_rival_increase.start()


bot.run(BOT_TOKEN)
