def tenant(request):
    school = getattr(request, 'school', None)
    branding = getattr(school, 'branding', None) if school else None
    return {
        'current_school': school,
        'school_branding': branding,
    }
