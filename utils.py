import streamlit as st

def load_css():
    st.markdown("""
    <style>
        .image-carousel {
            display: flex;
            overflow-x: auto;
            gap: 1rem;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        .carousel-item {
            flex: 0 0 auto;
            width: 300px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .carousel-item img {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        .caption {
            padding: 0.5rem;
            text-align: center;
            background-color: rgba(255, 255, 255, 0.9);
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)

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
        }
    ]

    # Use columns for a more native Streamlit layout
    cols = st.columns(len(images))
    for idx, (col, img) in enumerate(zip(cols, images)):
        with col:
            st.image(img["url"], caption=img["caption"], use_container_width=True)