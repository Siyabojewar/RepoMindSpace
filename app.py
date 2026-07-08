from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Project root directory (same folder as this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
    CORS(app)

    # Configuration from .env
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MONGO_DB_NAME'] = os.getenv('MONGO_DB_NAME')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')

    # Initialize MongoDB
    client = MongoClient(app.config['MONGO_URI'])
    db = client[app.config['MONGO_DB_NAME']]
    app.config['DB'] = db

    # -- Validate Gemini API key on startup ----------------------------------
    def _validate_gemini_key():
        try:
            key = os.getenv('GEMINI_API_KEY')
            if not key:
                print('\n[GEMINI] ERROR: GEMINI_API_KEY is missing from .env!')
                return
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            model.generate_content('ping')
            print('\n[GEMINI] OK: API key is valid and working (gemini-2.5-flash)')
        except Exception as e:
            err = str(e)
            if 'referer' in err.lower() or 'blocked' in err.lower() or 'HTTP_REFERRER' in err:
                print('\n[GEMINI] ERROR: KEY RESTRICTED - This key has HTTP referrer restrictions.')
                print('   It only works from a browser, not a server backend.')
                print('   FIX: Go to https://console.cloud.google.com/apis/credentials')
                print('   Edit the key -> Application restrictions -> set to "None"')
                print('   Then save and restart the server.')
            elif 'API_KEY_INVALID' in err or 'API key not valid' in err:
                print('\n[GEMINI] ERROR: INVALID API KEY - The key in .env is malformed or revoked.')
                print('   FIX: Go to https://aistudio.google.com/app/apikey and create a new key.')
            elif '429' in err or 'quota' in err.lower() or 'ResourceExhausted' in err:
                print('\n[GEMINI] WARNING: QUOTA EXCEEDED - Free tier daily limit reached.')
                print('   FIX: Wait for quota reset, or use a key from a new Google Cloud project.')
            else:
                print(f'\n[GEMINI] WARNING: Key check failed: {err[:120]}')
    _validate_gemini_key()
    # --------------------------------------------------------------------------

    # Register API Blueprints
    from routes.auth import auth_bp
    from routes.workspace import workspace_bp
    from routes.artifact import artifact_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(workspace_bp, url_prefix='/api/workspace')
    app.register_blueprint(artifact_bp, url_prefix='/api/artifacts')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    # ── Serve static frontend ─────────────────────────────────────────────────
    @app.route('/')
    def serve_index():
        return send_from_directory(BASE_DIR, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        # API routes handle themselves — don't intercept them
        if path.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        target = os.path.join(BASE_DIR, path)
        if os.path.isfile(target):
            return send_from_directory(BASE_DIR, path)
        # Fallback to index for any unknown route
        return send_from_directory(BASE_DIR, 'index.html')
    # ─────────────────────────────────────────────────────────────────────────

    return app

# Instantiate the app globally for WSGI servers like Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
