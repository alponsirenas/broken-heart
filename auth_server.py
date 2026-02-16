"""Flask OAuth callback server for Whoop authentication."""
from flask import Flask, request, redirect, session, jsonify
from whoop_auth import WhoopAuth
import config

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

auth = WhoopAuth()


@app.route('/')
def index():
    """Homepage with authentication status."""
    if auth.is_authenticated():
        return '''
        <h1>Whoop Health Data Comparison</h1>
        <p>✅ Authenticated with Whoop</p>
        <p><a href="/logout">Logout</a></p>
        <p><a href="/test">Test API Connection</a></p>
        '''
    else:
        return '''
        <h1>Whoop Health Data Comparison</h1>
        <p>❌ Not authenticated</p>
        <p><a href="/login">Login with Whoop</a></p>
        '''


@app.route('/login')
def login():
    """Redirect to Whoop authorization page."""
    auth_url, state = auth.generate_auth_url()
    session['oauth_state'] = state
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle OAuth callback from Whoop."""
    # Verify state for CSRF protection
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return 'Error: Invalid state parameter', 400
    
    # Check for errors
    error = request.args.get('error')
    if error:
        return f'Error: {error}', 400
    
    # Exchange code for token
    code = request.args.get('code')
    if not code:
        return 'Error: No authorization code received', 400
    
    try:
        auth.exchange_code_for_token(code)
        return redirect('/')
    except Exception as e:
        return f'Error exchanging code for token: {str(e)}', 500


@app.route('/logout')
def logout():
    """Revoke access and logout."""
    auth.revoke_access()
    session.clear()
    return redirect('/')


@app.route('/test')
def test_api():
    """Test API connection by fetching user profile."""
    if not auth.is_authenticated():
        return redirect('/login')
    
    try:
        from whoop_client import WhoopClient
        client = WhoopClient(auth)
        profile = client.get_user_profile()
        return jsonify({
            'status': 'success',
            'profile': profile
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("Starting Whoop OAuth server...")
    print(f"Visit http://localhost:5000 to authenticate")
    app.run(debug=True, port=5000)
