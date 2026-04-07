import os
import re

directory = r'frontend\src'

replacements = [
    (r'\bbg-gray-(?:50|100|200)\b', 'bg-outline/30'),
    (r'\bdark:bg-gray-(?:700|800|900)\b', 'dark:bg-surface-dark'),
    (r'\bhover:bg-gray-(?:50|100|200)\b', 'hover:bg-outline/50'),
    (r'\bdark:hover:bg-gray-(?:700|800|900)\b', 'dark:hover:bg-surface-dark/80'),
    (r'\Bbg-zinc-800\b', 'bg-surface-dark'),
    (r'\Bbg-zinc-900\b', 'bg-background-dark'),

    (r'\bborder-gray-(?:100|200)\b', 'border-outline'),
    (r'\bdark:border-gray-(?:700|800)\b', 'dark:border-outline/20'),
    (r'\bhover:border-gray-(?:200|300)\b', 'hover:border-outline'),
    (r'\bdark:hover:border-gray-(?:600|700)\b', 'dark:hover:border-outline/40'),

    (r'\btext-gray-(?:300|400|500)\b', 'text-muted'),
    (r'\bdark:text-gray-(?:200|300)\b', 'dark:text-white/90'),
    (r'\btext-gray-(?:700|800|900)\b', 'text-text-main'),
    (r'\btext-zinc-300\b', 'text-muted'),
    
    (r'stroke-\[\#00E676\]', 'stroke-success'),
    (r'stroke-\[\#FFD54F\]', 'stroke-warning'),
    (r'stroke-\[\#FF0050\]', 'stroke-primary'),
    (r'stroke="\#f0f0f0"', 'stroke-outline'),
    (r'stroke="\#00E676"', 'stroke-success'),
    (r'text-\[\#00b4bd\]', 'text-accent'),
    (r'color:\s*[\'\"]#00C853[\'\"]', "color: '#00E676'"),
    (r'color:\s*[\'\"]#FFD54F[\'\"]', "color: 'var(--color-warning)'"),
]

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.jsx'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            orig_content = content
            for pat, repl in replacements:
                content = re.sub(pat, repl, content)
            
            if content != orig_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Refactored {file}')
print('Done!')
