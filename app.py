from core.llm import get_llm

llm = get_llm()
print(llm.invoke("Hi my name is Tejas Singh").content)