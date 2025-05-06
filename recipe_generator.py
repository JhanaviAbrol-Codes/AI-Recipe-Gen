import os
from openai import OpenAI
import json

class RecipeGenerator:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate_recipe(self, ingredients, dietary_prefs):
        prompt = f"""Generate a recipe using these ingredients: {', '.join(ingredients)}
        Dietary preferences: {', '.join(dietary_prefs) if dietary_prefs else 'None'}
        
        Respond with a JSON object containing:
        - title: recipe name
        - prep_time: in minutes
        - servings: number of servings
        - ingredients: list of ingredients with measurements
        - instructions: list of step-by-step instructions
        - tips: cooking and storage tips
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    def get_waste_reduction_tips(self, ingredients):
        prompt = f"""Generate specific food waste reduction tips for these ingredients: 
        {', '.join(ingredients)}
        
        Respond with a JSON array of tips."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)["tips"]

    def get_substitutions(self, ingredients):
        prompt = f"""Suggest common substitutions for these ingredients: 
        {', '.join(ingredients)}
        
        Respond with a JSON object where keys are original ingredients and values are arrays of possible substitutions."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
