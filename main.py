import ollama
import time

inicio = time.time()

rpt= ollama.chat(
    model='llava:7b',
    messages=[
        {
            'role':'user',
            'content': 'What do you think of this web interface of a trucking page? What recommendations would you give for the UI/UX designer, be detailed',
            'images':['captura2.png']
        }
    ]
)

fin= time.time()
print(f"{(fin-inicio)/60} segundos")

print(rpt['message']['content'])