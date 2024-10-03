from functools import wraps
from flask import redirect, render_template, request, session
import json

def configure_routes(app):
    # Decorators
    def login_required(f):
        """This decorator ensures that a user is logged in before accessing certain routes.
        """
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                return redirect('/user/login')
    
        return wrap
    
    # Module Routes
    from ..user import routes
    
        
    @app.route('/')
    @login_required
    def index():
        """The home route which requires the user to be logged in and renders the 'home.html' template.

        Returns:
            str: Rendered HTML template for the home page.
        """
        return render_template('home.html')
    
    @app.route('/privacy-policy')
    def privacy_policy():
        """The privacy policy route which renders the 'privacy_policy.html' template.

        Returns:
            str: Rendered HTML template for the privacy policy page.
        """
        return render_template('privacy_policy.html')
 