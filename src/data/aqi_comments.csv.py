import llm
import pandas as pd
import sys


def main():
    # Top 5 Pakistani cities by population
    cities = ["Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Islamabad"]

    model = llm.get_model("claude-3-haiku-20240307")
    system_prompt = "You are a helpful assistant providing short, one-line observations about air quality. Keep responses under 100 characters. Be informative but slightly humorous."

    results = []
    for city in cities:
        prompt = f"Give me a one-line observation about the air quality (AQI) situation in {city}, Pakistan."
        response = model.prompt(prompt, system=system_prompt)
        results.append({"city": city, "text": response.text().strip()})

    df = pd.DataFrame(results)
    df.to_csv(sys.stdout, index=False)


if __name__ == "__main__":
    main()
