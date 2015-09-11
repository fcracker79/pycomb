def _get_type_name(type):
    return type.meta['name']

def _get_path(ctx):
    return ctx['path'] if ctx else []

def _new_ctx():
    return {'path': []}

def _setup_paths_and_contexts(type, ctx, name):
    path = _get_path(ctx) + [name] if ctx else [name]

    return {'path': path}