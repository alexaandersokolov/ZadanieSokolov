import os
import zlib
import subprocess

class GitVisualizer:
    def __init__(self):
        pass

    @staticmethod
    def get_object_content(object_path):
        with open(object_path, 'rb') as f:
            compressed_content = f.read()
            content = zlib.decompress(compressed_content)
            return content.decode('utf-8').replace('\x00', '')

    def get_tree_entries(self, tree_hash):
        tree_path = os.path.join('.git', 'objects', tree_hash[:2], tree_hash[2:])
        try:
            tree_content = self.get_object_content(tree_path)
        except FileNotFoundError:
            print(f"Skipping tree {tree_hash}: no such file.")
            return []

        entries = []
        lines = tree_content.split('\n')
        for line in lines:
            if not line:
                continue
            entry_info = line.split(' ')
            if len(entry_info) != 3:
                continue
            mode, name, entry_hash = entry_info
            entries.append({'mode': mode, 'name': name, 'hash': entry_hash})

        return entries

    def get_all_commits(self):
        """
        Получает список хэшей всех коммитов в проекте.

        :return: Список хэшей коммитов.
        """
        log_output = subprocess.check_output(['git', 'log', '--pretty=format:%H'])
        return log_output.decode('utf-8').split('\n')

    def generate_dot_graph_for_all_commits(self):
        """
        Генерирует описание графа изменений всех коммитов в проекте в формате DOT (graphviz).

        :return: Строка с описанием графа в формате DOT.
        """
        all_commits = self.get_all_commits()

        indent = '    '
        dot_graph = 'graph git {\n'

        for commit_hash in all_commits:
            dot_graph += f'{indent}"{commit_hash}" [label="{commit_hash[:7]}"];\n'

        for i in range(len(all_commits) - 1):
            current_commit = all_commits[i]
            next_commit = all_commits[i + 1]
            dot_graph += f'{indent}"{current_commit}" -- "{next_commit}" [label=""];\n'

        dot_graph += '}\n'

        with open('git_graph_all_commits.dot', 'w') as f:
            f.write(dot_graph)

        print(f"DOT graph for all commits has been written to 'git_graph_all_commits.dot'")

if __name__ == '__main__':
    git_visualizer = GitVisualizer()
    git_visualizer.generate_dot_graph_for_all_commits()
