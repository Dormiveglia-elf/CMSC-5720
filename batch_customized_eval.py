import re
import json
from openai import OpenAI
import jsonlines
import time

def batch_eval(query_file, result1_file, result2_file, output_file_path):
    # Openai configuration
    client = OpenAI(api_key='',base_url = "")
    with open(query_file, "r", encoding="utf-8") as f:
        data = f.read()

    queries = re.findall(r"- Question \d+: (.+)", data)

    # read first answer file
    with open(result1_file, "r", encoding="utf-8") as f:
        answers1 = json.load(f)
    answers1 = [i["result"] for i in answers1]

    # read second answer file
    with open(result2_file, "r", encoding="utf-8") as f:
        answers2 = json.load(f)
    answers2 = [i["result"] for i in answers2]

    if not (len(queries) == len(answers1) == len(answers2)):
        print("Warning: the number of query and answer does not match, please check!")
        return

    evaluations = []

    for i, (query, answer1, answer2) in enumerate(zip(queries, answers1, answers2), start=1):
        sys_prompt = """
        ---Role---
        You are an expert tasked with evaluating two answers to the same question based on five criteria: **Accuracy**, **Comprehensiveness**, **Diversity**, **Empowerment**, and **Hallucination**.
        """

        prompt = f"""
        You will evaluate two answers to the same question based on five criteria: **Accuracy**, **Comprehensiveness**, **Diversity**, **Empowerment**, and **Hallucination**.

        - **Accuracy**: How correct and factual is the information provided in the answer?
        - **Comprehensiveness**: How much detail does the answer provide to cover all aspects and details of the question?
        - **Diversity**: How varied and rich is the answer in providing different perspectives and insights on the question?
        - **Empowerment**: How well does the answer help the reader understand and make informed judgments about the topic?
        - **Hallucination**: How free is the answer from fabricated or unsupported information?

        For each criterion, choose the better answer (either Answer 1 or Answer 2) and explain why. Then, select an overall winner based on these five categories.

        Here is the question:
        {query}

        Here are the two answers:

        **Answer 1:**
        {answer1}

        **Answer 2:**
        {answer2}

        Evaluate both answers using the five criteria listed above and provide detailed explanations for each criterion.

        Output your evaluation in the following JSON format, do not contain the "json" identifier at the beginning and end!!!:

        {{
            "Accuracy": {{
                "Winner": "[Answer 1 or Answer 2]",
                "Explanation": "[Provide explanation here]"
            }},
            "Comprehensiveness": {{
                "Winner": "[Answer 1 or Answer 2]",
                "Explanation": "[Provide explanation here]"
            }},
            "Diversity": {{
                "Winner": "[Answer 1 or Answer 2]",
                "Explanation": "[Provide explanation here]"
            }},
            "Empowerment": {{
                "Winner": "[Answer 1 or Answer 2]",
                "Explanation": "[Provide explanation here]"
            }},
            "Hallucination": {{
                "Winner": "[Answer 1 or Answer 2]",
                "Explanation": "[Provide explanation here]"
            }},
            "Overall Winner": {{
                "Winner": "[Answer 1 or Answer 2]",
                "Explanation": "[Summarize why this answer is the overall winner based on the five criteria]"
            }}
        }}

        The output should not contain any extra characters or text outside of this JSON structure.
        Do NOT contain the "json" identifier at the beginning and end.
        """

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt},
        ]

        # try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0,
            max_tokens=1500,
        )

        max_retries = 3  # max retry
        retry_delay = 1

        response = response.choices[0].message.content
        for attempt in range(max_retries):
            try:
                evaluation = json.loads(response)
                evaluations.append(evaluation)
                print(f"Successfully evaluate {i}/{len(queries)}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Failed after maximum retries")

    with jsonlines.open(output_file_path, mode="w") as writer:
        for eval_item in evaluations:
            writer.write(eval_item)

    print(f"All evaluation completed, results are written to {output_file_path}")

if __name__ == "__main__":
    query_file = "questions.txt"
    result1_file = "answer1.json"
    result2_file = "answer2.json"
    output_file_path = "xxx.jsonl"

    batch_eval(query_file, result1_file, result2_file, output_file_path)
