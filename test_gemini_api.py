import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_api():
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
        print("Please add GEMINI_API_KEY=your_actual_key to your .env file.")
        return

    # Configure the SDK
    genai.configure(api_key=api_key)

    # Initialize the model
    # Using gemini-1.5-flash as it's fast and usually available
    model = genai.GenerativeModel('gemini-flash-latest')

    print("🚀 Testing Gemini API Key...")
    
    try:
        # Simple prompt to test connectivity and key validity
        response = model.generate_content("Say 'Gemini API is working correctly!'")
        
        if response and response.text:
            print(f"✅ Success! Response: {response.text}")
        else:
            print("⚠️ API call succeeded but returned an empty response.")
            
    except Exception as e:
        print(f"❌ API Test Failed!")
        print(f"Error details: {str(e)}")
    
    print("🏁 Test script finished execution.")

if __name__ == "__main__":
    test_gemini_api()
