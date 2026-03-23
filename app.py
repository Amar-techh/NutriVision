import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from PIL import Image
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

conn = sqlite3.connect('nutrivision_v2.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS meals (username TEXT, date TEXT, food_name TEXT, amount REAL, calories REAL)''')
conn.commit()

st.set_page_config(page_title="NutriVision AI", layout="wide", page_icon="🍏")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Home"

if 'water_count' not in st.session_state:
    st.session_state['water_count'] = 0

if 'custom_timeline' not in st.session_state:
    st.session_state['custom_timeline'] = []

if not st.session_state['logged_in']:
    
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #00FF7F;'>🍏 NutriVision AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #aaaaaa;'>Your Generative AI Nutrition Assistant</h3>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("#### 📸 AI Plate Scanner\nStop typing. Just upload a picture of your food and let our cutting-edge vision model calculate your calories instantly.")
    with col2:
        st.success("#### 🍳 Smart Pantry Recipes\nTell us what ingredients are sitting in your kitchen, and our AI will invent a custom, macro-friendly recipe on the spot.")
    with col3:
        st.warning("#### 🤖 24/7 AI Dietitian\nChat with a personalized AI coach to get customized diet plans, progressive surplus strategies, and macro breakdowns.")
        
    st.divider()
    st.markdown("<h4 style='text-align: center;'>👈 Open the sidebar to Login or Create a Free Account to get started!</h4>", unsafe_allow_html=True)

    st.sidebar.title("Access Portal")
    login_tab, signup_tab = st.sidebar.tabs(["Login", "Sign Up"])
    
    with login_tab:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (login_user, login_pass))
            if c.fetchone():
                st.session_state['logged_in'] = True
                st.session_state['username'] = login_user
                st.session_state['current_page'] = "Home"
                st.rerun()
            else:
                st.error("Invalid username or password")
                
    with signup_tab:
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        if st.button("Sign Up", use_container_width=True):
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
                conn.commit()
                st.success("Account created! You can now log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Choose another.")

else:
    st.sidebar.title(f"Welcome, {st.session_state['username']}!")
    
    st.sidebar.divider()
    if st.sidebar.button("🏠 Home Hub", use_container_width=True):
        st.session_state['current_page'] = "Home"
        st.rerun()
    if st.sidebar.button("🎯 Daily Action Center", use_container_width=True):
        st.session_state['current_page'] = "Track My Diet"
        st.rerun()
    if st.sidebar.button("📸 Log Food", use_container_width=True):
        st.session_state['current_page'] = "Log Food"
        st.rerun()
    if st.sidebar.button("🍳 Meal Planner", use_container_width=True):
        st.session_state['current_page'] = "Meal Planner"
        st.rerun()
    if st.sidebar.button("🤖 AI Dietitian", use_container_width=True):
        st.session_state['current_page'] = "AI Dietitian"
        st.rerun()
        
    st.sidebar.divider()
    st.sidebar.caption("⚠️ **Disclaimer:** NutriVision AI provides estimates for general wellness and fitness tracking. It is not a substitute for professional medical advice.")
    st.sidebar.divider()

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['current_page'] = "Home"
        st.session_state['custom_timeline'] = []
        st.session_state['water_count'] = 0
        st.rerun()

    if st.session_state['current_page'] == "Home":
        st.markdown("<h2 style='text-align: center;'>What would you like to do today?</h2>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("### 🎯 Daily Action Center\nView your progress rings, log your water intake, and check your AI meal schedule for the day.")
            if st.button("Open Action Center ➔", use_container_width=True, key="btn_track"):
                st.session_state['current_page'] = "Track My Diet"
                st.rerun()
                
            st.write("")
            st.write("")
                
            st.warning("### 🍳 Smart Meal Planner\nGenerate custom AI recipes based on the exact ingredients currently sitting in your kitchen.")
            if st.button("Open Meal Planner ➔", use_container_width=True, key="btn_plan"):
                st.session_state['current_page'] = "Meal Planner"
                st.rerun()

        with col2:
            st.success("### 📸 AI Food Logger\nSnap a picture of your plate or manually enter your meals to instantly calculate calories.")
            if st.button("Open Food Logger ➔", use_container_width=True, key="btn_log"):
                st.session_state['current_page'] = "Log Food"
                st.rerun()
                
            st.write("")
            st.write("")
                
            st.error("### 🤖 AI Dietitian\nAsk your personal AI coach for customized diet plans, protein advice, and health strategies.")
            if st.button("Chat with AI ➔", use_container_width=True, key="btn_chat"):
                st.session_state['current_page'] = "AI Dietitian"
                st.rerun()

    elif st.session_state['current_page'] == "Track My Diet":
        st.title("🎯 Daily Action Center")
        df = pd.read_sql_query(f"SELECT date, calories FROM meals WHERE username='{st.session_state['username']}'", conn)
        
        today_str = str(date.today())
        today_data = df[df['date'] == today_str] if not df.empty else pd.DataFrame()
        total_today = today_data['calories'].sum() if not today_data.empty else 0
        
        st.markdown("### Today's Goal Progress")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Calories Consumed", f"{total_today} / 2800 kcal")
            st.progress(min(total_today / 2800, 1.0))
            
        with col2:
            protein_est = int(total_today * 0.04) 
            st.metric("Protein Est.", f"{protein_est}g / 140g")
            st.progress(min(protein_est / 140, 1.0))
            
        with col3:
            st.metric("Water Tracker", f"{st.session_state['water_count']} / 8 Glasses")
            st.progress(min(st.session_state['water_count'] / 8, 1.0))
            if st.button("💧 Log 1 Glass"):
                st.session_state['water_count'] += 1
                st.rerun()
                
        st.divider()
        
        st.markdown("### 🤖 Generate Your Custom AI Meal Plan")
        
        with st.form("diet_prefs_form"):
            st.write("Tell the AI exactly what you need for today:")
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                plan_goal = st.selectbox("Your Primary Goal", ["Weight Gain (Caloric Surplus)", "Weight Loss (Deficit)", "Maintenance"])
                meal_count = st.slider("How many meals today?", 3, 6, 4)
            with f_col2:
                plan_type = st.selectbox("Diet Preference", ["High Protein", "Vegetarian", "Vegan", "Balanced"])
                specific_requests = st.text_input("Specific requests?", placeholder="e.g., must include egg omelette with bread")
                
            generate_plan = st.form_submit_button("Generate & Sync Plan 🚀", use_container_width=True)

        if generate_plan:
            with st.spinner("AI is engineering your custom schedule..."):
                prompt = f"""
                Act as an expert dietitian. Generate a {meal_count}-meal daily schedule for a user with a {plan_goal} goal. 
                Their dietary preference is {plan_type}. Additional requests: {specific_requests if specific_requests else 'None'}.
                
                You MUST format your EXACT response like this example, with ONE meal per line, separated by the pipe symbol (|):
                08:00 AM|High-Protein Breakfast|3 egg omelette with 2 slices of bread, perfect for morning muscle recovery.
                01:00 PM|Heavy Lunch|150g chicken breast with 1 cup brown rice for complex carbs.
                
                Do not add any intro, outro, or standard formatting. Just return the raw piped lines.
                """
                response = model.generate_content(prompt)
                st.session_state['custom_timeline'] = response.text.strip().split('\n')
                st.rerun()
        
        if len(st.session_state['custom_timeline']) == 0:
            st.info("Your timeline is currently empty. Fill out the form above to generate your dynamic schedule!")
        else:
            st.success("Target Locked. Here is your interactive AI plan for today:")
            for meal in st.session_state['custom_timeline']:
                try:
                    time, name, desc = meal.split('|')
                    with st.expander(f"🕒 **{time.strip()}** - {name.strip()}", expanded=True):
                        st.write(desc.strip())
                except:
                    pass 

        st.divider()
        
        with st.expander("📉 View Monthly History Chart"):
            if not df.empty:
                daily_calories = df.groupby('date')['calories'].sum().reset_index()
                st.area_chart(daily_calories.set_index('date'), color="#00FF7F")
            else:
                st.write("No meals logged yet to generate a chart.")

    elif st.session_state['current_page'] == "Log Food":
        st.title("AI Calorie Tracker")
        log_date = st.date_input("Date", value=date.today())
        
        st.subheader("Scan Your Plate")
        uploaded_file = st.file_uploader("Upload a picture of your food", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            if st.button("Analyze Food with AI"):
                with st.spinner("Analyzing image..."):
                    try:
                        prompt = "Identify the main food in this image and estimate the calories for a standard portion. Return exactly in this format: Food Name|Calories (e.g. Masala Dosa|450). Do not include any other text."
                        response = model.generate_content([prompt, image])
                        
                        result = response.text.split("|")
                        food_prediction = result[0].strip()
                        estimated_calories = float(result[1].strip())
                        
                        st.success(f"AI Identified: {food_prediction}")
                        c.execute("INSERT INTO meals (username, date, food_name, amount, calories) VALUES (?, ?, ?, ?, ?)", 
                                  (st.session_state['username'], str(log_date), food_prediction, 100.0, estimated_calories))
                        conn.commit()
                        st.info(f"Saved {estimated_calories} kcal to your daily log!")
                    except Exception as e:
                        st.error("AI couldn't clearly identify the food. Try a different angle or use manual entry!")
                
        st.divider()
        
        st.subheader("Manual Entry")
        food_name = st.text_input("What did you eat?")
        amount = st.number_input("Amount (in grams)", min_value=1.0, value=100.0)
        
        if st.button("Log Manual Meal"):
            calories = amount * 1.5 
            c.execute("INSERT INTO meals (username, date, food_name, amount, calories) VALUES (?, ?, ?, ?, ?)", 
                      (st.session_state['username'], str(log_date), food_name, amount, calories))
            conn.commit()
            st.success(f"Logged {amount}g of {food_name}!")

    elif st.session_state['current_page'] == "Meal Planner":
        st.title("Smart Pantry Meal Planner")
        
        col1, col2 = st.columns(2)
        with col1:
            target_calories = st.number_input("Target Calories", min_value=100, step=50, value=500)
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        with col2:
            diet_preference = st.selectbox("Diet Preference", ["Any", "Vegetarian", "Vegan", "High Protein", "Low Carb"])
            
        available_ingredients = st.text_area("What ingredients do you have in your kitchen?", placeholder="e.g., Paneer, spinach, 2 eggs, leftover bread...")
        
        if st.button("Generate AI Recipe"):
            if not available_ingredients:
                st.warning("Please enter some ingredients first!")
            else:
                with st.spinner("Gemini is designing your recipe..."):
                    prompt = f"""
                    You are an expert nutritionist and chef. 
                    I have these ingredients: {available_ingredients}.
                    I want to eat a {diet_preference} {meal_type}.
                    My calorie goal for this meal is strictly around {target_calories} calories.
                    
                    Please provide:
                    1. A creative Recipe Name (You MUST start this line exactly with "RECIPE_NAME: ")
                    2. A short list of exactly how much of each ingredient I should use to hit the {target_calories} calorie goal.
                    3. Brief, step-by-step cooking instructions.
                    
                    Format the response clearly using Markdown.
                    """
                    response = model.generate_content(prompt)
                    
                    recipe_name = "Healthy Recipe" 
                    for line in response.text.split('\n'):
                        if "RECIPE_NAME:" in line:
                            recipe_name = line.replace("RECIPE_NAME:", "").replace("*", "").strip()
                            break
                    
                    st.toast('AI Recipe Successfully Generated!', icon='🤖')
                    st.balloons()
                    
                    clean_text = response.text.replace("RECIPE_NAME:", "🍽️ **Recipe:**")
                    st.markdown(clean_text)
                    
                    search_query = f"{recipe_name} recipe".replace(" ", "+")
                    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
                    
                    st.divider()
                    st.markdown(f"**[🎥 Watch a visual guide for the cooking technique here!]({youtube_url})**")
                    st.caption("*(Note: The YouTube creator's ingredient amounts will differ from your custom AI math. Follow the AI for your calories, and the video for the technique!)*")

    elif st.session_state['current_page'] == "AI Dietitian":
        st.title("Chat with your AI Dietitian")
        st.write("Ask for personalized diet plans, macro breakdowns, or general health advice!")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        user_prompt = st.chat_input("e.g. Can you create a high-calorie weight gain diet using egg omelettes and bread?")
        
        if user_prompt:
            with st.chat_message("user"):
                st.markdown(user_prompt)
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            
            with st.spinner("Thinking..."):
                chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                system_instruction = "You are a highly supportive, expert AI Dietitian. Give concise, actionable advice based on the user's questions."
                full_prompt = f"{system_instruction}\n\nHere is the conversation history:\n{chat_history}\n\nassistant:"
                
                response = model.generate_content(full_prompt)
                
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})