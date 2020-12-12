from flask import render_template, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user, login_required
import msal
import uuid
from config import Config
from FlaskExercise import app
from FlaskExercise.models import User


@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    session['state'] = str(uuid.uuid4())
    # Note: Below will return None as an auth_url until you implement the function
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session['state'])
    return render_template('login.html', title='Sign In', auth_url=auth_url)


@app.route('/logout')
def logout():
    logout_user() # Log out of Flask session
    if session.get('user'): # Used MS Login
        # Wipe out user and its token cache from session
        session.clear()
        return redirect(
        Config.AUTHORITY + '/oauth2/v2.0/logout' + '?post_logout_redirect_uri=' + url_for('login', _external=True))
        # TODO: Also logout from your tenant's web session
        #   And make sure to redirect from there back to the login page
  

    return redirect(url_for('https://login.live.com/oauth20_desktop.srf'))


@app.route(Config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get('state') != session.get('state'):
        return redirect(url_for('home'))  # Failed, go back home
    if 'error' in request.args:  # Authentication/Authorization failure
        return render_template('auth_error.html', result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        # TODO: Acquire a token by authorization code from an MSAL app
        #  And replace the error dictionary
        #result = {'0.ASgA-YHkPZGkd0Ce112vm8XmQqA_sD0iYpJNhMb1RQQV3UAoAPs.AQABAAIAAAB2UyzwtQEKR7-rWbgdcBZIaACG0RNVfZwFOAMFpbQjFLkMNUYLYeWmkilnnZo7qvhEnaV7AFPaoDaSNZaYWEcW7kP4Za-COiVCJ9m33_phJWBOGF-H3-bAduAfM3PPKa10yOD55uYrjA9C4DjWuSThtpGk5x-5JI302_FvtX_G3042uKcBzdAP6aJnL40AdN7hcT45x_kX1W04vW12nNkSZgMN2z1d9di5fIC95thVOMuqBQhYwS6q6bk0wfxMwNywQczxZ_Pohq_0HXfK2zhwdejCDKY2OOfXp1_C8wm_0bTcr-PPDmlsp0xQpPgnzBkkb6Aox_VQqVwFXkGUlsJ_LtVM3xXMjq81A-eYj6-WjI49pwyeijcov3tyrUx3bc48cC_Ph_ERMFQThMlSj9dQrqLwJn2j_jW7kqoPqnVgqHq7MdGIOz3jctZTXpg0y5JzP-e3nCFriMD1b1vsDkfJ0zf2yggLBrHRJTupoRTER8jkh5ZfWGdKzuN_uf3Ld2a32g0qzkfjAx1dsGh6Oijj-amc1SxqNQJS4Y4OcBuS2P4VkLHHLpjeAdAuhqKnyB0R8_wYT-5isJM3DTLjDa0SRbhNAAF85k3DQaA8gpPMIPyq8rpHy767js9DkWdwz6L1LyUDsb3_B_aZsQXM3c-nJepV9uwEh_l4AhIe3sm6Y8QXzmVJemgFkRI63iOUt-5C4UyrqHYlkx0wpsXAQhRruFQchhZCuOVkcs_Mzy53CTHv56J-6WDN4o_X3cExhrZ60ekGbiG5QQe5bA27YJ8J0sJyE-fHYQgg_QTzcEAI5u6lY7Y8_vsacrCBrrrUFSH5C6apgonyHYlGfgADU8U0MFaYsXf6rZRqvcvxniSsRiRb7UpjCzjfTdwUfWVLIYraPLlrnsmDFJ3i_6GQZ3rH_YHPZcW5HO5XUby6SSZ0lE3-WWD0HHbmqlFL5MKCFSz2IpBMYIuOdRGjORRLiQPNqowK1oG7_6HVGHl3UM8uSYH-PA6byAW_0QTm3nh33HGwB0_hmxboLCGD8Q8wxTGjhrftzXWaisI0N12lMyNNnB50CdTGr17GAC_g4jdAR2FWRSyD2sM8rf-LDO4uXdwEmFMpBHm26vFJm2muqqEUkqelHvaTHQDpR7WKBM6Fbpc211JnKHNEJoCk5omM1JH6dUY8K8IFjUyoWNcpaJ_C3-aTIxHpYs-L0LEjxKy4fiyMnvTERdUA8kqCKsoHK34_ve9e04VV11sVKjQkiDxFJzL-uNU69_A1H4n3t7NkmjksH3fknjT-McfEzw-BULbpIAA&state=4986ea9e-2360-4238-94a6-83c83601699c&session_state=26acfbab-4453-40a4-a07d-ec3a13171e2f': 'Not Implemented', 'error_description': 'Function not implemented.'}
        result=_build_msal_app(cache=cache).acquire_token_by_authorization_code(request.args['code'],
        scopes=Config.SCOPE,
        redirect_uri=url_for('authorized',_external=True,_scehme='https'))
        #redirect_uri=url_for('authorized',_external=True))
        
        if 'error' in result:
            return render_template('auth_error.html', result=result)
        session['user'] = result.get('id_token_claims')
        # Note: In a real app, use the appropriate user's DB ID below,
        #   but here, we'll just log in with a fake user zero
        #   This is so flask login functionality works appropriately.
        user = User(0)
        login_user(user)
        _save_cache(cache)

    return redirect(url_for('home'))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get('token_cache'):
        cache.deserialize(session['token_cache'])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session['token_cache'] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
     return msal.ConfidentialClientApplication(
     Config.CLIENT_ID, authority=authority or Config.AUTHORITY,
     client_credential=Config.CLIENT_SECRET, token_cache=cache)
    
def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
    scopes or [],
    state=state or str(uuid.uuid4()),
    redirect_uri=url_for('authorized', _external=True, _scheme='https'))
    #redirect_uri=url_for('authorized', _external=True))
    
