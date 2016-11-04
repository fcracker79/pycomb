def get_type_name(type_obj):
    return type_obj.meta['name']


def get_path(ctx):
    return ctx['path'] if ctx else []


def new_ctx():
    return {'path': []}


def setup_paths_and_contexts(type_obj, ctx, name):
    path = get_path(ctx) + [name] if ctx else [name]

    return {'path': path}
