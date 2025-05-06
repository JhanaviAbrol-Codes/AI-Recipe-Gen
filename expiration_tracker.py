import streamlit as st
import datetime
import json
import os

class ExpirationTracker:
    def __init__(self, storage_file="user_data/expiration_data.json"):
        """Initialize the expiration date tracker"""
        self.storage_dir = "user_data"
        self.storage_file = storage_file
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # Load existing data or create new
        self._load_data()
    
    def _load_data(self):
        """Load expiration data from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.expiration_data = json.load(f)
            else:
                self.expiration_data = {
                    "items": [],
                    "notifications": []
                }
                self._save_data()
        except Exception as e:
            print(f"Error loading expiration data: {e}")
            # Initialize with empty data if file can't be loaded
            self.expiration_data = {
                "items": [],
                "notifications": []
            }
    
    def _save_data(self):
        """Save expiration data to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.expiration_data, f, indent=2)
        except Exception as e:
            print(f"Error saving expiration data: {e}")
    
    def add_item(self, name, expiry_date, quantity="", category=""):
        """Add a new food item with expiration date"""
        if not name or not expiry_date:
            return False
        
        # Format as ISO date for storage
        if isinstance(expiry_date, str):
            try:
                # Convert string to datetime object
                date_obj = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
                expiry_date = date_obj.isoformat()
            except ValueError:
                # If date format is not correct, return false
                return False
        elif isinstance(expiry_date, datetime.date):
            expiry_date = expiry_date.isoformat()
            
        # Create new item
        new_item = {
            "id": len(self.expiration_data["items"]) + 1,
            "name": name,
            "expiry_date": expiry_date,
            "quantity": quantity,
            "category": category,
            "added_date": datetime.date.today().isoformat()
        }
        
        self.expiration_data["items"].append(new_item)
        self._save_data()
        return True
    
    def remove_item(self, item_id):
        """Remove an item by ID"""
        self.expiration_data["items"] = [
            item for item in self.expiration_data["items"] 
            if item["id"] != item_id
        ]
        self._save_data()
    
    def update_item(self, item_id, **kwargs):
        """Update an item's details"""
        for item in self.expiration_data["items"]:
            if item["id"] == item_id:
                for key, value in kwargs.items():
                    if key in item:
                        item[key] = value
                self._save_data()
                return True
        return False
    
    def get_all_items(self):
        """Return all tracked items"""
        return self.expiration_data["items"]
    
    def get_expiring_soon(self, days=7):
        """Return items expiring within specified days"""
        today = datetime.date.today()
        expiring_soon = []
        
        for item in self.expiration_data["items"]:
            try:
                expiry = datetime.date.fromisoformat(item["expiry_date"])
                days_left = (expiry - today).days
                
                if 0 <= days_left <= days:
                    item_with_days = item.copy()
                    item_with_days["days_left"] = days_left
                    expiring_soon.append(item_with_days)
            except Exception as e:
                print(f"Error processing expiry date for {item['name']}: {e}")
                
        return sorted(expiring_soon, key=lambda x: x["days_left"])
    
    def get_expired(self):
        """Return items that have already expired"""
        today = datetime.date.today()
        expired = []
        
        for item in self.expiration_data["items"]:
            try:
                expiry = datetime.date.fromisoformat(item["expiry_date"])
                days_expired = (today - expiry).days
                
                if days_expired > 0:
                    item_with_days = item.copy()
                    item_with_days["days_expired"] = days_expired
                    expired.append(item_with_days)
            except Exception as e:
                print(f"Error processing expiry date for {item['name']}: {e}")
                
        return sorted(expired, key=lambda x: x["days_expired"], reverse=True)

# Helper function to display the expiration tracker UI
def display_expiration_tracker():
    """Display the expiration date tracker UI component"""
    st.subheader("🗓️ Expiration Date Tracker")
    
    # Initialize tracker
    tracker = ExpirationTracker()
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Add Items", "Expiring Soon", "All Items"])
    
    with tab1:
        # Form for adding new items
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("Item Name")
                quantity = st.text_input("Quantity (optional)")
            
            with col2:
                expiry_date = st.date_input("Expiration Date", min_value=datetime.date.today())
                category = st.selectbox(
                    "Category", 
                    ["Fruits", "Vegetables", "Dairy", "Meat", "Seafood", "Grains", "Frozen", "Other"]
                )
            
            submit_button = st.form_submit_button("Add Item")
            
            if submit_button:
                if item_name and expiry_date:
                    success = tracker.add_item(item_name, expiry_date, quantity, category)
                    if success:
                        st.success(f"Added {item_name} to expiration tracker!")
                    else:
                        st.error("Error adding item. Please check the information.")
                else:
                    st.warning("Please enter at least an item name and expiration date.")
    
    with tab2:
        # Display items expiring soon
        expiring_soon = tracker.get_expiring_soon(days=7)
        expired = tracker.get_expired()
        
        if expired:
            st.error(f"⚠️ {len(expired)} items have expired!")
            
            with st.expander("Show Expired Items"):
                for item in expired:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{item['name']}** ({item['quantity']})")
                        st.caption(f"Category: {item['category']}")
                    with col2:
                        st.write(f"**Expired {item['days_expired']} days ago!**")
                    with col3:
                        if st.button("Remove", key=f"remove_expired_{item['id']}"):
                            tracker.remove_item(item['id'])
                            st.rerun()
                    st.divider()
        
        if expiring_soon:
            st.warning(f"🔔 {len(expiring_soon)} items expiring within 7 days")
            
            for item in expiring_soon:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{item['name']}** ({item['quantity']})")
                    st.caption(f"Category: {item['category']}")
                with col2:
                    days_text = "Today!" if item['days_left'] == 0 else f"in {item['days_left']} days"
                    st.write(f"**Expires {days_text}**")
                with col3:
                    if st.button("Used", key=f"remove_{item['id']}"):
                        tracker.remove_item(item['id'])
                        st.rerun()
                st.divider()
        
        if not expiring_soon and not expired:
            st.info("No items expiring soon. 🎉")
    
    with tab3:
        # Display all items with sorting options
        all_items = tracker.get_all_items()
        
        if all_items:
            sort_option = st.selectbox(
                "Sort by", 
                ["Expiry Date (Soonest)", "Expiry Date (Latest)", "Name (A-Z)", "Category"]
            )
            
            if sort_option == "Expiry Date (Soonest)":
                all_items = sorted(all_items, key=lambda x: x["expiry_date"])
            elif sort_option == "Expiry Date (Latest)":
                all_items = sorted(all_items, key=lambda x: x["expiry_date"], reverse=True)
            elif sort_option == "Name (A-Z)":
                all_items = sorted(all_items, key=lambda x: x["name"].lower())
            elif sort_option == "Category":
                all_items = sorted(all_items, key=lambda x: x["category"])
            
            # Display items in a table
            st.write(f"📋 Total items: {len(all_items)}")
            
            for item in all_items:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                try:
                    expiry = datetime.date.fromisoformat(item["expiry_date"])
                    today = datetime.date.today()
                    days_left = (expiry - today).days
                    
                    with col1:
                        st.write(f"**{item['name']}** ({item['quantity']})")
                        st.caption(f"Category: {item['category']}")
                    
                    with col2:
                        if days_left < 0:
                            st.error(f"Expired {abs(days_left)} days ago!")
                        elif days_left == 0:
                            st.warning("Expires today!")
                        else:
                            st.write(f"Expires in {days_left} days")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_all_{item['id']}"):
                            tracker.remove_item(item['id'])
                            st.rerun()
                except Exception as e:
                    st.error(f"Error processing item: {e}")
                
                st.divider()
        else:
            st.info("No items tracked yet. Add some items to get started!")