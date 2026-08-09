def accessibility_preferences(request):
    ctx = {
        'user_colorblind_mode': False,
        'user_hearing_impaired_mode': False,
    }
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        ctx['user_colorblind_mode'] = profile.colorblind_mode
        ctx['user_hearing_impaired_mode'] = profile.hearing_impaired_mode
    return ctx
