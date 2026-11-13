from main import RecipeRAGSystem

if __name__ == "__main__":
    question = input("请输入你的食谱问题：").strip()

    rag = RecipeRAGSystem()
    rag.initialize_system()
    rag.build_knowledge_base()

    answer = rag.ask_question(question, stream=False)
    print(f"\n回答：\n{answer}")