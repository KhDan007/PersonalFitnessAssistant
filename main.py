import os
import telebot
import sqlite3

from openai import OpenAI
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API")
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


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Welcome message
    bot.send_message(user_id,
                     f"Welcome, {username}! I'm your Personal Fitness Assistant. Let's start by setting your fitness goal.")

    # Fitness goals keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    goals = ["Lose fat", "Build muscle", "Get stronger", "Improve endurance", "Improve joint flexibility"]
    for goal in goals:
        markup.add(types.KeyboardButton(goal))

    # Prompt the user to choose a fitness goal
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

    # Check if the entered goal is in the list
    valid_goals = ["Lose fat", "Build muscle", "Get stronger", "Improve endurance",
                   "Improve joint flexibility"]
    if fitness_goal not in valid_goals:
        bot.send_message(user_id, "Invalid input. Please choose a valid fitness goal.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for goal in valid_goals:
            markup.add(types.KeyboardButton(goal))

        # Prompt the user to choose a fitness goal
        bot.send_message(user_id, "Choose your fitness goal:", reply_markup=markup)
        return

    # Continue with the workflow

    # Ask the user to choose workout intensity
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    intensities = ["Easy", "Moderate", "Hard"]
    for intensity in intensities:
        markup.add(types.KeyboardButton(intensity))

    # Prompt the user to choose workout intensity
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

    workout_intensity = message.text.strip()

    valid_intensities = ["Easy", "Moderate", "Hard"]
    if workout_intensity not in valid_intensities:
        bot.send_message(user_id, "Invalid input. Please choose a valid workout intensity level.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for goal in valid_intensities:
            markup.add(types.KeyboardButton(goal))

        bot.send_message(user_id, "Choose your workout intensity:", reply_markup=markup)
        return

    # Ask the user to choose activity level
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    activity_levels = ["Sedentary (Inactive)", "Moderately Active", "Active"]
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
    weight_preferences = ["With Additional Weight", "Body weight Only"]
    for preference in weight_preferences:
        markup.add(types.KeyboardButton(preference))

    bot.send_message(user_id, "Do you prefer working with additional weight or with your own weight?",
                     reply_markup=markup)

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

    features = """
Here is the list of what this bot can do:
1) View/update fitness profile (/profile)
2) Get personalized motivation (/motivation)
3) Receive personalized workout routine (/workout)
4) Get personalized nutrition tips (/nutrition)
5) Receive hydration tips for workouts (/hydration)
6) Get personalized exercise ideas (/exercises)
7) Receive stretching tips for flexibility (/stretching)
8) Get ideas for rest days (/rest)
9) Receive mindful fitness tips (/mindfulness)
10) Get personalized healthy snack ideas (/snack)   
    """

    # Thank the user
    bot.send_message(user_id,
                     "You are all set! Thank you! Your fitness goal, workout intensity, activity level, weight preference, and dietary preference have been recorded.")
    bot.send_message(user_id, features, parse_mode='Markdown')

    # Clear user progress
    del user_progress[user_id]


# Handle the /profile command
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result
        profile_message = f"Your Fitness Profile:\n\nFitness Goal: {fitness_goal}\nWorkout Intensity: {workout_intensity}\nActivity Level: {activity_level}\nWeight Preference: {weight_preference}\nDietary Preference: {dietary_preference}"

        # Create a custom keyboard with buttons to view, edit, or return to the main menu
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        view_button = types.KeyboardButton('View Profile')
        edit_button = types.KeyboardButton('Edit Profile')
        return_button = types.KeyboardButton('Return to Main Menu')
        markup.add(view_button, edit_button, return_button)

        # Prompt the user with their profile information and options
        bot.send_message(user_id, profile_message, reply_markup=markup)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Handle user's response to the /profile command
@bot.message_handler(func=lambda message: message.text in ['View Profile', 'Edit Profile', 'Return to Main Menu'])
def handle_profile_actions(message):
    user_id = message.from_user.id

    if message.text == 'View Profile':
        # Retrieve user characteristics from the database
        with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
                (user_id,))
            result = cursor.fetchone()

        if result:
            fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result
            profile_message = f"Your Fitness Profile:\n\nFitness Goal: {fitness_goal}\nWorkout Intensity: {workout_intensity}\nActivity Level: {activity_level}\nWeight Preference: {weight_preference}\nDietary Preference: {dietary_preference}"
            bot.send_message(user_id, profile_message)
        else:
            bot.send_message(user_id,
                             "You haven't set your fitness profile yet. Use the /start command to get started.")
    elif message.text == 'Edit Profile':
        # Fitness goals keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        goals = ["Lose fat", "Build muscle", "Get stronger", "Improve endurance",
                 "Improve joint flexibility"]
        for goal in goals:
            markup.add(types.KeyboardButton(goal))

        bot.send_message(user_id, "Choose your fitness goal:", reply_markup=markup)

        # Set user progress to the first step
        user_progress[user_id] = "fitness_goal"


    elif message.text == 'Return to Main Menu':
        # Send the list of features
        features_message = """
Here is the list of what this bot can do:
1) View/update fitness profile (/profile)
2) Get personalized motivation (/motivation)
3) Receive personalized workout routine (/workout)
4) Get personalized nutrition tips (/nutrition)
5) Receive hydration tips for workouts (/hydration)
6) Get personalized exercise ideas (/exercises)
7) Receive stretching tips for flexibility (/stretching)
8) Get ideas for rest days (/rest)
9) Receive mindful fitness tips (/mindfulness)
10) Get personalized healthy snack ideas (/snack)
                """
        bot.send_message(user_id, features_message, parse_mode='Markdown')


# Function to handle the /snack command
@bot.message_handler(commands=['snack'])
def handle_snack(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized healthy snack ideas for you... This usually takes about 15-20 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate snack ideas
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a nutritionist, skilled in providing healthy snack ideas for users, by analyzing their preferences"},
                {"role": "user",
                 "content": f"Generate personalized healthy snack ideas for a person who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/snack.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /workout command
@bot.message_handler(commands=['workout'])
def handle_workout(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized workout routine for you... This usually takes about 15-20 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate workout routine
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a fitness trainer, skilled in creating workout routines for users, by analyzing their preferences"},
                {"role": "user",
                 "content": f"Generate a personalized workout routine for user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/workout.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /motivation command
@bot.message_handler(commands=['motivation'])
def handle_motivation(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized motivation for you... This usually takes about 5-10 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate motivation
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a motivational coach, skilled in providing personalized motivation for users, by understanding their fitness goals"},
                {"role": "user",
                 "content": f"Generate a motivational quote for a person who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/motivation.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /nutrition command
@bot.message_handler(commands=['nutrition'])
def handle_nutrition_tips(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized nutrition tips for you... This usually takes about 15-20 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate nutrition tips
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a nutritionist, skilled in providing personalized nutrition tips for users, by understanding their fitness goals and dietary preferences"},
                {"role": "user",
                 "content": f"Generate 5 brief personalized nutrition tips for user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/nutrition.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /exercises command
@bot.message_handler(commands=['exercises'])
def handle_exercise_ideas(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized exercise ideas for you... This usually takes about 10-15 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate exercise ideas
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a fitness trainer, skilled in providing personalized exercise ideas for users, by understanding their fitness goals and preferences"},
                {"role": "user",
                 "content": f"Generate 5 short brief personalized exercise ideas for user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/exercises.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /stretching command
@bot.message_handler(commands=['stretching'])
def handle_stretching_tips(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized stretching tips for you... This usually takes about 15-20 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate stretching tips
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a fitness expert, skilled in providing personalized stretching tips for users, by understanding their fitness goals and preferences"},
                {"role": "user",
                 "content": f"Generate 5 brief and short personalized stretching tips for user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/stretching.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /hydration command
@bot.message_handler(commands=['hydration'])
def handle_hydration_tips(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized hydration tips for you... This usually takes about 10-15 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate hydration tips
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a fitness expert, skilled in providing personalized hydration tips for users, by understanding their fitness goals and preferences"},
                {"role": "user",
                 "content": f"Generate 3 brief short personalized hydration tips, each limited in 20 words for a user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/hydration.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /rest command
@bot.message_handler(commands=['rest'])
def handle_rest_day_ideas(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized rest day ideas for you... This usually takes about 10-15 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate rest day ideas
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a fitness expert, skilled in providing personalized rest day ideas for users, by understanding their fitness goals and preferences"},
                {"role": "user",
                 "content": f"Generate 5 personalized rest day ideas each limited to 15 words for user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/rest.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Function to handle the /mindfulness command
@bot.message_handler(commands=['mindfulness'])
def handle_mindful_fitness(message):
    user_id = message.from_user.id

    # Retrieve user characteristics from the database
    with sqlite3.connect('fitness_bot.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference FROM users WHERE user_id = ?',
            (user_id,))
        result = cursor.fetchone()

    if result:
        fitness_goal, workout_intensity, activity_level, weight_preference, dietary_preference = result

        # Send initial message
        initial_message = "Generating personalized mindful fitness tips for you... This usually takes about 10-15 seconds..."
        bot.send_message(user_id, initial_message)

        # Use OpenAI API to generate mindful fitness tips
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a fitness expert, skilled in providing personalized mindful fitness tips for users, by understanding their fitness goals and preferences"},
                {"role": "user",
                 "content": f"Generate 5 personalized mindful fitness tips each limited in 20 words for a user who selected: Fitness Goal: {fitness_goal}, Workout Intensity: {workout_intensity}, Activity Level: {activity_level}, Weight Preference: {weight_preference}, Dietary Preference: {dietary_preference}."}
            ]
        )

        # Retrieve and send the generated response
        response = completion.choices[0].message.content
        print(response)
        bot.send_message(user_id, response, parse_mode='Markdown')

        # Send the image along with the tips
        with open('img/mindfulness.jpg', 'rb') as photo:
            bot.send_photo(user_id, photo)
    else:
        bot.send_message(user_id, "You haven't set your fitness profile yet. Use the /start command to get started.")


# Generic error handling function
@bot.message_handler(func=lambda message: True)
def handle_invalid_command(message):
    user_id = message.from_user.id

    # Respond with an error message
    error_message = "I'm sorry, but I didn't understand that command. Here are some available commands:\n\n" \
                    "/profile: View/update fitness profile\n" \
                    "/motivation: Get personalized motivation\n" \
                    "/workout: Receive personalized workout routine\n" \
                    "/nutrition: Get personalized nutrition tips\n" \
                    "/hydration: Receive hydration tips for workouts\n" \
                    "/exercises: Get personalized exercise ideas\n" \
                    "/stretching: Receive stretching tips for flexibility\n" \
                    "/rest: Get ideas for rest days\n" \
                    "/mindfulness: Receive mindful fitness tips\n" \
                    "/snack: Get personalized healthy snack ideas"

    bot.send_message(user_id, error_message, parse_mode='Markdown')


# Start the bot
print('bot is running')
bot.polling(none_stop=True)
