# Gemini TTS Comparison Demo

This project demonstrates various methods for generating Japanese Text-to-Speech (TTS) using Google Cloud services. It compares four different approaches:

1.  **Default:** Basic TTS with no special tuning.
2.  **Manual Tuning:** TTS with global adjustments to speaking rate and pitch.
3.  **Rule-Based Auto-Tagging:** A simple script that automatically adds SSML tags based on punctuation.
4.  **AI-Powered Tuning:** Uses the Gemini model via Vertex AI to intelligently analyze the text and insert nuanced SSML tags for a more natural, human-like delivery.

The entire process is authenticated securely using a single Google Cloud IAM Service Account.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python (~3.12)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (optional, but useful for debugging).

## Setup Instructions

Follow these steps to set up the project and reproduce the MP3 generation.

### 1. Clone the Repository

Clone this repository to your local machine:
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Google Cloud Project Setup

This project requires a Google Cloud project with a few services enabled.

**A. Create or Select a Project**
- Go to the [Google Cloud Console](https://console.cloud.google.com/) and select an existing project or create a new one.

**B. Enable Billing**
- The Vertex AI API requires that your project be linked to an active billing account.
- In the console, navigate to the **Billing** section and ensure your project is associated with a billing account. New users may be eligible for a free trial with credits.

**C. Enable Required APIs**
- You must enable two APIs for this project. Click the links below and click "Enable" for each one:
    1.  [Cloud Text-to-Speech API](https://console.cloud.google.com/apis/library/texttospeech.googleapis.com)
    2.  [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)

**D. Create a Service Account**
- A service account is used to securely authenticate the script.
    1.  In the Google Cloud Console, navigate to **IAM & Admin > Service Accounts**.
    2.  Click **+ CREATE SERVICE ACCOUNT**.
    3.  Give it a name (e.g., `gemini-tts-demo-user`).
    4.  Click **CREATE AND CONTINUE**.
    5.  In the "Grant this service account access to project" step, add the **Vertex AI User** role. This single role provides all necessary permissions for both TTS and the Gemini model.
    6.  Click **DONE**.

**E. Download the Service Account Key**
    1.  Find the service account you just created in the list.
    2.  Click the three-dots menu under "Actions" and select **Manage keys**.
    3.  Click **ADD KEY > Create new key**.
    4.  Select **JSON** as the key type and click **CREATE**. A JSON file will be downloaded.
    5.  Move this file into the root of your project directory and rename it to `iam-key.json`.

**Important:** The `.gitignore` file is configured to ignore `iam-key.json`. **Do not commit this file to source control.**

### 3. Install Dependencies

With Poetry installed, run the following command in the project root to create a virtual environment and install all required libraries:

```bash
poetry install
```

## Running the Script

To generate the four comparison MP3 files, run the main script using Poetry:

```bash
poetry run python tts_comparison.py
```

The script will execute and print its progress. Upon completion, you will find the following four files in the project directory:

- `news_1_default.mp3`
- `news_2_manual_tuned.mp3`
- `news_3_auto_tagged.mp3`
- `news_4_ai_tuned.mp3`
