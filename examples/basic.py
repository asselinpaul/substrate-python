import os
import sys
from pathlib import Path

# add parent dir to sys.path to make 'substrate' importable
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

api_key = os.environ.get("SUBSTRATE_API_KEY")
if api_key is None:
    raise EnvironmentError("No SUBSTRATE_API_KEY set")

from substrate import Substrate, TranscribeMedia

substrate = Substrate(api_key=api_key, timeout=60 * 5)

transcribe = TranscribeMedia({"audio_uri": "s3://"})

# summary = GenerateText({"prompt": sb.concat("summarize this story in one sentence: ", story.future.text)})

response = substrate.run(transcribe)
print(response.api_response.json)
print(response.api_response.status_code)

# summary_out = response.get(summary)
# print(summary_out.text)

# viz = Substrate.visualize(ry)
# print(viz)
