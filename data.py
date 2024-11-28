# data.py
import pandas as pd
from sentence_transformers import SentenceTransformer

# Load the data
file_path = 'genai_data.csv'
df = pd.read_csv(file_path)

# Select and clean specific columns
new_df = df.iloc[:, [0, 1, 2, 3, 5, 8, 28]]
new_df = new_df.dropna(subset=['Description', 'TA coverage'])
df_cleaned = new_df

# Function to concatenate columns
def concatenate_columns(row):
    return ' '.join([
        str(row['Country']),
        str(row['Region']),
        str(row['Name of Database/Report']),
        str(row['Dataset Type']),
        str(row['Parent Vendor Name (If Applicable)']),
        str(row['Description']),
        str(row['TA coverage'])
    ])

# Apply concatenation and generate embeddings
df_cleaned['concatenated'] = df_cleaned.apply(concatenate_columns, axis=1)

# Initialize the model
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for concatenated text
df_cleaned['embedding'] = df_cleaned['concatenated'].apply(lambda x: sentence_model.encode(x, convert_to_numpy=True).tolist())

# Save the dataframe with embeddings
df_cleaned.to_csv('processed_data_with_embeddings.csv', index=False)
