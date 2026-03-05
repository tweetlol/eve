
def write_to_file(filename: str, content: str):
    filepath = f"/home/fj/eve/state_outputs/{filename}"
    with open(filepath, 'w') as f:
        f.write(content)
