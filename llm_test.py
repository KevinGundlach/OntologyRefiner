from llm_helper import LLMClient, ModelSettings

def main():

    with LLMClient(ModelSettings.gemini_flash_2_5(), use_google_genai=False) as client:
        text = client.generate("What is your name?")
        print("Response:")
        print(text)


if __name__ == "__main__":
    main()
    print("Done")
