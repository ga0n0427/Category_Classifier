from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")
model.save("saved_models/KoSimCSE")
print("✅ 로컬 저장 완료!")
