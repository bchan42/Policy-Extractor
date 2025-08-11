from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load wildfire example policies (list of dicts)
with open("backend/atasc_gp_policies.json", "r") as f:
    example_policies_json = json.load(f)

# Format each policy dict into a string for embedding and retrieval, e.g. "Policy 1.1: ..."
example_policies = [
    f"{item['policy']}: {item['policy_text']}" for item in example_policies_json
]

# Embed the formatted policy strings
example_embeddings = embedder.encode(example_policies, convert_to_numpy=True)

# Create FAISS index
dimension = example_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(example_embeddings)


def retrieve_examples(paragraph, k=3):
    para_embedding = embedder.encode([paragraph], convert_to_numpy=True)
    distances, indices = index.search(para_embedding, k)
    return [example_policies[i] for i in indices[0]]


def query_gemini_with_rag(paragraph):

    from backend.extract import query_gemini

    examples = retrieve_examples(paragraph, k=3)
    example_text = "\n".join(examples)

    prompt = f"""You are a city planning policy expert.

            Below are real examples of policies: {example_text}
            Now, from the following page, extract ONLY policies.
            A policy can be a rule, guideline, goal, or program.
            If the policy is preceded by a number or label, include it.
            Do not include explanations, summaries, or policies not explicitly stated.
            If no policies are present, respond with: NONE.

            Page: {paragraph}"""
    
    return query_gemini(prompt)  # Your existing function
