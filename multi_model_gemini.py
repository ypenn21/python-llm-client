import vertexai

from vertexai.generative_models import GenerativeModel, Part

# TODO(developer): Update project_id and location
vertexai.init(project="PROJECT", location="us-central1")

model = GenerativeModel("gemini-1.5-flash-001")

image_file = Part.from_uri(
    "gs://library_genai-enterprise-accounts/high-level-architecture-gcp.png", "image/jpeg"
)

# Query the model
response = model.generate_content([image_file, "I want you to be an expert gcp architect. Please parse the architecture diagram presented here. Describe the architecture and the flow. Thereafter generate infrastructure as code for terraform."])
print(response.text)