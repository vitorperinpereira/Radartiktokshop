import urllib.request
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = {
  "dashboard.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2Y0MjdjZGQ5OTY2NTQ4NzhiNzAxYzIyMzFjMWNjZjVmEgsSBxC0korgoxsYAZIBJAoKcHJvamVjdF9pZBIWQhQxNjE4NTczMTg2Njc1MzgxMzM3Nw&filename=&opi=89354086",
  "product_detail.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzZlMjcyNGRlYzhlNTQ1MTk5YjQyY2E4ZDVjZjgyZjI0EgsSBxC0korgoxsYAZIBJAoKcHJvamVjdF9pZBIWQhQxNjE4NTczMTg2Njc1MzgxMzM3Nw&filename=&opi=89354086",
  "content_ideas.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzNmYjMyY2IwOTMxMzQ4MTk5YWJlNWQ2ODU1NTFiN2M4EgsSBxC0korgoxsYAZIBJAoKcHJvamVjdF9pZBIWQhQxNjE4NTczMTg2Njc1MzgxMzM3Nw&filename=&opi=89354086",
  "saved_products.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzRjYjAyNjA1YWI4ZjQ3ODFhMDcwMTlmN2VlMzUyZmU0EgsSBxC0korgoxsYAZIBJAoKcHJvamVjdF9pZBIWQhQxNjE4NTczMTg2Njc1MzgxMzM3Nw&filename=&opi=89354086"
}

os.makedirs(".tmp/stitch_screens", exist_ok=True)

for name, url in urls.items():
    print(f"Downloading {name}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response, open(f".tmp/stitch_screens/{name}", 'wb') as out_file:
        data = response.read()
        out_file.write(data)
print("Done")
