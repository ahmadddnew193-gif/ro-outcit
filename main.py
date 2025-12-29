import requests
import streamlit as st

st.set_page_config(page_title="Ro-Outfit Deep Scanner", layout="wide")
st.title("🎫 Ro-Outfit Deep Metadata Scanner")

input_val = st.text_input("Enter Username or User ID", value="Builderman")

BRICK_COLORS = {
    1: "White", 5: "Brick yellow", 18: "Nougat (Skin)", 21: "Bright red", 
    23: "Bright blue", 24: "Bright yellow", 26: "Black", 101: "Medium red", 
    102: "Medium blue", 192: "Reddish brown", 1001: "Institutional White",
    1010: "Really blue", 1022: "Pastel light blue"
}

def resolve_user_id(target):
    if target.isdigit(): return target
    url = "https://users.roblox.com/v1/usernames/users"
    res = requests.post(url, json={"usernames": [target]})
    return str(res.json()['data'][0]['id']) if res.status_code == 200 and res.json()['data'] else None

def deep_scan_live(uid):
    """Bypasses 'Private Outfits' by pulling the LIVE avatar data."""
    url = f"https://avatar.roblox.com/v1/users/{uid}/avatar"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def reveal_ui(data, uid, is_live=False):
    st.divider()
    st.header(f"🔍 METADATA REVEAL: {'LIVE AVATAR' if is_live else data.get('name')}")
    
    # Render Logic
    if is_live:
        render_url = f"https://www.roblox.com/avatar-thumbnail/image?userId={uid}&width=420&height=420&format=png"
    else:
        render_url = f"https://www.roblox.com/outfit-thumbnail/image?userOutfitId={data.get('id')}&width=420&height=420&format=png"
    
    col_img, col1, col2 = st.columns([1.5, 2, 2])
    with col_img:
        st.image(render_url, caption="Extracted Render")
    
    with col1:
        st.subheader("🧬 Physics & Animations")
        scales = data.get('scales', {})
        for k, v in scales.items():
            st.write(f"- **{k.capitalize()}:** {int(v*100) if v <=2 else int(v)}%")
            
    with col2:
        st.subheader("🎨 Skin Tones")
        for limb, cid in data.get('bodyColors', {}).items():
            name = BRICK_COLORS.get(cid, f"ID: {cid}")
            st.write(f"- **{limb.replace('ColorId', '')}:** {name}")

    st.subheader(f"🛠️ Asset Anatomy")
    st.table([{"Type": a['assetType']['name'], "Name": a['name'], "ID": a['id']} for a in data.get('assets', [])])

# --- EXECUTION ---
if st.button("FETCH USER"):
    uid = resolve_user_id(input_val)
    if uid:
        st.session_state['target_id'] = uid
        # Standard Fetch
        res = requests.get(f"https://avatar.roblox.com/v1/users/{uid}/outfits")
        st.session_state['outfits'] = res.json().get('data', [])
        
        if not st.session_state['outfits']:
            st.warning("⚠️ Saved Outfits are PRIVATE. Use 'DEEP SCAN' to bypass.")
    else:
        st.error("User not found.")

if 'target_id' in st.session_state:
    col_a, col_b = st.columns(2)
    with col_a:
        if st.session_state.get('outfits'):
            opts = {f"{o['name']}": o['id'] for o in st.session_state['outfits']}
            choice = st.selectbox("Public Outfits", options=list(opts.keys()))
            if st.button("Reveal Outfit"):
                details = requests.get(f"https://avatar.roblox.com/v1/outfits/{opts[choice]}/details").json()
                reveal_ui(details, st.session_state['target_id'])
    
    with col_b:
        if st.button("🚀 DEEP SCAN (Bypass Privacy)"):
            live_data = deep_scan_live(st.session_state['target_id'])
            if live_data:
                reveal_ui(live_data, st.session_state['target_id'], is_live=True)
