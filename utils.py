import streamlit as st

def load_css():
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_food_image_carousel():
    # Create image carousel using pre-fetched stock photos
    images = [
        {
            "url": "https://images.unsplash.com/photo-1601001815853-3835274403b3",
            "caption": "Fresh Ingredients"
        },
        {
            "url": "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e",
            "caption": "Colorful Vegetables"
        },
        {
            "url": "https://images.unsplash.com/photo-1479832793815-b9be4c77023e",
            "caption": "Prepared Meal"
        },
        {
            "url": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae",
            "caption": "Modern Kitchen"
        }
    ]

    # Display images in a horizontal scroll container
    st.markdown(
        """
        <div class="image-carousel">
            {}
        </div>
        """.format(
            "".join(
                f"""
                <div class="carousel-item">
                    <img src="{img['url']}" alt="{img['caption']}">
                    <p class="caption">{img['caption']}</p>
                </div>
                """
                for img in images
            )
        ),
        unsafe_allow_html=True
    )
