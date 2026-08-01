"""
matcher.py
TF-IDF Cosine Similarity Resume Matcher Engine
Featured in Episode 6 & 7 of 'Doctorate to Data'
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(cv_text: str, job_description: str) -> float:
    """
    Calculates TF-IDF cosine similarity between Academic CV text and Industry Job Description.
    Returns score as a percentage float.
    """
    documents = [cv_text, job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Cosine similarity between doc 0 (CV) and doc 1 (JD)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)

if __name__ == "__main__":
    with open("data/cv_master.txt", "r") as f:
        cv = f.read()
        
    sample_jd = """
    We are seeking a Data Scientist with strong Python, SQL, and statistical modeling experience.
    The ideal candidate has experience with scikit-learn, regression analysis, time series forecasting,
    and building data pipelines. A background in Quantitative Research or Mathematics is a plus!
    """
    
    score = calculate_match_score(cv, sample_jd)
    print(f"🎯 Calculated Resume Match Score: {score}%")
