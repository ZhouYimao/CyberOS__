import requests

# 你的 GitHub 用户名和个人访问令牌
api_key = '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'


def get_github_repo_contents(owner, repo, path='', headers=None):
    if headers is None:
        headers = {'Authorization': f'token {api_key}', 'Accept': 'application/vnd.github.v3+json'}
    
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            if item.get('type') == 'file':
                # 处理文件内容
                print(item['name'])
                # 获取文件内容，需要下载链接
                if 'download_url' in item:
                    file_response = requests.get(item['download_url'], headers=headers)
                    if file_response.status_code == 200:
                        print(1)
            elif item.get('type') == 'dir':
                # 递归调用以处理子目录
                get_github_repo_contents(owner, repo, item['path'], headers)
    else:
        print(f'Failed to get repository contents: {response.status_code}')

# 使用示例
get_github_repo_contents('jina-ai', 'jina')