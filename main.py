# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import pandas as pd
import spacy
import numpy as np

# Initialize FastAPI app
app = FastAPI()

# Define allowed origins
origins = [
    "http://localhost:5173",  # Add your frontend URL here
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Initialize models
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")

# Load preprocessed dataset
df_cleaned = pd.read_csv('processed_data_with_embeddings.csv')

# Function to generate embeddings
def generate_embeddings_batch(texts):
    return sentence_model.encode(texts, convert_to_numpy=True)

# Function to preprocess query
def preprocess_query(query: str):
    return query.lower().strip()

# Function to extract factors and context using NER
def extract_factors_and_context(query: str):
    factors = {
        'geographic': None,
        'therapeutic': None,
        'dataset': None
    }
    doc = nlp(query)
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            factors['geographic'] = ent.text
        elif ent.label_ in ['ORG', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
            factors['therapeutic'] = ent.text
    factors['dataset'] = query
    return factors

# Function to search datasets based on factors
def search_datasets(query, df_cleaned, factors):
    query_embedding = generate_embeddings_batch([query])[0]

    # Prepare the relevant columns based on extracted factors
    relevant_columns = []
    if factors['geographic']:
        relevant_columns.append('Geographic coverage')
    if factors['therapeutic']:
        relevant_columns.append('Therapeutic coverage')
    if factors['dataset']:
        relevant_columns.append('Dataset Category')

    # Combine relevant columns into a single string
    combined_coverage = df_cleaned[relevant_columns].fillna('').agg(' '.join, axis=1)
    column_embeddings = generate_embeddings_batch(combined_coverage.tolist())

    # Calculate similarities
    similarities = np.inner(query_embedding, column_embeddings)
    df_cleaned['similarity'] = similarities

    # Apply penalty for "TBD" values in certain columns
    penalty_columns = ['Dataset Category', 'Vendor', 'Dataset Name', 'Description', 'Therapeutic coverage', 'Geographic coverage']
    
    def apply_penalty(row):
        penalty = 0
        for column in penalty_columns:
            if 'TBD' in str(row.get(column, '')):
                penalty += 0.1
        return penalty

    df_cleaned['penalty'] = df_cleaned.apply(apply_penalty, axis=1)
    df_cleaned['penalized_similarity'] = df_cleaned['similarity'] - df_cleaned['penalty']

    # Filtering by geographic and category masks
    geo_mask = df_cleaned['Geographic coverage'].str.contains(factors['geographic'], case=False, na=False) if factors['geographic'] else np.ones(len(df_cleaned), dtype=bool)
    category_mask = df_cleaned['Dataset Category'].str.contains(factors['dataset'], case=False, na=False) if factors['dataset'] else np.ones(len(df_cleaned), dtype=bool)

    filtered_by_geo_and_cat = df_cleaned[geo_mask & category_mask]

    # Determine top results
    top_k = 20
    if not filtered_by_geo_and_cat.empty:
        top_results = filtered_by_geo_and_cat.nlargest(top_k, 'penalized_similarity')
    else:
        top_results = df_cleaned.nlargest(top_k, 'penalized_similarity')

    return top_results

@app.get("/hello")
async def search():
    return {"message": "Hello from FastAPI!"}

# Define the data model for the request body
class SearchQuery(BaseModel):
    query: str

# FastAPI route for handling search queries

@app.post("/search")
async def search(search_query: SearchQuery):
    query = search_query.query
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    processed_query = preprocess_query(query)
    factors = extract_factors_and_context(processed_query)
    
    top_results = search_datasets(processed_query, df_cleaned, factors)
    
    if top_results.empty:
        return {"message": "No results found."}

    # Convert results to a list of dictionaries
    results = top_results.to_dict(orient='records')
    return {"results": results}



# @app.post("/search")
# async def search(search_query: SearchQuery):
#     # Mock response for demonstration
#     results = [
#         {
#             "Dataset Category": "Example Category",
#             "Vendor": "Example Vendor",
#             "Dataset Name": "Example Dataset",
#             "Description": "Example Description",
#             "Therapeutic coverage": "Example Therapeutic Coverage",
#             "Geographic coverage": "Example Geographic Coverage",
#         }
#     ]
#     return {"results": results}