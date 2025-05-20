import logging
import json
import re
import nltk
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag to track whether NLTK resources have been checked
nltk_resources_checked = False

# Function to lazily check and download NLTK resources when needed
def ensure_nltk_resources():
    global nltk_resources_checked
    if not nltk_resources_checked:
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            logger.info("Downloading NLTK resources...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
        nltk_resources_checked = True

# Download required NLTK resources on import
ensure_nltk_resources()

# Now import the NLTK modules after resources are downloaded
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# We're using a mock BERT implementation, so no need for real TensorFlow
# Dummy classes to replace TensorFlow
class DummyTokenizer:
    def __init__(self, num_words=None):
        self.num_words = num_words

# Initialize lemmatizer and stop words after ensuring resources exist
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Define aspect categories relevant to educational feedback
ASPECTS = [
    "teaching_quality", 
    "course_content", 
    "infrastructure", 
    "lab_facilities", 
    "administration", 
    "library_resources", 
    "extracurricular", 
    "general"
]

# Mock BERT model implementation
# In a real implementation, you would load a pre-trained BERT model
# For this demo, we'll simulate the model's behavior
class MockBertModel:
    def __init__(self):
        self.tokenizer = DummyTokenizer(num_words=5000)
        
    def preprocess_text(self, text):
        # Clean text
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
        
        return ' '.join(tokens)
    
    def predict_sentiment(self, text):
        # Mock sentiment prediction
        # In reality, this would use a trained BERT model
        text = self.preprocess_text(text)
        
        # Simple rule-based approach for demonstration
        positive_words = ['good', 'great', 'excellent', 'helpful', 'best', 'amazing', 'perfect', 'love', 'enjoy']
        negative_words = ['bad', 'poor', 'terrible', 'worst', 'hate', 'difficult', 'unfair', 'inadequate', 'waste']
        
        pos_count = sum(1 for word in text.split() if word in positive_words)
        neg_count = sum(1 for word in text.split() if word in negative_words)
        
        # Calculate sentiment score between -1 and 1
        total = pos_count + neg_count
        if total == 0:
            score = 0  # Neutral if no sentiment words
        else:
            score = (pos_count - neg_count) / total
        
        # Determine sentiment label
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        
        return score, label
    
    def extract_aspects(self, text):
        # Mock aspect extraction
        # In reality, this would use more sophisticated NLP techniques
        text = self.preprocess_text(text)
        words = text.split()
        
        # Keywords for each aspect
        aspect_keywords = {
            "teaching_quality": ['teaching', 'lecture', 'teacher', 'professor', 'explain', 'clarity', 'instructor'],
            "course_content": ['content', 'material', 'syllabus', 'curriculum', 'topic', 'subject', 'course'],
            "infrastructure": ['classroom', 'building', 'facility', 'campus', 'wifi', 'infrastructure'],
            "lab_facilities": ['lab', 'laboratory', 'equipment', 'practical', 'experiment', 'instrument'],
            "administration": ['admin', 'office', 'staff', 'management', 'registration', 'administrative'],
            "library_resources": ['library', 'book', 'resource', 'study', 'reference', 'journal'],
            "extracurricular": ['event', 'activity', 'club', 'sport', 'cultural', 'fest', 'competition'],
            "general": ['overall', 'general', 'college', 'university', 'institution', 'education']
        }
        
        # Identify aspects mentioned in the text
        mentioned_aspects = {}
        
        for aspect, keywords in aspect_keywords.items():
            aspect_score = 0
            matches = []
            
            for keyword in keywords:
                for word in words:
                    if keyword in word:
                        matches.append(word)
                        
                        # Check nearby words for sentiment
                        idx = words.index(word)
                        nearby_words = words[max(0, idx-3):min(len(words), idx+4)]
                        
                        # Simple sentiment calculation
                        positive_words = ['good', 'great', 'excellent', 'helpful', 'best']
                        negative_words = ['bad', 'poor', 'terrible', 'worst', 'inadequate']
                        
                        pos_count = sum(1 for w in nearby_words if w in positive_words)
                        neg_count = sum(1 for w in nearby_words if w in negative_words)
                        
                        # Update aspect sentiment
                        if pos_count > neg_count:
                            aspect_score += 1
                        elif neg_count > pos_count:
                            aspect_score -= 1
            
            # Only include aspects that were mentioned
            if matches:
                mentioned_aspects[aspect] = {
                    "score": aspect_score,
                    "sentiment": "positive" if aspect_score > 0 else "negative" if aspect_score < 0 else "neutral",
                    "mentions": matches
                }
        
        return mentioned_aspects


# Create a singleton instance of the model
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            # In a real implementation, load a pre-trained BERT model
            # For this demo, we'll use our mock implementation
            _model = MockBertModel()
            logger.info("BERT model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing BERT model: {e}")
            # Fallback to a very simple model if there's an error
            _model = MockBertModel()
    return _model


def analyze_text(text):
    """
    Analyze text feedback and return sentiment score and label
    
    Args:
        text (str): The feedback text to analyze
        
    Returns:
        tuple: (sentiment_score, sentiment_label)
    """
    # Lazily load NLTK resources when needed
    ensure_nltk_resources()
    
    if not text or len(text.strip()) == 0:
        return 0.0, "neutral"  # Default for empty text
    
    try:
        model = get_model()
        score, label = model.predict_sentiment(text)
        return score, label
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return 0.0, "neutral"  # Default in case of error


def aspect_based_analysis(text):
    """
    Perform aspect-based sentiment analysis on feedback text
    
    Args:
        text (str): The feedback text to analyze
        
    Returns:
        dict: Aspect-based analysis results
    """
    # Lazily load NLTK resources when needed
    ensure_nltk_resources()
    if not text or len(text.strip()) == 0:
        return {}  # Empty result for empty text
    
    try:
        model = get_model()
        aspects = model.extract_aspects(text)
        return aspects
    except Exception as e:
        logger.error(f"Error in aspect-based analysis: {e}")
        return {}  # Empty result in case of error
