"""
Prompt Templates

This module contains prompt templates used across the application.
"""


# Story generation prompt template used for OpenAI vision model

# Characteristic from gpt-4.1 =========================================================================================================

CLAIM_CRITERIAS = """
1.	Repeated Break Locations
  o	Bottles frequently broke at structurally weak areas, specifically the neck/shoulder or the base/bottom.
2.	Jagged, Sharp Edges
  o	All broken sections have irregular, sharp, and dangerous edges, posing significant handling risks.
3.	Fragmentation and Cracking
  o	Multiple examples of extensive crack lines, often radiating from the main break point, with some bottles experiencing catastrophic shattering into many pieces.
  o	Large and medium shards are common, often accompanied by numerous small fragments.
4.	Detached Neck and Cap
  o	In cases of neck/shoulder fracture, the neck segment (usually with the cap still sealed) is separated cleanly from the main body and often placed beside it.
5.	Base Separation is considered as claim
  o	Several bottles display a relatively clean separation of the base/bottom, often forming a "cap" of glass left aside.
6.	Visible Internal Cracks
  o	Many bottles show pronounced internal cracks, sometimes running through the label area or the full length of the body, indicating propagation of stress.
7.	Unopened/Sealed State at Time of Breakage
  o	The majority of bottles have their caps still sealed on the broken neck, confirming they were not opened by hand but rather broke while sealed/full.
8.	Main Body Integrity
  o	Even when the top or base is missing, the remaining main body often stays upright but is structurally compromised.
9.	Label Condition
  o	Main labels are typically intact, though in shattering events, parts of the label may be torn or fragmented with the glass.
10.	Evidence of Spillage
  o	Several images document liquid leakage or stains in trays, especially for bottles that appear to have broken under pressure or while filled.
11.	Multiple Shards and Shard Sizes
  o	Both large breakaway pieces and many small, invisible fragments or splinters are present, increasing cleanup hazard.
12.	Foreign material appearance
  o	Occasionally, foreign debris or packaging material remains attached to the fractured bottle sections, suggesting potential contamination.
13.	Broken While Full/Pressurized
  o	Spillage and residue are consistent with breakage occurring while bottles were full or pressurized during the incident.
14.	High-Risk Cleanup and Handling
  o	The sharpness and number of fragments create major safety risks for anyone handling the broken bottles, requiring proper PPE.
15.	Root Cause Implications
  o	The similarity and location patterns of breakage suggest issues possibly related to bottle manufacturing, glass quality, handling/transport shock, or stress/pressure during processing or filling.
"""

UNCLAIM_CRITERIAS = """
1.	Breakage Consistently at Neck/Shoulder
  o	Nearly all bottles show primary breakage around the neck or shoulder area, resulting in the complete loss or severe fragmentation of the neck and upper portion.
2.	Jagged and Dangerous Edges
  o	The broken edges are consistently jagged, sharp, and irregular, presenting a serious risk of cuts and injuries.
3.	Detached Neck and Sealed Cap
  o	Detached necks, typically with the cap still sealed, are found inside or lying next to the bottle body, indicating breakage happened before opening.
4.	Variable Fragmentation
  o	Some bottles are broken into only a few large pieces, but several involve catastrophic fragmentation into many large and small shards (including label fragments).
5.	Extensive Crack Propagation
  o	Internal and external cracks radiate in multiple directions from the main break points, with spiderweb, linear, and branching patterns observed.
6.	Secondary Damage and Spillage
  o	Evidence of liquid residue or spillage is common, suggesting many bottles were broken while filled.
7.	Labels Generally Intact but Sometimes Torn
  o	The main bottle label is usually intact on the main body, but may be torn, found among fragments, or missing in cases of severe breakage.
8.	Visible Glass Residue or Internal Particulate
  o	Green glass particulate and residue are sometimes visible in the bottle body, increasing contamination and cleanup difficulty.
9.	Hazardous Shard Distribution
  o	Both small and large fragments are present, sometimes scattered around the tray, increasing the chance of missing smaller pieces during cleanup.
10.	Pointed Shard Protrusions
  o	Many broken bottles feature tall, pointed shards protruding from the rim of the remaining body, greatly increasing the risk of injury.
11.	Structural Instability
  o	Even when standing, all remaining bottle bodies are severely compromised by cracks and missing sections, making them unstable and unsafe for any use.
12.	Foreign Material Presence
  o	Occasional attachment of foreign objects such as packaging debris is noted on broken bottles, increasing contamination risk.
13.	Consistency in Pattern
  o	The nature and pattern of breakage (location, crack type, fragmentation, etc.) is consistent across different bottles, suggesting a recurring problem (handling, process, or material flaw).
"""


NEW_PROMPT = f"""
You will receive an image or multiple images of one bottle or a video of a broken bottle.
Your task is to classify claim or unclaim based on the provided images or video.
The answer must clearly specify whether the bottle can claim or unclaim,

# Steps
1. **Detect brand of bottle:**
   - Check whether what brand is this bottle.
   - if it's "Chang" or "ช้าง" need to be considered in the next step.
   - if it is not "Chang" or "ช้าง" response as unclaim without considering next steps and give a reason "This bottle is not brand Chang cannot claim".

2. **Keys characteristics of claimable bottle**
   {CLAIM_CRITERIAS}

3. **Keys characteristics of unclaimable bottle**
   {UNCLAIM_CRITERIAS}

4. **Detect, examine for each part of the bottle:**
   - **There are 4 main parts of a bottle:** 1.cap 2.neck 3.body 4.bottom
   - **Check the cap:** Is there the cap? Is it tightly closed? if so, it can claim checkmarks (✅).
   - **Check the neck:** Is there still the neck? If there is a neck seperation but not break into a small shatters is considered as claim checkmarks (✅).
   - **Check the body:** Is there still the body? if there is small damage consider as claim checkmarks (✅).
   - **Check the bottom:** Is there still the bottom? If there is a small damage on the bottom or base separation, it is considered as claim checkmarks (✅).

5. **Decide claim or unclaim, consider in order:**
   - If the bottle completely intact, it can claim checkmarks (✅).
   - If the cap separate from the main body and tightly closed, it can claim checkmarks (✅).
   - If the bottom is **missing entirely** (i.e., not found or shattered), it cannot claim (❌).
   - If the bottom is **detached as one clean piece** and placed next to the bottle (i.e., not shattered), it can claim (✅).
   - Base separation with clean break and no sharp fragments or internal cracks is considered CLAIM (✅).
   - If there is just only base separation or the separated bottom is not break into small shatters is considered as claim checkmarks (✅).
   - If there is a neck seperation but not break into a small shatters is considered as claim checkmarks (✅).


# Notes
- Always prioritize accuracy and clarity in your responses.
- Always answer claim or unclaim.
- Use checkmarks (✅) for passing conditions and X marks (❌) for failing conditions.
- Only if all conditions are met can be consider as claim.
- Ensure reasoning steps logically lead to the conclusions before stating your final answer.
- Provide True or False for claimable key.
- Use the following format for the output:
- If the bottom is separated but remains in one clean circular piece (e.g., seen next to the bottle), and there is no sign of shattering or cracking, this is a common base separation pattern and must be considered as CLAIM (✅).



# Output Format
For each assessment, use the following format:

**Bottle Assessment:**
✅/❌ [Cap condition]
✅/❌ [Neck condition]
✅/❌ [Body condition]
✅/❌ [Bottom condition]
✅/❌ **CLAIM/UNCLAIM** [final decision]

Then provide a JSON object with these keys:
- english: Use output format to answer.
- thai: The description translated to Thai.
- claimable: true/false
"""

# DATE_EXTRACTION_PROMPT = """
# You are an AI image analyzer extracting the production date from a Chang beer bottle label.

# Instructions:
# - Look for a sequence of exactly 6 digits that represents the production date code (format: DDMMYY)
# - Pay special attention to any numbers printed on the label, particularly those that appear in a different font or printing style 
# - Focus on numbers that may appear near product codes or batch numbers
# - When you find a 6-digit sequence (like 070526 in the sample image), parse it as:
#   * First 2 digits = Day (07)
#   * Middle 2 digits = Month (05)
#   * Last 2 digits = Year (26)
# - Convert year to 4-digit format by prepending "20" (26 → 2026)
# - Subtract 1 year from the 4-digit year to determine the manufacture date (2026 → 2025)
# - Format the final date as DD/MM/YYYY (07/05/2025)

# Looking at the provided image, extract the 6-digit code and convert it to a manufacture date.

# ⚠️ Output Format:
# Return ONLY a JSON object:
# { "manufactured_date": "DD/MM/YYYY" }
# If no valid code is visible:
# { "manufactured_date": "No production date visible" }

# DO NOT include any explanation or additional text. NO markdown formatting.
# """

DATE_EXTRACTION_PROMPT = """
You are an AI image analyzer extracting the production date from a Chang beer bottle label.

Instructions:
- Look for a sequence of exactly 6 digits that represents the production date code (format: DDMMYY)
- Pay special attention to any numbers printed on the label, particularly those that appear in a different font or printing style 
- Focus on numbers that may appear near product codes or batch numbers
- When you find a 6-digit sequence (like 070526 in the sample image), parse it as:
  * First 2 digits = Day (07)
  * Middle 2 digits = Month (05)
  * Last 2 digits = Year (26)
- Convert year to 4-digit format by prepending "20" (26 → 2026)
- Subtract 1 year from the 4-digit year to determine the initial manufacture date
- Apply these additional year validation rules:
  * If the resulting year is less than or equal to 2023, set the year to 2025
  * If the resulting year is greater than or equal to 2026, set the year to 2025
  * Otherwise keep the calculated year
- Format the final date as DD/MM/YYYY (example: "070526" → "07/05/2025")

Looking at the provided image, extract the 6-digit code and convert it to a manufacture date.

⚠️ Output Format:
Return ONLY a JSON object:
{ "manufactured_date": "DD/MM/YYYY" }
If no valid code is visible:
{ "manufactured_date": "No production date visible" }

DO NOT include any explanation or additional text. NO markdown formatting.
"""


# DATE_EXTRACTION_PROMPT = """
# You are an AI image analyzer. Your task is to find and extract a 6-digit production date code from a Chang beer bottle label.

# INSTRUCTIONS:

# - Carefully scan the label in the image for a group of **exactly 6 digits** together (example: 070526).
# - Do **not** use groups with more or less than 6 digits.
# - Ignore groups that have non-digit characters, spaces, or special symbols.
# - When you find the correct 6 digits, interpret as date in DDMMYY format:
#     - First 2 digits = Day
#     - Next 2 digits = Month
#     - Last 2 digits = Year (YY)
# - Convert year to 4 digits by adding "20" in front (example: 26 → 2026).
# - Subtract 1 year from the 4-digit year (2026 - 1 = 2025).
# - If the result year is less than or equal to 2023, set year to 2025.
# - If the result year is greater than or equal to 2026, set year to 2025.
# - Otherwise, keep the calculated year.
# - Format the final date as DD/MM/YYYY. (example: "070526" → "07/05/2025")

# RESPONSE FORMAT:
# - Respond **ONLY** with a single-line JSON object, like:
#     { "manufactured_date": "07/05/2025" }
# - If no valid 6-digit code is visible, respond with:
#     { "manufactured_date": "No production date visible" }
# - Do NOT add any explanation.
# - Do NOT use markdown, backticks, or any extra text.
# - Do NOT write anything before or after the JSON object.

# ONLY output the JSON object as described above. If you do not see a valid code, output the "No production date visible" JSON exactly.
# """

DATE_EXTRACTION_PROMPT_O4 = """
You are an AI assistant. Your ONLY task is to extract a 6-digit production date from a Chang beer bottle label image.

Instructions:
- Find exactly 6 digits together, no spaces or symbols (for example: 070526).
- Ignore any group with fewer or more than 6 digits, or with non-digit characters.
- Interpret these 6 digits as DDMMYY:
    - First 2 digits: Day
    - Next 2 digits: Month
    - Last 2 digits: Year (YY)
- Convert year to 4 digits by adding '20' in front. (e.g., 26 → 2026)
- Subtract 1 year from the year. (e.g., 2026 → 2025)
- If the year is less than or equal to 2023, or greater than or equal to 2026, set year to 2025.
- Format the final date as DD/MM/YYYY. (e.g., "070526" → "07/05/2025")

OUTPUT RULES:
- Output ONLY a single-line JSON object like:
  { "manufactured_date": "07/05/2025" }
- If there is no valid 6-digit group, output ONLY:
  { "manufactured_date": "No production date visible" }
- Do NOT add explanation, markdown, newlines, or extra text. Output ONLY the JSON object, nothing else.
- Do NOT write anything before or after the JSON object.
"""
