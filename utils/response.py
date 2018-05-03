def remove_empty_lines(func):
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        content = response.content.decode('utf-8').split('\n')
        content = [c for c in content if c.strip(' ') != '']
        response.content = '\n'.join(content).encode('utf-8')
        return response
    return wrapper
