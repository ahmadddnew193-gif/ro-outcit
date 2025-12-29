import requests
import streamlit as st
import time

st.set_page_config(page_title="Ro-Metadata Hybrid Scanner", layout="wide")
st.title("🎫 Ro-Metadata Deep Scanner (Hybrid Mode)")

# Dictionary for BrickColor conversion
BRICK_COLORS = {1: "White", 18: "Skin (Nougat)", 26: "Black", 1001: "Institutional White", 101: "Medium Red"}

def get_asset_info(asset_id):
    """Fetches the real name and type of a raw asset ID."""
    url = f"https://economy.roblox.com/v1/assets/{asset_id}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {"Name": data.get("Name"), "Type": data.get("AssetTypeId")}
    return {"Name": "Private/Deleted Asset", "Type": "Unknown"}

def resolve_user(target):
    if target.isdigit(): return target
    res = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [target]})
    return str(res.json()['data'][0]['id']) if res.status_code == 200 and res.json()['data'] else None

def scan_3d_stream(uid):
    """Bypass logic: Scrapes the 3D render stream for raw metadata."""
    url = f"https://thumbnails.roblox.com/v1/users/avatar-3d?userId={uid}"
    res = requests.get(url)
    if res.status_code == 200 and res.json().get('state') == "Completed":
        return requests.get(res.json()['imageUrl']).json()
    return None

# --- UI LOGIC ---
target = st.text_input("Username or ID", "Builderman")

if st.button("RUN SCAN"):
    uid = resolve_user(target)
    if uid:
        st.subheader(f"Scanning User: {uid}")
        
        # 1. Try Public Outfits First
        res = requests.get(f"https://avatar.roblox.com/v1/users/{uid}/outfits")
        outfits = res.json().get('data', [])
        
        if outfits:
            st.success(f"Found {len(outfits)} Public Outfits")
            for o in outfits:
                with st.expander(f"Outfit: {o['name']} (ID: {o['id']})"):
                    det = requests.get(f"https://avatar.roblox.com/v1/outfits/{o['id']}/details").json()
                    st.write(f"**Scaling:** {det.get('scales')}")
                    st.table(det.get('assets', []))
        else:
            # 2. PRIVATE DETECTED - Switch to Deep Metadata Extraction
            st.warning("⚠️ OUTFITS ARE PRIVATE. Initiating 3D Deep Scan...")
            data = scan_3d_stream(uid)
            if data:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 🧬 Live Physics Metadata")
                    for k, v in data.get('scales', {}).items():
                        st.write(f"- **{k.capitalize()}:** {int(v*100) if v <= 2 else int(v)}%")
                with col2:
                    st.markdown("### 🎨 Live Skin Metadata")
                    for limb, cid in data.get('bodyColors', {}).items():
                        st.write(f"- **{limb}:** {BRICK_COLORS.get(cid, cid)}")
                
                st.markdown("### 🛠️ Extracted Asset Metadata")
                textures = list(set(data.get('textures', [])))
                asset_data = []
                for tid in textures:
                    info = get_asset_info(tid)
                    asset_data.append({"Asset ID": tid, "Name": info["Name"]})
                st.table(asset_data)
