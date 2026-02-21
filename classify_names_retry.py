#!/usr/bin/env python3
"""
Retry classification for remaining unknown author names with improved JSON parsing
"""
import os
import json
import sqlite3
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Database connection
db_path = "data/gender_data.db"

def get_unknown_names():
    """Fetch all author IDs and names with unknown gender (length > 1)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM authors WHERE (gender IS NULL OR gender = 'unknown') AND LENGTH(name) > 1 ORDER BY id"
    )
    results = cursor.fetchall()
    conn.close()
    return results

def parse_json_response(response_text):
    """
    Try multiple strategies to parse JSON from response
    """
    # Strategy 1: Direct JSON parsing
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract JSON from markdown blocks
    if "```json" in response_text:
        try:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    if "```" in response_text:
        try:
            json_str = response_text.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Strategy 3: Try to fix common JSON issues
    try:
        # Remove trailing commas
        fixed = re.sub(r',(\s*[}\]])', r'\1', response_text)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Try to extract key-value pairs manually
    classifications = {}
    # Match patterns like "Name": "gender"
    pattern = r'"([^"]+)":\s*"(male|female|unknown)"'
    matches = re.findall(pattern, response_text)
    if matches:
        classifications = dict(matches)
        return classifications if classifications else None

    return None

def classify_names_batch(names_batch, batch_num):
    """
    Classify a batch of names using Groq API with improved parsing
    Returns a dict mapping name -> gender classification
    """
    # Create a list of names for the prompt
    names_list = [name for _, name in names_batch]

    # Create a JSON request format for the API
    example_response = '{"name": "male"}' if len(names_list) < 2 else f'{{"{names_list[0]}": "male", "{names_list[1]}": "female"}}'

    prompt = f"""You are an expert at classifying names by gender. Analyze the following list of names and classify each as either "male", "female", or "unknown" based on the name alone.

Return ONLY a valid JSON object where keys are the names and values are the gender classification. Ensure all special characters in names are properly escaped.

Names to classify:
{json.dumps(names_list)}

Response format (must be valid JSON with proper escaping):
{example_response}"""

    try:
        print(f"  [Batch {batch_num}] Sending {len(names_list)} names to Groq API...")
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.choices[0].message.content.strip()
        print(f"  [Batch {batch_num}] Received response ({len(response_text)} chars)")

        # Try to parse with improved strategy
        classifications = parse_json_response(response_text)

        if classifications:
            print(f"  [Batch {batch_num}] Successfully parsed {len(classifications)} classifications")
            return classifications
        else:
            print(f"  [Batch {batch_num}] ERROR: Could not parse JSON response")
            print(f"  [Batch {batch_num}] Response preview: {response_text[:200]}")
            return {}

    except Exception as e:
        print(f"  [Batch {batch_num}] ERROR calling Groq API: {e}")
        return {}

def update_database(updates):
    """Update the database with gender classifications"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    updated_count = 0
    for author_id, gender in updates:
        cursor.execute(
            "UPDATE authors SET gender = ? WHERE id = ?",
            (gender, author_id)
        )
        updated_count += 1

    conn.commit()
    conn.close()
    return updated_count

def main():
    print("Fetching remaining unknown author names...")
    unknown_names = get_unknown_names()
    print(f"Found {len(unknown_names)} remaining unknown names to classify")

    # Process in batches
    batch_size = 100
    total_updated = 0
    total_batches = (len(unknown_names) + batch_size - 1) // batch_size

    for i in range(0, len(unknown_names), batch_size):
        batch = unknown_names[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"\n[{batch_num}/{total_batches}] Processing batch ({i+1}-{min(i+batch_size, len(unknown_names))} of {len(unknown_names)} names)...")

        # Classify the batch
        classifications = classify_names_batch(batch, batch_num)

        if not classifications:
            print(f"  Skipped batch {batch_num} (error or empty response)")
            continue

        # Prepare updates: map author_id to gender based on name match
        updates = []
        for author_id, name in batch:
            if name in classifications:
                gender = classifications[name]
                updates.append((author_id, gender))

        if updates:
            print(f"  Updating {len(updates)} matched records...")
            updated = update_database(updates)
            total_updated += updated
            print(f"  ✓ Updated {updated} records in database")
        else:
            print(f"  No matches found in batch {batch_num}")

    print(f"\n{'='*60}")
    print(f"✓ Complete! Updated {total_updated} records total")

    # Verify the updates
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM authors WHERE (gender IS NULL OR gender = 'unknown') AND LENGTH(name) > 1")
    remaining = cursor.fetchone()[0]
    conn.close()

    print(f"Remaining unknown names: {remaining}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
