import streamlit as st
import json
import os
from datetime import datetime

class UserPreferences:
    def __init__(self, storage_file="user_data/user_preferences.json"):
        """Initialize the user preferences system"""
        self.storage_dir = "user_data"
        self.storage_file = storage_file
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # Load existing data or create new
        self._load_data()
    
    def _load_data(self):
        """Load user preference data from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.user_data = json.load(f)
            else:
                self.user_data = {
                    "dietary_preferences": [],
                    "liked_recipes": [],
                    "disliked_recipes": [],
                    "ingredient_preferences": {
                        "favorites": [],
                        "dislikes": []
                    },
                    "meal_history": [],
                    "cuisine_preferences": []
                }
                self._save_data()
        except Exception as e:
            print(f"Error loading user data: {e}")
            # Initialize with empty data if file can't be loaded
            self.user_data = {
                "dietary_preferences": [],
                "liked_recipes": [],
                "disliked_recipes": [],
                "ingredient_preferences": {
                    "favorites": [],
                    "dislikes": []
                },
                "meal_history": [],
                "cuisine_preferences": []
            }
    
    def _save_data(self):
        """Save user preference data to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def update_dietary_preferences(self, preferences):
        """Update user's dietary preferences"""
        self.user_data["dietary_preferences"] = preferences
        self._save_data()
    
    def add_liked_recipe(self, recipe):
        """Add a recipe to the liked list"""
        # Store essential recipe info
        recipe_data = {
            "id": len(self.user_data["liked_recipes"]) + 1,
            "title": recipe["title"],
            "ingredients": recipe["ingredients"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.user_data["liked_recipes"].append(recipe_data)
        
        # Remove from disliked if it was there
        self.user_data["disliked_recipes"] = [
            r for r in self.user_data["disliked_recipes"] 
            if r["title"] != recipe["title"]
        ]
        
        self._save_data()
    
    def add_disliked_recipe(self, recipe):
        """Add a recipe to the disliked list"""
        # Store essential recipe info
        recipe_data = {
            "id": len(self.user_data["disliked_recipes"]) + 1,
            "title": recipe["title"],
            "ingredients": recipe["ingredients"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.user_data["disliked_recipes"].append(recipe_data)
        
        # Remove from liked if it was there
        self.user_data["liked_recipes"] = [
            r for r in self.user_data["liked_recipes"] 
            if r["title"] != recipe["title"]
        ]
        
        self._save_data()
    
    def add_favorite_ingredient(self, ingredient):
        """Add an ingredient to favorites"""
        if ingredient not in self.user_data["ingredient_preferences"]["favorites"]:
            self.user_data["ingredient_preferences"]["favorites"].append(ingredient)
            
            # Remove from dislikes if it was there
            if ingredient in self.user_data["ingredient_preferences"]["dislikes"]:
                self.user_data["ingredient_preferences"]["dislikes"].remove(ingredient)
                
            self._save_data()
    
    def add_disliked_ingredient(self, ingredient):
        """Add an ingredient to dislikes"""
        if ingredient not in self.user_data["ingredient_preferences"]["dislikes"]:
            self.user_data["ingredient_preferences"]["dislikes"].append(ingredient)
            
            # Remove from favorites if it was there
            if ingredient in self.user_data["ingredient_preferences"]["favorites"]:
                self.user_data["ingredient_preferences"]["favorites"].remove(ingredient)
                
            self._save_data()
    
    def add_meal_to_history(self, recipe_title, meal_type="dinner"):
        """Add a meal to the history"""
        meal_entry = {
            "recipe": recipe_title,
            "date": datetime.now().isoformat(),
            "meal_type": meal_type
        }
        
        self.user_data["meal_history"].append(meal_entry)
        self._save_data()
    
    def update_cuisine_preferences(self, cuisines):
        """Update cuisine preferences"""
        self.user_data["cuisine_preferences"] = cuisines
        self._save_data()
    
    def get_dietary_preferences(self):
        """Get user's dietary preferences"""
        return self.user_data["dietary_preferences"]
    
    def get_favorite_ingredients(self):
        """Get user's favorite ingredients"""
        return self.user_data["ingredient_preferences"]["favorites"]
    
    def get_disliked_ingredients(self):
        """Get user's disliked ingredients"""
        return self.user_data["ingredient_preferences"]["dislikes"]
    
    def get_liked_recipes(self):
        """Get user's liked recipes"""
        return self.user_data["liked_recipes"]
    
    def get_cuisine_preferences(self):
        """Get user's cuisine preferences"""
        return self.user_data["cuisine_preferences"]
    
    def get_meal_history(self, limit=10):
        """Get recent meal history"""
        return sorted(
            self.user_data["meal_history"], 
            key=lambda x: x["date"], 
            reverse=True
        )[:limit]
    
    def get_preference_summary(self):
        """Get a summary of user preferences for recipe generation"""
        return {
            "dietary_preferences": self.user_data["dietary_preferences"],
            "favorite_ingredients": self.user_data["ingredient_preferences"]["favorites"],
            "disliked_ingredients": self.user_data["ingredient_preferences"]["dislikes"],
            "cuisine_preferences": self.user_data["cuisine_preferences"]
        }

# Helper function to display the user preferences UI
def display_user_preferences():
    """Display the user preferences UI component"""
    st.subheader("👤 User Preferences")
    
    # Initialize user preferences
    prefs = UserPreferences()
    
    # Create tabs for different preference sections
    tab1, tab2, tab3 = st.tabs(["Dietary & Ingredients", "Cuisine Preferences", "Recipe History"])
    
    with tab1:
        # Dietary preferences
        st.write("#### Dietary Preferences")
        current_dietary = prefs.get_dietary_preferences()
        
        dietary_options = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", 
                         "Low-Carb", "Keto", "Paleo", "Pescatarian", "Nut-Free"]
        
        dietary_selections = st.multiselect(
            "Select your dietary preferences:",
            options=dietary_options,
            default=current_dietary
        )
        
        if st.button("Save Dietary Preferences"):
            prefs.update_dietary_preferences(dietary_selections)
            st.success("Dietary preferences saved!")
        
        # Ingredient preferences
        st.write("#### Ingredient Preferences")
        
        favorite_ingredients = prefs.get_favorite_ingredients()
        disliked_ingredients = prefs.get_disliked_ingredients()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Favorite Ingredients**")
            new_favorite = st.text_input("Add favorite ingredient:")
            if st.button("Add to Favorites") and new_favorite:
                prefs.add_favorite_ingredient(new_favorite.strip().lower())
                st.experimental_rerun()
                
            if favorite_ingredients:
                for ingredient in favorite_ingredients:
                    st.write(f"• {ingredient}")
            else:
                st.write("No favorite ingredients added yet.")
        
        with col2:
            st.write("**Disliked Ingredients**")
            new_disliked = st.text_input("Add disliked ingredient:")
            if st.button("Add to Dislikes") and new_disliked:
                prefs.add_disliked_ingredient(new_disliked.strip().lower())
                st.experimental_rerun()
                
            if disliked_ingredients:
                for ingredient in disliked_ingredients:
                    st.write(f"• {ingredient}")
            else:
                st.write("No disliked ingredients added yet.")
    
    with tab2:
        # Cuisine preferences
        st.write("#### Cuisine Preferences")
        current_cuisines = prefs.get_cuisine_preferences()
        
        cuisine_options = ["Italian", "Mexican", "Chinese", "Japanese", "Indian", 
                          "Thai", "Mediterranean", "French", "American", "Middle Eastern",
                          "Korean", "Vietnamese", "Greek", "Spanish"]
        
        cuisine_selections = st.multiselect(
            "Select your preferred cuisines:",
            options=cuisine_options,
            default=current_cuisines
        )
        
        cuisine_rank = {}
        
        for idx, cuisine in enumerate(cuisine_selections):
            cuisine_rank[cuisine] = st.slider(
                f"How much do you like {cuisine} cuisine?",
                1, 10, 7, help="1 = Least favorite, 10 = Most favorite"
            )
        
        if st.button("Save Cuisine Preferences"):
            # Store ranked cuisines
            ranked_cuisines = [
                {"name": cuisine, "rank": rank}
                for cuisine, rank in cuisine_rank.items()
            ]
            
            # Sort by rank
            ranked_cuisines = sorted(
                ranked_cuisines, 
                key=lambda x: x["rank"], 
                reverse=True
            )
            
            # Store just the cuisine names in order of preference
            prefs.update_cuisine_preferences([c["name"] for c in ranked_cuisines])
            st.success("Cuisine preferences saved!")
    
    with tab3:
        # Recipe history and feedback
        st.write("#### Recipe History")
        
        liked_recipes = prefs.get_liked_recipes()
        meal_history = prefs.get_meal_history()
        
        st.write("**Liked Recipes**")
        if liked_recipes:
            for recipe in liked_recipes:
                st.write(f"• {recipe['title']}")
        else:
            st.write("No liked recipes yet.")
        
        st.write("**Recent Meal History**")
        if meal_history:
            for meal in meal_history:
                try:
                    date = datetime.fromisoformat(meal["date"])
                    formatted_date = date.strftime("%b %d, %Y")
                    st.write(f"• {formatted_date} - {meal['recipe']} ({meal['meal_type']})")
                except:
                    st.write(f"• {meal['recipe']} ({meal['meal_type']})")
        else:
            st.write("No meal history recorded.")

# Function to provide personalized recipe recommendations based on user preferences
def get_personalized_recommendations(ingredients=None):
    """Get personalized recipe recommendations based on user preferences"""
    prefs = UserPreferences()
    preferences = prefs.get_preference_summary()
    
    personalization_data = {
        "dietary_restrictions": preferences["dietary_preferences"],
        "favorite_ingredients": preferences["favorite_ingredients"],
        "disliked_ingredients": preferences["disliked_ingredients"],
        "cuisine_preferences": preferences["cuisine_preferences"][:3]  # Top 3 cuisines
    }
    
    if ingredients:
        personalization_data["available_ingredients"] = ingredients
    
    return personalization_data