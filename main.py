import streamlit as st
import json
from recipe_generator import RecipeGenerator
from utils import load_css, display_food_image_carousel

# Page configuration
st.set_page_config(
    page_title="AI Recipe Generator & Food Waste Reducer",
    page_icon="🍳",
    layout="wide"
)

# Load custom CSS
load_css()

def main():
    # Initialize recipe generator
    recipe_gen = RecipeGenerator()

    # Header section
    st.title("🍳 AI Recipe Generator & Food Waste Reducer")
    
    # Image carousel
    display_food_image_carousel()

    # Sidebar for input
    with st.sidebar:
        st.header("🥗 Available Ingredients")
        ingredients = st.text_area(
            "Enter your ingredients (one per line):",
            height=200,
            help="List ingredients you have available"
        )
        
        dietary_prefs = st.multiselect(
            "Dietary Preferences:",
            ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb"]
        )
        
        generate_btn = st.button("Generate Recipe 🪄")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        if generate_btn and ingredients:
            with st.spinner("Generating your recipe..."):
                ingredients_list = [i.strip() for i in ingredients.split("\n") if i.strip()]
                recipe = recipe_gen.generate_recipe(ingredients_list, dietary_prefs)
                
                # Display recipe card
                with st.container():
                    st.subheader(f"📖 {recipe['title']}")
                    st.write(f"⏱️ Prep Time: {recipe['prep_time']} minutes")
                    st.write(f"👥 Servings: {recipe['servings']}")
                    
                    st.write("### Ingredients")
                    for ingredient in recipe['ingredients']:
                        st.write(f"• {ingredient}")
                    
                    st.write("### Instructions")
                    for idx, step in enumerate(recipe['instructions'], 1):
                        st.write(f"{idx}. {step}")
                    
                    st.write("### Tips")
                    st.info(recipe['tips'])

    with col2:
        st.header("🌱 Food Waste Reduction Tips")
        if ingredients:
            with st.spinner("Generating tips..."):
                waste_tips = recipe_gen.get_waste_reduction_tips(ingredients.split("\n"))
                for tip in waste_tips:
                    st.write(f"• {tip}")
        
        st.header("🔄 Ingredient Substitutions")
        if ingredients:
            with st.spinner("Finding substitutions..."):
                substitutions = recipe_gen.get_substitutions(ingredients.split("\n"))
                for original, subs in substitutions.items():
                    st.write(f"**{original}** can be replaced with:")
                    for sub in subs:
                        st.write(f"• {sub}")

if __name__ == "__main__":
    main()
