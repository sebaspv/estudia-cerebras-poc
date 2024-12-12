from langchain_cerebras import ChatCerebras

from models.exam import Exam

model = ChatCerebras(model="llama-3.3-70b", temperature=0.2, top_p=0.9)
structured_model = model.with_structured_output(Exam)

concept = "US invasion of Mexico"
print(structured_model.invoke(f"Generate a school exam about {concept}"))
