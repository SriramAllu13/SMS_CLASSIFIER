import streamlit as st
import pickle
import zipfile
import nltk
from PIL import Image
import io
import pytesseract
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

ps = PorterStemmer()
vector = pickle.load(open('vector.pkl', 'rb'))

# Function to load compressed pickle file
def load_compressed_pickle(zip_filename, pickle_filename):
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        with zip_ref.open(pickle_filename) as pickle_file:
            loaded_data = pickle.load(pickle_file)
    return loaded_data

zip_filename = 'model.zip'
pickle_filename = 'model.pkl'
SV = load_compressed_pickle(zip_filename, pickle_filename)

# Function to transform the message
def transform_message(message):
    message = message.lower()
    message = nltk.word_tokenize(message)

    y = [i for i in message if i.isalnum()]
    message = y[:]
    y.clear()

    stop_words = set(stopwords.words('english'))
    y = [i for i in message if i not in stop_words and i not in string.punctuation]
    message = y[:]
    y.clear()

    y = [ps.stem(i) for i in message]
    return " ".join(y)

# Sidebar for navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio("Select a page:", ["Text Classify", "Text Input", "Image Input", "Feedback"])

# Page: Text Classify
if option == "Text Classify":
    st.title("SMS Classifier")
    st.write("Welcome to the SMS Classifier!")
    st.write("This application classifies messages into spam or normal. You can use the other options to interact with the application.")
    st.write("### How it Works")
    st.write("1. **Text Input**: Enter your message and get the classification.")
    st.write("2. **Image Input**: Upload an image containing text to extract and classify.")
    st.write("3. **Feedback**: Provide your feedback about the application.")

# Page: Text Input
elif option == "Text Input":
    st.title("Text Input")
    input_sms = st.text_area("Enter your message")
    
    if st.button('Predict'):
        if input_sms:
            with st.spinner('Processing...'):
                transform_sms = transform_message(input_sms)
                vector_inp = vector.transform([transform_sms]).toarray()
                result = SV.predict(vector_inp)[0]
                if result == 1:
                    st.header('Wait a Minute, this is a SPAM!')
                else:
                    st.header('Ohhh, this is a normal message.')
        else:
            st.warning("Please enter a message for prediction.")

# Page: Image Input
elif option == "Image Input":
    st.title("Image Input")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        st.write("Extracting text from image...")
        with st.spinner('Processing...'):
            # Extract text from the image using pytesseract
            text = pytesseract.image_to_string(image)
            st.text_area("Extracted Text", text, height=300)
            
            if text:
                transform_sms = transform_message(text)
                vector_inp = vector.transform([transform_sms]).toarray()
                result = SV.predict(vector_inp)[0]
                if result == 1:
                    st.header('Wait a Minute, this is a SPAM!')
                else:
                    st.header('Ohhh, this is a normal message.')
            else:
                st.warning("No text detected in the image.")

# Page: Feedback
elif option == "Feedback":
    st.title("Feedback")
    feedback = st.text_area("Your feedback")
    
    if st.button('Submit Feedback'):
        if feedback:
            st.success("Thank you for your feedback!")
            # Here, you can save the feedback to a file or a database
        else:
            st.warning("Please provide your feedback before submitting.")
