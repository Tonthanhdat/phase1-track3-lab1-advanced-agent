import json

def main():
    with open('data/hotpot_mini.json', 'r') as f:
        data = json.load(f)
    
    new_data = []
    # Repeat the 8 examples 13 times to get 104 examples
    for i in range(13):
        for item in data:
            new_item = item.copy()
            new_item['qid'] = f"{item['qid']}_dup_{i}"
            new_data.append(new_item)
            
    with open('data/test_100.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"Created data/test_100.json with {len(new_data)} examples.")

if __name__ == '__main__':
    main()
