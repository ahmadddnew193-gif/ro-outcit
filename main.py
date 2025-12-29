import requests
import streamlit as st
import time

st.set_page_config(page_title="Ro-Metadata Deep Scanner", layout="wide")
st.title("🎫 Ro-Deep Metadata Scanner (2025 Force-Start)")

input_val = st.text_input("Enter Username or User ID", value="Builderman")

def resolve_user_id(target):
    if target.isdigit(): return target
    url = "https://users.roblox.com/v1/usernames/users"
    res = requests.post(url, json={"usernames": [target]})
    return str(res.json()['data'][0]['id']) if res.status_code == 200 and res.json()['data'] else None

def get_3d_metadata_forced(uid):
    """Triggers the 3D engine and waits for completion."""
    url = f"https://thumbnails.roblox.com/v1/users/avatar-3d?userId={uid}"
    
    # Attempt to fetch up to 5 times
    for _ in range(5):
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if data.get('state') == "Completed":
                # Success! Now fetch the actual JSON file
                json_res = requests.get(data['imageUrl'])
                return json_res.json()
            elif data.get('state') == "Pending":
                st.write("⏳ Render is Pending... Retrying in 1s...")
                time.sleep(1)
            else:
                st.error(f"Error: 3D Engine returned state '{data.get('state')}'")
                break
    return None

# --- EXECUTION ---
if st.button("EXECUTE DEEP SCAN"):
    uid = resolve_user_id(input_val)
    if uid:
        st.info(f"Scanning User ID: {uid}...")
        
        # Pull Live Image
        st.image(f"https://www.roblox.com/avatar-thumbnail/image?userId={uid}&width=420&height=420&format=png", width=250)
        
        # Pull 3D Data
        deep_data = get_3d_metadata_forced(uid)
        
        if deep_data:
            st.success("3D Metadata Successfully Extracted!")
            
            # Extract Textures (The real private data)
            textures = deep_data.get('textures', [])
            
            if textures:
                st.markdown(f"### 🛠️ Extracted Asset Textures ({len(textures)})")
                st.info("These are the raw IDs used by the 3D engine. Even private items show up here.")
                
                for tid in textures:
                    # We use the Library link because it bypasses Catalog 404s
                    st.write(f"- Texture ID: `{tid}` — [View Raw Asset](https://www.roblox.com/library/{tid})")
            else:
                st.warning("No texture IDs found in the 3D stream. The user might be wearing a simple avatar with no custom assets.")
        else:
            st.error("Deep Scan Failed: The 3D Render timed out. Try again in 10 seconds.")
    else:
        st.error("User not found.")
