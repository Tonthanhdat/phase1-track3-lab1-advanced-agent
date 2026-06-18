import json

def convert():
    input_file = 'data/hotpot_dev_distractor_v1.json'
    output_file = 'data/hotpot_dev_converted.json'
    
    print(f"Reading from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
        
    converted = []
    for item in data:
        ctx = []
        for title, sentences in item.get('context', []):
            ctx.append({
                "title": title,
                "text": " ".join(sentences)
            })
            
        converted.append({
            "qid": item["_id"],
            "difficulty": item["level"],
            "question": item["question"],
            "gold_answer": item["answer"],
            "context": ctx
        })
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2)
    
    print(f"Successfully converted {len(converted)} items to {output_file}")

if __name__ == '__main__':
    convert()
