import os
import zlib


class GitVisualizer:
    def __init__(self):
        # Конструктор класса, здесь можно разместить инициализацию объекта, если необходимо
        # Является заглушкой
        pass

    def get_object_content(self, object_path):
        """
        Получает содержимое git-объекта из файла по указанному пути.

        :param object_path: Путь к файлу git-объекта.
        :return: Распакованное содержимое git-объекта в виде строки.
        """
        with open(object_path, 'rb') as f:
            compressed_content = f.read()
            # Распаковка zlib-сжатого содержимого объекта
            content = zlib.decompress(compressed_content)
            return content.decode('utf-8')

    def get_commit_info(self, commit_hash):
        """
        Получает информацию о коммите, основываясь на его хэше.

        :param commit_hash: Хэш коммита.
        :return: Хэш дерева, связанного с коммитом.
        """
        commit_path = os.path.join('.git', 'objects', commit_hash[:2], commit_hash[2:])
        commit_content = self.get_object_content(commit_path)
        lines = commit_content.split('\n')
        tree_hash = lines[0].split(' ')[1]
        return tree_hash

    def get_tree_entries(self, tree_hash):
        """
        Получает информацию о файлах и поддеревьях в дереве по его хэшу.

        :param tree_hash: Хэш дерева.
        :return: Список словарей с информацией о файлах и поддеревьях в дереве.
        """
        tree_path = os.path.join('.git', 'objects', tree_hash[:2], tree_hash[2:])
        tree_content = self.get_object_content(tree_path)
        entries = []
        for line in tree_content.split('\n'):
            if not line:
                continue
            entry_info = line.split(' ')
            mode, name, entry_hash = entry_info[0], entry_info[-1], entry_info[1]
            entries.append({'mode': mode, 'name': name, 'hash': entry_hash})
        return entries

    def generate_dot_graph(self, commit_hash, depth=0):
        """
        Генерирует описание графа изменений дерева проекта в формате DOT (graphviz).

        :param commit_hash: Хэш коммита, с которого начинается построение графа.
        :param depth: Глубина вложенности (используется для отступов).
        :return: Строка с описанием графа в формате DOT.
        """
        indent = '    ' * depth
        dot_graph = f'{indent}"{commit_hash}" [label="{commit_hash[:7]}"];\n'

        tree_hash = self.get_commit_info(commit_hash)
        entries = self.get_tree_entries(tree_hash)

        for entry in entries:
            dot_graph += f'{indent}"{commit_hash}" -- "{entry["hash"]}" [label="{entry["name"]}"];\n'
            if entry['mode'] == 'tree':
                dot_graph += self.generate_dot_graph(entry['hash'], depth + 1)

        return dot_graph

    def get_latest_commit_hash(self):
        """
        Получает хэш последнего коммита в репозитории.

        :return: Хэш последнего коммита.
        """
        head_path = os.path.join('.git', 'HEAD')
        try:
            with open(head_path, 'r') as f:
                ref = f.read().strip()
                if ref.startswith('ref:'):
                    ref_path = os.path.join('.git', ref[5:])
                    with open(ref_path, 'r') as ref_file:
                        return ref_file.read().strip()
                else:
                    return ref
        except FileNotFoundError:
            with open(os.path.join('.git', 'refs', 'heads', 'master'), 'r') as master_file:
                return master_file.read().strip()

    def main(self):
        # Получаем хеш последнего коммита
        latest_commit_hash = self.get_latest_commit_hash()

        # Генерируем DOT