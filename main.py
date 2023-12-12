import telebot
import sqlite3
from telebot import types

# Initialize the Telegram Bot token
TOKEN = '6986413487:AAFfgyYuJSSIW-8QaxUec8VgdF1TBW4sfKY'
bot = telebot.TeleBot(TOKEN)

# Create the users table if not exists
with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            fitness_goal TEXT,
            workout_intensity TEXT,
            activity_level TEXT,
            weight_preference TEXT,
            dietary_preference TEXT
        )
    ''')
    conn.commit()

# Dictionary to store user progress
user_progress = {}

# Welcome message and fitness goals keyboard
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Welcome message
    bot.send_message(user_id, f"Welcome, {username}! I'm your Personal Fitness Assistant. Let's start by setting your fitness goal.")

    # Fitness goals keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    goals = ["Lose fat", "Build muscle", "Get stronger", "Improve endurance/conditioning", "Improve joint flexibility"]
    for goal in goals:
        markup.add(types.KeyboardButton(goal))

    bot.send_message(user_id, "Choose your fitness goal:", reply_markup=markup)

    # Set user progress to the first step
    user_progress[user_id] = "fitness_goal"

# Handle user's fitness goal
@bot.message_handler(func=lambda message: user_progress.get(message.from_user.id) == "fitness_goal")
def handle_fitness_goal(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Extract fitness goal from the user's message
    fitness_goal = message.text.strip()

    # Ask the user to choose workout intensity
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    intensities = ["Easy", "Moderate", "Hard"]
    for intensity in intensities:
        markup.add(types.KeyboardButton(intensity))

    bot.send_message(user_id, "Choose your workout intensity:", reply_markup=markup)

    # Store the fitness goal in the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, fitness_goal)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET fitness_goal=excluded.fitness_goal
        ''', (user_id, username, fitness_goal))

        conn.commit()

    # Set user progress to the next step
    user_progress[user_id] = "workout_intensity"

# Handle user's workout intensity
@bot.message_handler(func=lambda message: user_progress.get(message.from_user.id) == "workout_intensity")
def handle_workout_intensity(message):
    user_id = message.from_user.id

    # Extract workout intensity from the user's message
    workout_intensity = message.text.strip()

    # Ask the user to choose activity level
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    activity_levels = ["Sedentary", "Moderately Active", "Active"]
    for level in activity_levels:
        markup.add(types.KeyboardButton(level))

    bot.send_message(user_id, "Choose your activity level:", reply_markup=markup)

    # Store the workout intensity in the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET workout_intensity = ? WHERE user_id = ?
        ''', (workout_intensity, user_id))

        conn.commit()

    # Set user progress to the next step
    user_progress[user_id] = "activity_level"

# Handle user's activity level
@bot.message_handler(func=lambda message: user_progress.get(message.from_user.id) == "activity_level")
def handle_activity_level(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Extract activity level from the user's message
    activity_level = message.text.strip()

    # Ask the user about weight preference
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    weight_preferences = ["With Additional Weight", "Bodyweight Only"]
    for preference in weight_preferences:
        markup.add(types.KeyboardButton(preference))

    bot.send_message(user_id, "Do you prefer working with additional weight or with your own weight?", reply_markup=markup)

    # Store the activity level in the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET activity_level = ? WHERE user_id = ?
        ''', (activity_level, user_id))

        conn.commit()

    # Set user progress to the next step
    user_progress[user_id] = "weight_preference"

# Handle user's weight preference
@bot.message_handler(func=lambda message: user_progress.get(message.from_user.id) == "weight_preference")
def handle_weight_preference(message):
    user_id = message.from_user.id

    # Extract weight preference from the user's message
    weight_preference = message.text.strip()

    # Ask the user about dietary preference
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    dietary_preferences = ["Vegetarian", "Vegan", "Gluten-Free", "No Restrictions"]
    for preference in dietary_preferences:
        markup.add(types.KeyboardButton(preference))

    bot.send_message(user_id, "Do you have any dietary restrictions or preferences?", reply_markup=markup)

    # Store the weight preference in the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET weight_preference = ? WHERE user_id = ?
        ''', (weight_preference, user_id))

        conn.commit()

    # Set user progress to the next step
    user_progress[user_id] = "dietary_preference"

# Handle user's dietary preference
@bot.message_handler(func=lambda message: user_progress.get(message.from_user.id) == "dietary_preference")
def handle_dietary_preference(message):
    user_id = message.from_user.id

    # Extract dietary preference from the user's message
    dietary_preference = message.text.strip()

    # Store the dietary preference in the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET dietary_preference = ? WHERE user_id = ?
        ''', (dietary_preference, user_id))

        conn.commit()

    # Thank the user
    bot.send_message(user_id, "You are all set! Here is the list of what this bot can do:")
    bot.send_message(user_id, "1. Choose your fitness goal.")
    bot.send_message(user_id, "2. Choose your workout intensity.")
    bot.send_message(user_id, "3. Choose your activity level.")
    bot.send_message(user_id, "4. Choose your weight preference.")
    bot.send_message(user_id, "5. Choose your dietary preference.")
    bot.send_message(user_id, "Thank you! Your fitness goal, workout intensity, activity level, weight preference, and dietary preference have been recorded.")

    # Clear user progress
    del user_progress[user_id]

# Handle the /profile command
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result
        profile_message = f"Your Fitness Profile:\n\nFitness Goal: {fitness_goal}\nWorkout Intensity: {workout_intensity}\nActivity Level: {activity_level}\nWeight Preference: {weight_preference}\nDietary Preference: {dietary_preference}"
        bot.send_message(user_id, profile_message)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")

# Start the bot
print('bot is running')
bot.polling(none_stop=True)
