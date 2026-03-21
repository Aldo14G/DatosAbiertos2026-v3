import urllib.request
import os
import json

screens = [
    {"id": "9513a0d3d8374142b0b72c3328328812", "title": "Rendimiento por Categoría", 
     "image": "https://lh3.googleusercontent.com/aida/ADBb0ujATYqfuZGhwo7vmZFi64wqrJZrr6hnMx0EdfuueMXT9KGwAbB6FK0Az_O5jbQunhXUALTvGAz7FD94IasLRc6BvobKTpf-UDBKmfAae6YdEvuYQXRDdaAV-jdlOhFj1IzwechTTtpNZdwtzm83kBQMp-4bFw2s1VEjaSbI2pGYXYM2wKHIRDJM2l6G08ryecuWfWWXOLowVNx2ukgr5E5yMyoks00H5VLlh1QhvdXkaG9p0EI8BSRmlzM", 
     "html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzczY2IyYThmYzFjMzQxMTY4NjFhOTdjMGE0Mjk0YmIzEgsSBxDEqJituxQYAZIBIwoKcHJvamVjdF9pZBIVQhMzMDUwMjQ5NTc4NjgwMDA2MjA2&filename=&opi=89354086"},
    {"id": "0ae87685aa2341aba4a06bfe35b98983", "title": "Resumen General", 
     "image": "https://lh3.googleusercontent.com/aida/ADBb0ugCKCs8orPKcMu2J_lxJ2fNqUbAhgV3BL5DubdmqCvKD8-hpwqd6q3-IRmnFrU7iQ1lbu9pdChXiwdteWAeMIbjZ9IeQnbQtMnROFWvqB09WHUnXnIKQEFsOj21DDhS4Yv7keICAfbFbRddXrn3N5ZpRYpS-H68PO7HWlahi_chVI15xh9hZJn5mrbqP1XDVKxJncUFZuwvFqPDRwX74t1UEHUf-mUZC_6Cym-JCIKWKhsC1TnpAXu2pQ", 
     "html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzkzNGY1ZDY3NWM0MjRhMjRhYmQ3NjNlMTE5NjdhNGYwEgsSBxDEqJituxQYAZIBIwoKcHJvamVjdF9pZBIVQhMzMDUwMjQ5NTc4NjgwMDA2MjA2&filename=&opi=89354086"},
    {"id": "6b80ee275e27438883c7773e48a0be98", "title": "Explorador de Datasets", 
     "image": "https://lh3.googleusercontent.com/aida/ADBb0ui8IHiF1KANwuo71ipSiyJ86wBC55DJwx9Zbp_E3eBCkyBU3TEhjOBN2UOowkxL3D5GY4CXYz1lDRLjmj7CAsRvQhHPpJzf5i-EQOmrSz4ZXzTyBnwAj_BLdQ7nAGo5lnDk7UzoWv3Y7TQlnrF3SjFROlaAYpcegGph__Pqn5NJQZW5zyrODEh9Iy7shTvJ3DrEYq-Tk2XsUFhB5_DDDwlBnubEBmlXFcBYNelqjPy5OmBLy-R8igM7qQ", 
     "html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzJmMzRkYmE3M2QyMjQyOTJhMDE1M2Y2MDk1OGI5YzA3EgsSBxDEqJituxQYAZIBIwoKcHJvamVjdF9pZBIVQhMzMDUwMjQ5NTc4NjgwMDA2MjA2&filename=&opi=89354086"},
    {"id": "7c30516f9b7b418787cb873ef84b8342", "title": "Evolución Histórica", 
     "image": "https://lh3.googleusercontent.com/aida/ADBb0uh-Smlkj6rKWESoViHi5Ovkbers4S7xKJEQzFdZPNiz2MoLAZd_5td8GbVuviSdKD9A_6IYOMtBOyLIywUeXYYFRoZbuanSl4clq3qEm3u8FmVpo0g2Y8eduaGHQ1lk4UBOdKzNB9PluU7DmNgxINqpOwZt40XZc15uAlurqofH-SurKw32R91_eY10UuvnwtHRdLJ8tgyzLlYdTyR1D5WzpYnUNmh_11iwzYPsh9qSnZtBSNM-E2zMwLw", 
     "html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzIxYjNhNzBmZGNjOTRiNzdiMTg5ZDQ3M2ZmODc0MmQ5EgsSBxDEqJituxQYAZIBIwoKcHJvamVjdF9pZBIVQhMzMDUwMjQ5NTc4NjgwMDA2MjA2&filename=&opi=89354086"},
    {"id": "8b2ef5d7dc174aa5812f7ca097044540", "title": "Monitoreo de Alertas", 
     "image": "https://lh3.googleusercontent.com/aida/ADBb0ujTAjzvTvtLYlEM3tMdOZPWepihINZ8_HnSHGLEk8aWn9syzH2D7EtzGNqyWuDHac8GpuUFDg7Mij-iD4i-ViYq5FkNu6SM7hD6oJINdv_t7UuZBjf5HDVVJPSASi06l300p08j0FIrVjtOLWRxAuOa9xdYn1FuG46LFgEjKYn7I3Z1W0h1ntcbEDnr6bKhllnFgaEGoEpM7zslFlgpNdRv9bXft0fm5giJfFyJ3MDNJC2bfxWkmOgg2SU", 
     "html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzg0M2RiOTgzZGViNzQ4NGJhZGYzYTljZWEzM2ZhYjYzEgsSBxDEqJituxQYAZIBIwoKcHJvamVjdF9pZBIVQhMzMDUwMjQ5NTc4NjgwMDA2MjA2&filename=&opi=89354086"},
    {"id": "0b961b3fcfa840798f4099c637a24dc2", "title": "Análisis de Data Science", 
     "image": "https://lh3.googleusercontent.com/aida/ADBb0ui6Mj_cMHpx6UNf7cLu0DrMKNEL4A7-93goN5V6D1NceaU9Jk2zpYfFDwNTkyYoxP4Mu63G2LqLb1T7jmArskfl2hNhLk6U1O5C_fIQxgEW2WWh_DI9_D6yfOIwsRn8qnnoRFUNs_OcF_iq0nAptxhelyXs_-YeUgQN9es71_FHz8n8aQh7JsyNiA64SUCWBUqrBdkDa3yPs4DCRO_qbIWWKu2YsiPEyGPUtw05UYaiieYsfG74yP5xeQ", 
     "html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sX2U0ZmJjNDNhOWMwOTRjNWRiZDM3Y2U3M2M0ZTdlYjYyEgsSBxDEqJituxQYAZIBIwoKcHJvamVjdF9pZBIVQhMzMDUwMjQ5NTc4NjgwMDA2MjA2&filename=&opi=89354086"}
]

os.makedirs("stitch_screens", exist_ok=True)

for s in screens:
    title_safe = "".join([c if c.isalnum() else "_" for c in s["title"]])
    # Prepend LightMode to distinguish them easily from the dark mode ones
    img_path = f"stitch_screens/LightMode_{title_safe}_{s['id']}.png"
    html_path = f"stitch_screens/LightMode_{title_safe}_{s['id']}.html"
    
    print(f"Downloading LightMode {title_safe}...")
    try:
        urllib.request.urlretrieve(s["image"], img_path)
        urllib.request.urlretrieve(s["html"], html_path)
    except Exception as e:
        print(f"Failed {title_safe}: {e}")

print("Done downloading all 6 Light Mode screens.")
