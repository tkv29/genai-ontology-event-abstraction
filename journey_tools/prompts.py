"""File containing all prompts for the patient journey generation."""

CREATE_PATIENT_JOURNEY_PROMPT = """
Imagine you have been diagnosed with Rheumatoid Arthritis. Please provide a detailed account of your journey with this condition, focusing primarily on the medications you have been prescribed. Include the following information:

Initial symptoms that led to your diagnosis and the approximate timeline of their appearance
The process of getting diagnosed, mentioning any misdiagnoses or delays
A comprehensive list of all medications prescribed for managing your Rheumatoid Arthritis symptoms, including:
1. Initial symptoms and the timeline of their appearance
2. The process of getting diagnosed, including any misdiagnoses or delays
3. All Medications prescribed for managing Rheumatoid Arthritis symptoms, including:
- Names of the medications
- Effectiveness of each medication in managing your symptoms
4. Healthcare professionals you consulted
Provide a chronological narrative of your experiences, using specific dates when possible and relative time references (e.g., "a week later," "the following month") when exact dates are not available. Focus on your personal experiences with the medications prescribed for Rheumatoid Arthritis and how they impacted your symptoms and overall quality of life.

Please aim for a word count between 100 and 400 words, ensuring that the main emphasis remains on


"""