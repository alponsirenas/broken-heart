"""Streamlit-integrated OAuth handler (no separate Flask server needed)."""
import streamlit as st
from whoop_auth import WhoopAuth
import config


def handle_oauth_flow():
    """Handle OAuth flow within Streamlit using query parameters."""
    auth = WhoopAuth()
    
    # Check for OAuth callback
    query_params = st.query_params
    
    if 'code' in query_params:
        # OAuth callback - exchange code for token
        code = query_params['code']
        state = query_params.get('state')
        
        # Verify state if stored in session
        if 'oauth_state' in st.session_state:
            if state != st.session_state['oauth_state']:
                st.error("Invalid OAuth state. Please try again.")
                return False
        
        try:
            auth.exchange_code_for_token(code)
            st.success("✓ Successfully authenticated with Whoop!")
            # Clear query params
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return False
    
    return auth.is_authenticated()


def show_login_button():
    """Display login button that redirects to Whoop OAuth."""
    auth = WhoopAuth()
    auth_url, state = auth.generate_auth_url()
    
    # Store state in session
    st.session_state['oauth_state'] = state
    
    st.markdown(f"""
    <a href="{auth_url}" target="_self">
        <button style="
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        ">
            🔐 Login with Whoop
        </button>
    </a>
    """, unsafe_allow_html=True)


def show_logout_button():
    """Display logout button."""
    if st.button("🚪 Logout"):
        auth = WhoopAuth()
        auth.revoke_access()
        st.session_state.clear()
        st.rerun()
