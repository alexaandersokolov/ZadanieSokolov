import os
import hashlib
import zlib


def get_object_content(object_path):
    with open(object_path, 'rb') as f:
        compressed_content = f.read()
        # Распаковка zlib-сжатого содержимого объекта
        content = zlib.decompress(compressed_content)
        return content.decode('utf-8')


def get_commit_info(commit_hash):
    commit_path = os.path.join('.git', 'objects', commit_hash[:2], commit_hash[2:])
    commit_content = get_object_content(commit_path)
    lines = commit_content.split('\n')
    tree_hash = lines[0].split(' ')[1]
    return tree_hash


def get_latest_commit_hash():
    head_path = os.path.join('.git', 'HEAD')
    with open(head_path, 'r') as f:
        ref = f.read().strip()
        if ref.startswith('ref:'):
            # Если HEAD является символической ссылкой, следуем за ней, чтобы получить фактический хэш коммита
            ref_path = os.path.join('.git', ref[5:])
            with open(ref_path, 'r') as ref_file:
                return ref_file.read().strip()
        else:
            # Если HEAD является прямой ссылкой на хэш коммита
            return ref


def get_tree_entries(tree_hash):
    tree_path = os.path.join('.git', 'objects', tree_hash[:2], tree_hash[2:])
    tree_content = get_object_content(tree_path)
    entries = []
    for line in tree_content.split('\n'):
        if not line:
            continue
        entry_info = line.split(' ')
        mode, name, entry_hash = entry_info[0], entry_info[-1], entry_info[1]
        entries.append({'mode': mode, 'name': name, 'hash': entry_hash})
    return entries


def generate_dot_graph(commit_hash, depth=0):
    indent = '    ' * depth
    dot_graph = f'{indent}"{commit_hash}" [label="{commit_hash[:7]}"];\n'

    tree_hash = get_commit_info(commit_hash)
    entries = get_tree_entries(tree_hash)

    for entry in entries:
        dot_graph += f'{indent}"{commit_hash}" -- "{entry["hash"]}" [label="{entry["name"]}"];\n'
        if entry['mode'] == 'tree':
            dot_graph += generate_dot_graph(entry['hash'], depth + 1)

    return dot_graph


def main():
    # Получаем хеш последнего коммита
    latest_commit_hash = get_latest_commit_hash()

    dot_graph = generate_dot_graph(latest_commit_hash)

    with open('git_graph.dot', 'w') as f:
        f.write('graph git {\n')
        f.write(dot_graph)
        f.write('}\n')


if __name__ == '__main__':
    main()