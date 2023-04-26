import streamlit as st 
import requests
from trycourier import Courier
import ai21

# Set up API keys for ai21 labs and Courier
ai21.api_key = AI21_API_KEY = st.secrets['AI21_API_KEY']
COURIER_AUTH_TOKEN = st.secrets['COURIER_AUTH_TOKEN']

# Configures the default settings of the page
st.set_page_config(
    page_title="TnC Digest",
    page_icon="📃",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/dotAadarsh/TnC-Digest',
        'Report a bug': "https://github.com/dotAadarsh/TnC-Digest",
        'About': "# Clear the clutter, understand it better: Simplify T&Cs with our app."
        }
    )

def get_metadata(input_url):
    url = 'https://api.microlink.io'
    params = {'url': f'{input_url}', 'meta': True}

    response = requests.get(url, params)
    result = response.json()
    title = result['data']['title']
    description = result['data']['description']
    publisher = result['data']['publisher']

    return title, description, publisher

@st.cache_data
def segment(input_url):

    # Define the input source and type
    source = input_url
    sourceType = "URL"

    # Call the Segmentation API
    response = ai21.Segmentation.execute(source=source, sourceType=sourceType)

    segments = response["segments"] # get the list of segments
    for segment in segments:
        if segment["segmentType"] == "normal_text": # filter for segments with segmentType "normal_text"
            # print(segment["segmentText"]) # access the segmentText value

            result = ""
            segment_text = segment["segmentText"]
            result += summarize(segment_text)

    return result

@st.cache_data
def summarize(segmented_text):

    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {AI21_API_KEY}',
    }

    json_data = {
        'prompt': f'By posting Content to the Service, You grant Us the right and license to use, modify, publicly perform, publicly display, reproduce, and distribute such Content on and through the Service. You retain any and all of Your rights to any Content You submit, post or display on or through the Service and You are responsible for protecting those rights. You agree that this license includes the right for Us to make Your Content available to other users of the Service, who may also use Your Content subject to these Terms. \n\nExtract important points and convert it into a short bulletin format for the given terms and conditions:\n- By posting Content, you give us the right to use, modify, and distribute it \n- You retain your rights to the content and are responsible for protecting them \n- We have the right to make your content available to other users of the Service, who may also use your content subject to these terms\n\n###\n\nOur Service may contain links to third-party web sites or services that are not owned or controlled by the Company.\nThe Company has no control over, and assumes no responsibility for, the content, privacy policies, or practices of any third party web sites or services. You further acknowledge and agree that the Company shall not be responsible or liable, directly or indirectly, for any damage or loss caused or alleged to be caused by or in connection with the use of or reliance on any such content, goods or services available on or through any such web sites or services.\nWe strongly advise You to read the terms and conditions and privacy policies of any third-party web sites or services that You visit.\n\nExtract important points and convert it into a short bulletin format for the given terms and conditions:\n- Service may contain links to third-party websites/services not owned by the company\n- Company has no control over the content/privacy policies/practices of such third-party sites\n- Company not responsible/liable for any damage or loss caused by use of or reliance on such content/goods/services\n- Users should read terms and conditions/privacy policies of any third-party sites visited\n\n###\n\n{segmented_text}\n\nExtract important points and convert it into a short bulletin format for the given terms and conditions:\n',
        'numResults': 1,
        'maxTokens': 200,
        'temperature': 0,
        'topKReturn': 0,
        'topP': 1,
        'countPenalty': {
            'scale': 0,
            'applyToNumbers': False,
            'applyToPunctuations': False,
            'applyToStopwords': False,
            'applyToWhitespaces': False,
            'applyToEmojis': False,
        },
        'frequencyPenalty': {
            'scale': 0,
            'applyToNumbers': False,
            'applyToPunctuations': False,
            'applyToStopwords': False,
            'applyToWhitespaces': False,
            'applyToEmojis': False,
        },
        'presencePenalty': {
            'scale': 0,
            'applyToNumbers': False,
            'applyToPunctuations': False,
            'applyToStopwords': False,
            'applyToWhitespaces': False,
            'applyToEmojis': False,
        },
        'stopSequences': [],
    }

    response = requests.post('https://api.ai21.com/studio/v1/j2-grande-instruct/complete', headers=headers, json=json_data)
    data = response.json()
    return data['completions'][0]["data"]['text']


# Define a function to send an email using Courier API
def send_email(key_points, recipient_email, title, description, publisher):

    url = "https://api.courier.com/send"

    payload = {
    "message": {
        "template": "NG0YGY4T0G4B42NWNW5NZZADR0ZK",
        "data": {
        "title": title,
        "key_points": key_points,
        "publisher": publisher,
        "description": description,
        },
        "to": {
        "email": recipient_email
        }
    }
    }
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {COURIER_AUTH_TOKEN}"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)

# Define the Streamlit app
def main():

    with st.sidebar:
        st.write("Created for Courier Hacks: Python Programs")
        st.header("TnC Digest")
        st.markdown("""

            ### What it does?

            It extracts the key points from the long and never read terms and conditions documents.
            ### Built with

            - [AI21 Labs](https://www.ai21.com/)
            - [Courier](https://www.courier.com/)
            - [Streamlit](https://streamlit.io/)

            ### How it works?
            Initially it segments the texts from the given document URL and send it to AI21 Labs to extract the key points in chunks and ties it up. 
            Then it uses Courier API to send the result to the desired E-Mail given by the user.

            ### Example Links
            - [Streamlit - Terms of Use](https://streamlit.io/terms-of-use)
            - [Deepgram - Terms](https://deepgram.com/terms/)
        """)
    
    st.title('TnC Digest')
    url = st.text_input('Enter the URL of the TermsnConditions/Policy document', 'https://streamlit.io/terms-of-use')
    email = st.text_input('Enter your email address')

    if st.button('Generate Summary') and url and email:
        with st.spinner('Wait for it.../ Once its completed you can check the mail as well'):
            title, description, publisher = get_metadata(url)
            summary = segment(url)
            if summary:
                send_email(summary, email, title, description, publisher)
                st.write(summary)
        st.success('Done!')

if __name__ == '__main__':
    main()
