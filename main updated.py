import streamlit as st
import json
from recipe_generator import RecipeGenerator
from utils import load_css, display_food_image_carousel
from database import init_db
from expiration_tracker import display_expiration_tracker
from user_preferences import display_user_preferences, UserPreferences, get_personalized_recommendations
import datetime

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="SmartChef - AI Recipe Generator & Food Waste Reducer",
    page_icon="🍳",
    layout="wide"
)

# Load custom CSS
load_css()

# Initialize session states if not already
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'recipe' not in st.session_state:
    st.session_state.recipe = None
if 'like_recipe' not in st.session_state:
    st.session_state.like_recipe = False

def set_page(page_name):
    st.session_state.page = page_name

def main():
    # Initialize recipe generator
    recipe_gen = RecipeGenerator()
    
    # Initialize user preferences
    user_prefs = UserPreferences()

    # Header section with navigation menu
    col1, col2, col3, col4, col5 = st.columns([6, 2, 2, 2, 2])
    
    with col1:
        st.title("🍳 SmartChef")
    
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            set_page('home')
    
    with col3:
        if st.button("👤 Preferences", use_container_width=True):
            set_page('preferences')
    
    with col4:
        if st.button("🗓️ Expiration Tracker", use_container_width=True):
            set_page('expiration')
    
    with col5:
        if st.button("📚 Recipe History", use_container_width=True):
            set_page('history')
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Display selected page
    if st.session_state.page == 'home':
        display_home_page(recipe_gen, user_prefs)
    elif st.session_state.page == 'preferences':
        display_user_preferences()
    elif st.session_state.page == 'expiration':
        display_expiration_tracker()
    elif st.session_state.page == 'history':
        display_history_page(user_prefs)
    else:
        # Default to home
        display_home_page(recipe_gen, user_prefs)

def display_home_page(recipe_gen, user_prefs):
    """Display the main home page with recipe generator"""
    # Image carousel
    display_food_image_carousel()

    # Sidebar for input
    with st.sidebar:
        st.header("🥗 Available Ingredients")
        
        # Option to auto-fill from expiring soon ingredients
        if st.checkbox("Include expiring soon ingredients"):
            from expiration_tracker import ExpirationTracker
            tracker = ExpirationTracker()
            expiring_items = tracker.get_expiring_soon(days=3)
            
            expiring_ingredients = [item['name'] for item in expiring_items]
            if expiring_ingredients:
                st.info(f"Including {len(expiring_ingredients)} expiring ingredients")
                prefilled = "\n".join(expiring_ingredients)
            else:
                prefilled = ""
                st.info("No expiring ingredients found")
        else:
            prefilled = ""
        
        ingredients = st.text_area(
            "Enter your ingredients (one per line):",
            value=prefilled,
            height=200,
            help="List ingredients you have available"
        )

        # Get dietary preferences from user profile
        default_dietary = user_prefs.get_dietary_preferences()
        
        dietary_prefs = st.multiselect(
            "Dietary Preferences:",
            ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb", "Keto", "Paleo", "Pescatarian", "Nut-Free"],
            default=default_dietary
        )

        # Option to use personalized recommendations
        use_preferences = st.checkbox("Use my preferences", value=True, help="Use your favorite ingredients and cuisine preferences")
        
        generate_btn = st.button("Generate Recipe 🪄", use_container_width=True)
        
        # Show the user's preference summary if they're using preferences
        if use_preferences:
            st.write("**Using your preferences:**")
            
            fav_ingredients = user_prefs.get_favorite_ingredients()
            if fav_ingredients:
                st.write("💚 Favorites: " + ", ".join(fav_ingredients[:3]))
                
            cuisines = user_prefs.get_cuisine_preferences()
            if cuisines:
                st.write("🌍 Cuisines: " + ", ".join(cuisines[:2]))
                
            disliked = user_prefs.get_disliked_ingredients()
            if disliked:
                st.write("❌ Avoiding: " + ", ".join(disliked[:3]))

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        if generate_btn and ingredients:
            with st.spinner("Generating your recipe..."):
                ingredients_list = [i.strip() for i in ingredients.split("\n") if i.strip()]
                
                # Get personalized recommendations if requested
                if use_preferences:
                    personalization = get_personalized_recommendations(ingredients_list)
                else:
                    personalization = None
                
                recipe = recipe_gen.generate_recipe(ingredients_list, dietary_prefs, personalization)
                st.session_state.recipe = recipe
                
                # Display recipe card
                with st.container():
                    # Check if we have a valid recipe or an error message
                    if recipe.get('prep_time', 0) == 0 and recipe.get('servings', 0) == 0:
                        # This is likely an error response
                        st.error(f"⚠️ {recipe['title']}")
                        
                        # Show instructions as error message
                        for message in recipe['instructions']:
                            st.warning(message)
                        
                        # Show tips as info message
                        st.info(recipe['tips'])
                    else:
                        # Show the successful recipe
                        st.subheader(f"📖 {recipe['title']}")
                        
                        # Recipe feedback buttons in a row
                        like_col, dislike_col, save_col = st.columns([1, 1, 2])
                        with like_col:
                            if st.button("👍 Like", use_container_width=True):
                                user_prefs.add_liked_recipe(recipe)
                                user_prefs.add_meal_to_history(recipe['title'])
                                st.success("Recipe saved to favorites!")
                        
                        with dislike_col:
                            if st.button("👎 Dislike", use_container_width=True):
                                user_prefs.add_disliked_recipe(recipe)
                                st.info("We'll avoid similar recipes in the future")
                                
                        with save_col:
                            meal_types = ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"]
                            selected_meal = st.selectbox("Save as meal type:", meal_types, index=2)
                            
                        st.write(f"⏱️ Prep Time: {recipe['prep_time']} minutes")
                        st.write(f"👥 Servings: {recipe['servings']}")
                        
                        # Show cuisine if available
                        if 'cuisine' in recipe:
                            st.write(f"🌍 Cuisine: {recipe['cuisine']}")

                        st.write("### Ingredients")
                        for ingredient in recipe['ingredients']:
                            st.write(f"• {ingredient}")

                        st.write("### Instructions")
                        for idx, step in enumerate(recipe['instructions'], 1):
                            st.write(f"{idx}. {step}")

                        st.write("### Tips")
                        st.info(recipe['tips'])
                        
                        # Add feature to save ingredients to expiration tracker
                        st.write("### Track Leftover Ingredients")
                        with st.expander("Add unused ingredients to expiration tracker"):
                            from expiration_tracker import ExpirationTracker
                            tracker = ExpirationTracker()
                            
                            ingredient_to_track = st.selectbox(
                                "Select ingredient to track:", 
                                [ing.split(',')[0].strip() for ing in recipe['ingredients']]
                            )
                            
                            expiry_date = st.date_input(
                                "Expiration date:",
                                value=(datetime.date.today() + datetime.timedelta(days=7)),
                                min_value=datetime.date.today()
                            )
                            
                            quantity = st.text_input("Quantity (optional):")
                            
                            if st.button("Add to Tracker"):
                                success = tracker.add_item(
                                    ingredient_to_track, 
                                    expiry_date, 
                                    quantity
                                )
                                
                                if success:
                                    st.success(f"Added {ingredient_to_track} to expiration tracker!")
                                else:
                                    st.error("Error adding item. Please try again.")

    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #f0f2f6; padding-bottom: 6px;">
            <div style="color: #4CAF50; font-size: 24px; margin-right: 10px;">🌱</div>
            <div style="font-size: 20px; font-weight: 600; color: #333;">Food Waste Reduction Tips</div>
        </div>
        """, unsafe_allow_html=True)
        
        if ingredients:
            with st.spinner("Generating tips..."):
                waste_tips = recipe_gen.get_waste_reduction_tips(ingredients.split("\n"))
                
                # Check if we have tips or error messages
                if isinstance(waste_tips, list) and len(waste_tips) == 1 and isinstance(waste_tips[0], str) and any(error_keyword in waste_tips[0].lower() 
                                               for error_keyword in ["unavailable", "api key", "billing"]):
                    st.warning(waste_tips[0])
                else:
                    # Create a formatted container for tips with better styling
                    with st.container():
                        # Check if the tips are in the new format (list of dicts with ingredient and tips)
                        if isinstance(waste_tips, list) and len(waste_tips) > 0 and isinstance(waste_tips[0], dict) and "ingredient" in waste_tips[0]:
                            # Iterate through the ingredients and their tips
                            for item in waste_tips:
                                ingredient = item.get("ingredient", "")
                                tips = item.get("tips", [])
                                
                                if ingredient and tips:
                                    # Create a compact card for each ingredient with its tips
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #f5f9f5; border-radius: 8px; padding: 12px; 
                                                   margin-bottom: 12px; border-left: 3px solid #4CAF50; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                                            <div style="font-weight: 600; color: #2E7D32; margin-bottom: 8px; font-size: 15px;">
                                                {ingredient}
                                            </div>
                                            <div style="margin-left: 5px;">
                                                {"".join([f'<div style="display: flex; margin-bottom: 6px; align-items: flex-start;">'
                                                        f'<div style="color: #4CAF50; margin-right: 6px; font-size: 14px;">•</div>'
                                                        f'<div style="font-size: 14px; line-height: 1.4; color: #333;">{tip}</div>'
                                                        f'</div>' for tip in tips])}
                                            </div>
                                        </div>
                                        """, 
                                        unsafe_allow_html=True
                                    )
                        else:
                            # Fallback to the original format for backward compatibility
                            for tip in waste_tips:
                                # Check if tip is a string or other type
                                if isinstance(tip, str):
                                    # Clean up the tip text if it's a string
                                    tip_text = tip.strip()
                                    if not tip_text:  # Skip empty tips
                                        continue
                                else:
                                    # Handle case where tip might be a dictionary or other type
                                    tip_text = str(tip)
                                    
                                # Create a card-like appearance for each tip
                                with st.container():
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #f5f9f5; border-radius: 8px; padding: 10px; 
                                                  margin-bottom: 8px; border-left: 3px solid #4CAF50;">
                                            <span style='font-size: 14px; color: #333;'>• {tip_text}</span>
                                        </div>
                                        """, 
                                        unsafe_allow_html=True
                                    )

        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 20px; border-bottom: 1px solid #f0f2f6; padding-bottom: 6px;">
            <div style="color: #2196F3; font-size: 24px; margin-right: 10px;">🔄</div>
            <div style="font-size: 20px; font-weight: 600; color: #333;">Ingredient Substitutions</div>
        </div>
        """, unsafe_allow_html=True)
        
        if ingredients:
            with st.spinner("Finding substitutions..."):
                substitutions = recipe_gen.get_substitutions(ingredients.split("\n"))
                
                # Check for any error messages in the first substitution
                first_ingredient = next(iter(substitutions.items()))[0]
                first_subs = substitutions[first_ingredient]
                
                if len(first_subs) == 1 and any(error_keyword in first_subs[0].lower() 
                                               for error_keyword in ["unavailable", "api key", "billing"]):
                    # Display a single warning instead of repeating for each ingredient
                    st.warning(first_subs[0])
                else:
                    # Create better-looking containers for substitutions
                    for original, subs in substitutions.items():
                        st.markdown(
                            f"""
                            <div style="background-color: #e3f2fd; border-radius: 8px; padding: 12px; 
                                      margin-bottom: 12px; border-left: 3px solid #2196F3; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                                <div style="font-weight: 600; color: #1976D2; margin-bottom: 8px; font-size: 15px;">
                                    {original.capitalize()} can be replaced with:
                                </div>
                                <div style="margin-left: 5px;">
                                    {"".join([f'<div style="display: flex; margin-bottom: 6px; align-items: flex-start;">'
                                            f'<div style="color: #2196F3; margin-right: 6px; font-size: 14px;">•</div>'
                                            f'<div style="font-size: 14px; line-height: 1.4; color: #333;">{sub if isinstance(sub, str) else str(sub)}</div>'
                                            f'</div>' for sub in subs])}
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
        
        # Expiration reminder
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 20px; border-bottom: 1px solid #f0f2f6; padding-bottom: 6px;">
            <div style="color: #FF9800; font-size: 24px; margin-right: 10px;">⚠️</div>
            <div style="font-size: 20px; font-weight: 600; color: #333;">Ingredient Expiration Guide</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show expiring ingredients and guide for input ingredients
        try:
            from expiration_tracker import ExpirationTracker
            tracker = ExpirationTracker()
            
            # Get items from expiration tracker
            expiring_items = tracker.get_expiring_soon(days=3)
            expired_items = tracker.get_expired()
            
            # Typical expiration times for common ingredients
            common_expirations = {
                "onion": {"shelf": "2-3 months", "fridge": "1-2 months", "freezer": "8-12 months"},
                "rice": {"shelf": "1-2 years (white), 3-6 months (brown)", "fridge": "Not recommended", "freezer": "Up to 6 months cooked"},
                "chicken": {"shelf": "Not recommended raw", "fridge": "1-2 days raw, 3-4 days cooked", "freezer": "9-12 months raw, 2-6 months cooked"},
                "paneer": {"shelf": "Not recommended", "fridge": "1-2 weeks unopened, 3-5 days opened", "freezer": "3-4 months"},
                "green chilli": {"shelf": "1-2 weeks", "fridge": "2-3 weeks", "freezer": "4-6 months"},
                "eggs": {"shelf": "Not recommended", "fridge": "3-5 weeks", "freezer": "Not recommended raw"},
                "milk": {"shelf": "Not recommended fresh", "fridge": "5-7 days opened", "freezer": "3 months"},
                "tomato": {"shelf": "4-7 days ripe", "fridge": "1-2 weeks", "freezer": "2-3 months"},
                "potato": {"shelf": "2-3 months cool, dark place", "fridge": "3-4 weeks", "freezer": "10-12 months cooked"},
                "bread": {"shelf": "5-7 days", "fridge": "1-2 weeks", "freezer": "2-3 months"},
                "cheese": {"shelf": "Not recommended soft cheese", "fridge": "1-4 weeks (hard), 1-2 weeks (soft)", "freezer": "6-8 months"},
                "leafy greens": {"shelf": "Not recommended", "fridge": "3-5 days", "freezer": "8-12 months blanched"},
                "fruits": {"shelf": "2-7 days ripe", "fridge": "1-2 weeks", "freezer": "8-12 months"},
                "meat": {"shelf": "Not recommended raw", "fridge": "1-2 days raw, 3-4 days cooked", "freezer": "4-12 months depending on type"},
                "vegetables": {"shelf": "Varies by type", "fridge": "1-2 weeks most varieties", "freezer": "8-12 months"},
                "beans": {"shelf": "1-2 years dry", "fridge": "3-5 days cooked", "freezer": "1-2 months cooked"},
                "tofu": {"shelf": "Not recommended", "fridge": "3-5 days opened", "freezer": "4-6 months"},
                "oil": {"shelf": "3-5 months opened", "fridge": "Up to 1 year", "freezer": "Not recommended"},
                "garlic": {"shelf": "3-6 months whole head", "fridge": "1-2 weeks peeled", "freezer": "6-8 months"},
                "herbs": {"shelf": "Not recommended fresh", "fridge": "1-2 weeks fresh", "freezer": "6-12 months"},
                "spices": {"shelf": "1-2 years ground, 2-3 years whole", "fridge": "Not necessary", "freezer": "Not necessary"}
            }
            
            # Show tracked items that are expiring or expired
            if expired_items:
                st.error(f"{len(expired_items)} items have expired! [Check Now](/?page=expiration)")
            
            if expiring_items:
                st.warning(f"{len(expiring_items)} tracked items expiring within 3 days!")
                
                # Show the first 3 expiring items
                for item in expiring_items[:3]:
                    days_text = "Today!" if item.get('days_left', 0) == 0 else f"in {item.get('days_left', '?')} days"
                    st.markdown(
                        f"""
                        <div style="background-color: #fff3e0; padding: 8px; border-radius: 5px; 
                                    margin-bottom: 8px; border-left: 3px solid #ff9800;">
                            <span style="font-weight: bold;">{item['name']}</span> ({item.get('quantity', '')})
                            <br><span style="font-size: 12px;">Expires {days_text}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                if len(expiring_items) > 3:
                    st.write(f"[View all {len(expiring_items)} expiring items](/?page=expiration)")
            
            # Get ingredients from the input
            if ingredients:
                input_ingredients = [i.strip().lower() for i in ingredients.split('\n') if i.strip()]
                
                # Show expiration guidance for input ingredients
                st.markdown("""
                <div style="font-size: 17px; font-weight: 500; color: #555; margin: 15px 0 10px 0;">
                    Expiration Guide for Your Ingredients
                </div>
                """, unsafe_allow_html=True)
                
                for ing in input_ingredients:
                    # Find the closest match in our common expirations dictionary
                    match_found = False
                    
                    for common_ing in common_expirations:
                        if common_ing in ing or ing in common_ing:
                            exp_data = common_expirations[common_ing]
                            
                            st.markdown(
                                f"""
                                <div style="background-color: #fff3e0; border-radius: 8px; padding: 12px; 
                                           margin-bottom: 12px; border-left: 3px solid #FF9800; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                                    <div style="font-weight: 600; color: #E65100; margin-bottom: 8px; font-size: 15px;">
                                        {ing.capitalize()}
                                    </div>
                                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                        <div style="flex: 1; min-width: 110px;">
                                            <div style="font-size: 12px; color: #888; margin-bottom: 2px;">SHELF</div>
                                            <div style="font-size: 14px;">{exp_data["shelf"]}</div>
                                        </div>
                                        <div style="flex: 1; min-width: 110px;">
                                            <div style="font-size: 12px; color: #888; margin-bottom: 2px;">REFRIGERATOR</div>
                                            <div style="font-size: 14px;">{exp_data["fridge"]}</div>
                                        </div>
                                        <div style="flex: 1; min-width: 110px;">
                                            <div style="font-size: 12px; color: #888; margin-bottom: 2px;">FREEZER</div>
                                            <div style="font-size: 14px;">{exp_data["freezer"]}</div>
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            match_found = True
                            break
                    
                    # If no match found, show generic advice
                    if not match_found:
                        st.markdown(
                            f"""
                            <div style="background-color: #e8f5e9; border-radius: 8px; padding: 12px; 
                                      margin-bottom: 12px; border-left: 3px solid #4CAF50; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                                <div style="font-weight: 600; color: #2E7D32; margin-bottom: 8px; font-size: 15px;">
                                    {ing.capitalize()}
                                </div>
                                <div style="font-size: 14px; display: flex; align-items: center;">
                                    <span style="margin-right: 10px;">🔍</span>
                                    <span>Track this ingredient's expiration date for personalized reminders.</span>
                                    <a href="/?page=expiration" style="margin-left: 8px; color: #1976D2; text-decoration: none; font-weight: 500;">
                                        Add to tracker
                                    </a>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                # If no ingredients entered, show general expiration advice
                st.markdown(
                    """
                    <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <p style="margin: 0;">
                            <strong>Pro tip:</strong> Enter ingredients in the sidebar to see specific expiration guidelines 
                            or visit the Expiration Tracker to add items you want to monitor.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Show list of common expirations - sample of most common ingredients
                st.markdown("#### Common Ingredient Shelf Life")
                st.markdown(
                    """
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                        <div style="background-color: #f5f5f5; padding: 8px; border-radius: 5px;">
                            <strong>Meat/Poultry:</strong> 1-2 days (fridge, raw), 9-12 months (freezer)
                        </div>
                        <div style="background-color: #f5f5f5; padding: 8px; border-radius: 5px;">
                            <strong>Dairy:</strong> 5-7 days (milk), 1-4 weeks (hard cheese)
                        </div>
                        <div style="background-color: #f5f5f5; padding: 8px; border-radius: 5px;">
                            <strong>Fruits:</strong> 2-7 days (counter), 1-2 weeks (fridge)
                        </div>
                        <div style="background-color: #f5f5f5; padding: 8px; border-radius: 5px;">
                            <strong>Vegetables:</strong> 1-2 weeks (fridge), 8-12 months (freezer)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        except Exception as e:
            st.error(f"Error loading expiration data: {e}")

def display_history_page(user_prefs):
    """Display the recipe history page"""
    st.header("📚 Recipe History & Favorites")
    
    # Create tabs for liked recipes and meal history
    tab1, tab2 = st.tabs(["Liked Recipes", "Meal History"])
    
    with tab1:
        st.subheader("Your Favorite Recipes")
        
        liked_recipes = user_prefs.get_liked_recipes()
        
        if not liked_recipes:
            st.info("You haven't liked any recipes yet. When you find recipes you enjoy, click the 'Like' button to save them here!")
        else:
            st.write(f"You have liked {len(liked_recipes)} recipes:")
            
            for recipe in liked_recipes:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; 
                                   margin-bottom: 15px; border-left: 4px solid #2196F3;">
                            <span style="font-size: 18px; font-weight: bold;">{recipe['title']}</span>
                            <p style="margin-top: 8px;">Key ingredients: {', '.join(recipe['ingredients'][:5])}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    with tab2:
        st.subheader("Your Meal History")
        
        meal_history = user_prefs.get_meal_history(limit=20)
        
        if not meal_history:
            st.info("Your meal history will appear here once you've cooked some recipes.")
        else:
            st.write(f"Your last {len(meal_history)} meals:")
            
            # Group by date
            from collections import defaultdict
            from datetime import datetime
            
            meals_by_date = defaultdict(list)
            
            for meal in meal_history:
                try:
                    date = datetime.fromisoformat(meal["date"]).strftime("%Y-%m-%d")
                    meals_by_date[date].append(meal)
                except:
                    # If date parsing fails, use "Unknown Date"
                    meals_by_date["Unknown Date"].append(meal)
            
            # Display meals by date
            for date, meals in sorted(meals_by_date.items(), reverse=True):
                try:
                    # Format date nicely if it's a valid date
                    if date != "Unknown Date":
                        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d, %Y")
                    else:
                        formatted_date = date
                except:
                    formatted_date = date
                
                st.write(f"**{formatted_date}**")
                
                for meal in meals:
                    meal_type = meal.get('meal_type', 'Meal')
                    recipe_name = meal.get('recipe', 'Unknown recipe')
                    
                    st.markdown(
                        f"""
                        <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 8px;">
                            <span style="font-weight: bold;">{meal_type}:</span> {recipe_name}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()