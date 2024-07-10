LOCATION = "us-east5"
prompt_template = """You are an expert in Google Cloud Platform (GCP), fluent in `gcloud` commands, 
and deeply familiar with Terraform modules for GCP. Your task is to translate shell 
scripts that utilize `gcloud` commands into equivalent, well-structured Terraform code, 
adhering to Terraform best practices for file organization and maintainability.

Please carefully analyze the provided bash script enclosed within triple back quotes `%s` 

Your output should include:

1. **Terraform Code in Separate Files:**
   * **main.tf:** A fully functional Terraform configuration file containing the core 
     infrastructure resource definitions that replicate the functionality of the bash script.
   * **variables.tf:** This file should contain all input variable declarations used in 
     the `main.tf` file.
   * **Additional Files (If Applicable):**  Suggest and create additional Terraform files 
     as needed (e.g., `outputs.tf`, `provider.tf`, `data.tf`) based on the complexity and 
     requirements of the converted script.

2. **Explanation:** A clear breakdown of the Terraform resources, variables, and modules 
   used, along with explanations for how they achieve the same results as the original script.
   Indicate which file each element belongs to.

3. **Best Practices:** Where applicable, offer suggestions for adhering to Terraform best 
   practices beyond file organization (e.g., resource naming, input validation, module usage).

4. **Potential Optimizations:** If there are opportunities to make the Terraform code more 
   efficient, concise, or maintainable, please highlight them.

**Important Considerations:**

* **Environment Variables:** If the bash script relies on environment variables, ensure the 
   Terraform code handles them appropriately (e.g., using input variables in `variables.tf`).
* **Error Handling:** Terraform provides error handling mechanisms that may be missing in the 
   bash script. Incorporate these to improve the robustness of the code.
* **State Management:** Briefly explain how Terraform state would be managed for this particular 
   configuration.
* **Example Usage:** Demonstrates how to apply Terraform script.
* **Reference Documentation:** Output should also consider the following document enclosed within triple back quotes for best practice:
`%s` """
bash_script = """

      PROJECT_ID="my-gcp-project"
      ZONE="us-central1-a"
      INSTANCE_NAME="web-server-01"
      MACHINE_TYPE="e2-medium"
      IMAGE="debian-cloud/debian-11"

      gcloud services enable vision.googleapis.com
      gcloud services enable cloudfunctions.googleapis.com

      gcloud compute instances create $INSTANCE_NAME \
        --project $PROJECT_ID \
        --zone $ZONE \
        --machine-type $MACHINE_TYPE \
        --image $IMAGE \
        --boot-disk-size 20GB

      gsutil mb -l us-central1 gs://library_next24_images
      gsutil uniformbucketlevelaccess set on gs://library_next24_images
      gsutil iam ch allUsers:objectViewer gs://library_next24_images

"""
reference_doc = """
 Best practices on dependency
management
This document provides recommendations for expressing dependencies between resources in
your Terraform configuration.
Favor implicit dependencies over explicit dependencies
Resource dependencies arise when one resource depends on the existence of other resources.
Terraform must be able to understand these dependencies to ensure that resources are
created in the correct order. For example, if resource A has a dependency on resource B,
resource B is created before resource A.
Terraform configuration dependencies can be established through implicit and explicit
dependency declarations
 (https://developer.hashicorp.com/terraform/tutorials/configuration-language/dependencies). Implicit
dependencies are declared through expression references
 (https://developer.hashicorp.com/terraform/language/expressions/references), while explicit
dependencies are specified by using the depends_on
 (https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on) meta argument.
The depends_on argument specifies that Terraform must complete all the actions on the
object(s) that a resource or a module depends on, before proceeding with the dependent
object.
While both approaches ensure a correct order of operations, implicit dependencies often lead
to more efficiency in planning for updates and replacement of resources
 (https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on#processing-andplanning-consequences)
. This is because Terraform can intelligently track the specific fields involved in an implicit
dependency, potentially avoiding changes to the dependent resource if those specific fields
remain unaltered within the dependency.
In comparison to implicit dependencies, explicit dependencies convey less specific
information. This means that Terraform can only formulate more conservative plans for
resource creation, updates, and replacement in the absence of knowledge of the particular
attributes that constitute the dependency. In practice, this impacts the sequence in which
6/13/24, 11:19 AM Best practices on dependency management | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/dependency-management 1/5
resources are created by Terraform and how Terraform determines whether resources require
updates or replacements.
We recommended using explicit dependencies with the depends_on meta argument only as
the last resort when a dependency between two resources is hidden and can't be expressed
through implicit dependencies.
In the following example, the required project services must be enabled before creating a
BigQuery dataset. This dependency is declared explicitly:
thumb_downNot recommended:
The following example replaces the explicit dependency with an implicit dependency by
referencing the project_id argument as the project_id output attribute of the
project_services resource:
thumb_upRecommended:
module "project_services" {
source = "terraform-google-modules/project-factory/google//modules/project_se
version = "~> 14.4"
project_id = var.project_id
activate_apis = [
"bigquery.googleapis.com",
"bigquerystorage.googleapis.com",
]
}
module "bigquery" {
source = "terraform-google-modules/bigquery/google"
version = "~> 5.4"
dataset_id = "demo_dataset"
dataset_name = "demo_dataset"
project_id = var.project_id
depends_on = [module.project_services] # <- explicit dependency
}
6/13/24, 11:19 AM Best practices on dependency management | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/dependency-management 2/5
The use of implicit dependencies allows for precise declarations of dependencies, such as
specifying the exact information that needs to be collected from an upstream object. This also
reduces the need for making changes in multiple places, which in turn reduces the risk of
errors.
Reference output attributes from dependent resources
When you create implicit dependencies by referencing values from upstream resources, make
sure to only reference output attributes, specifically values that are not yet known
 (https://developer.hashicorp.com/terraform/language/expressions/references#values-not-yet-known).
This will ensure that Terraform waits for the upstream resources to be created before
provisioning the current resource.
In the following example, the google_storage_bucket_object resource references the name
argument of the google_storage_bucket resource. Arguments have known values during the
Terraform plan phase. This means that when Terraform creates the
google_storage_bucket_object resource, it doesn't wait for the google_storage_bucket
resource to be created because referencing a known argument (the bucket name) doesn't
create an implicit dependency between the google_storage_bucket_object and the
google_storage_bucket. This defeats the purpose of the implicit dependency declaration
between the two resources.
thumb_downNot recommended:
module "bigquery" {
source = "terraform-google-modules/bigquery/google"
version = "~> 5.4"
dataset_id = "demo_dataset"
dataset_name = "demo_dataset"
project_id = module.project_services.project_id # <- implicit dependency
}
# Cloud Storage bucket
resource "google_storage_bucket" "bucket" {
6/13/24, 11:19 AM Best practices on dependency management | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/dependency-management 3/5
Instead, google_storage_bucket_object resource must reference the id output attribute of
the google_storage_bucket_object resource. Since the id field is an output attribute, its
value is only set after the creation of its resource has been executed. Therefore, Terraform will
wait for the creation of the google_storage_bucket_object resource to complete before
beginning the creation of the google_storage_bucket_object resource.
thumb_upRecommended:
Sometimes there is no obvious output attribute to reference. For example, consider the
following example where module_a takes the name of the generated file as input. Inside
module_a, the filename is used to read the file. If you run this code as-is, you'll get a no such
file or directory exception, which is caused by Terraform attempting to read the file during
its planning phase, at which time the file hasn't been created yet. In this case, an examination
of the output attribute of the local_file resource reveals that there are no obvious fields that
you can use in place of the filename input argument.
thumb_downNot recommended:
name = "demo-bucket"
location = "US"
}
resource "google_storage_bucket_object" "bucket_object" {
name = "demo-object"
source = "./test.txt"
bucket = google_storage_bucket.bucket.name # name is an input argument
}
resource "google_storage_bucket_object" "bucket_object" {
name = "demo-object"
source = "./test.txt"
bucket = google_storage_bucket.bucket.id # id is an output attribute
}
resource "local_file" "generated_file" {
filename = "./generated_file.text"
content = templatefile("./template.tftpl", {
6/13/24, 11:19 AM Best practices on dependency management | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/dependency-management 4/5
You can solve this problem by introducing an explicit dependency. As a best practice, make
sure add a comment on why the explicit dependency is needed:
thumb_up Recommended:

module "module_a" {
source = "./modules/module-a"
root_config_file_path = local_file.generated_file.filename
depends_on = [local_file.generated_file] # waiting for generated_file to be created
}

Best practices for general style and
structure
This document provides basic style and structure recommendations for your Terraform
configurations. These recommendations apply to reusable Terraform modules and to root
configurations.
This guide is not an introduction to Terraform. For an introduction to using Terraform with
Google Cloud, see Get started with Terraform (/docs/terraform/get-started-with-terraform).
Follow a standard module structure
Terraform modules must follow the standard module structure
 (https://www.terraform.io/docs/modules/create.html).
Start every module with a main.tf file, where resources are located by default.
In every module, include a README.md file in Markdown format. In the README.md file,
include basic documentation about the module.
Place examples in an examples/ folder, with a separate subdirectory for each example.
For each example, include a detailed README.md file.
Create logical groupings of resources with their own files and descriptive names, such as
network.tf, instances.tf, or loadbalancer.tf.
Avoid giving every resource its own file. Group resources by their shared purpose.
For example, combine google_dns_managed_zone and google_dns_record_set in
dns.tf.
In the module's root directory, include only Terraform (*.tf) and repository metadata
files (such as README.md and CHANGELOG.md).
Place any additional documentation in a docs/ subdirectory.
Adopt a naming convention
6/13/24, 11:17 AM Best practices for general style and structure | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/general-style-structure 1/8
Name all configuration objects using underscores to delimit multiple words. This practice
ensures consistency with the naming convention for resource types, data source types,
and other predefined values. This convention does not apply to name arguments
 (https://www.terraform.io/docs/glossary#argument).
thumb_upRecommended:
thumb_downNot recommended:
To simplify references to a resource that is the only one of its type (for example, a single
load balancer for an entire module), name the resource main.
It takes extra mental work to remember
some_google_resource.my_special_resource.id versus
some_google_resource.main.id.
To differentiate resources of the same type from each other (for example, primary and
secondary), provide meaningful resource names.
Make resource names singular.
In the resource name, don't repeat the resource type. For example:
thumb_upRecommended:
resource "google_compute_instance" "web_server" {
name = "web-server"
}
resource "google_compute_instance" "web-server" {
name = "web-server"
}
resource "google_compute_global_address" "main" { ... }
6/13/24, 11:17 AM Best practices for general style and structure | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/general-style-structure 2/8
thumb_downNot recommended:
Use variables carefully
Declare all variables in variables.tf.
Give variables descriptive names that are relevant to their usage or purpose:
Inputs, local variables, and outputs representing numeric values—such as disk sizes
or RAM size—must be named with units (such as ram_size_gb). Google Cloud APIs
don't have standard units, so naming variables with units makes the expected input
unit clear for configuration maintainers.
For units of storage, use binary unit prefixes (powers of 1024)—kibi, mebi, gibi.
For all other units of measurement, use decimal unit prefixes (powers of 1000)
—kilo, mega, giga. This usage matches the usage within Google Cloud.
To simplify conditional logic, give boolean variables positive names—for example,
enable_external_access.
Variables must have descriptions. Descriptions are automatically included in a published
module's auto-generated documentation. Descriptions add additional context for new
developers that descriptive names cannot provide.
Give variables defined types.
When appropriate, provide default values:
For variables that have environment-independent values (such as disk size), provide
default values.
For variables that have environment-specific values (such as project_id), don't
provide default values. This way, the calling module must provide meaningful
values.
Use empty defaults for variables (like empty strings or lists) only when leaving the
variable empty is a valid preference that the underlying APIs don't reject.
resource "google_compute_global_address" "main_global_address" { … }
6/13/24, 11:17 AM Best practices for general style and structure | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/general-style-structure 3/8
Be judicious in your use of variables. Only parameterize values that must vary for each
instance or environment. When deciding whether to expose a variable, ensure that you
have a concrete use case for changing that variable. If there's only a small chance that a
variable might be needed, don't expose it.
Adding a variable with a default value is backwards-compatible.
Removing a variable is backwards-incompatible.
In cases where a literal is reused in multiple places, you can use a local value
 (https://www.terraform.io/docs/configuration/locals.html) without exposing it as a
variable.
Expose outputs
Organize all outputs in an outputs.tf file.
Provide meaningful descriptions for all outputs.
Document output descriptions in the README.md file. Auto-generate descriptions on
commit with tools like terraform-docs (https://github.com/terraform-docs/terraform-docs).
Output all useful values that root modules might need to refer to or share. Especially for
open source or heavily used modules, expose all outputs that have potential for
consumption.
Don't pass outputs directly through input variables, because doing so prevents them from
being properly added to the dependency graph. To ensure that implicit dependencies
 (https://learn.hashicorp.com/terraform/getting-started/dependencies.html) are created, make
sure that outputs reference attributes from resources. Instead of referencing an input
variable for an instance directly, pass the attribute through as shown here:
thumb_upRecommended:
output "name" {
description = "Name of instance"
value = google_compute_instance.main.name
}
6/13/24, 11:17 AM Best practices for general style and structure | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/general-style-structure 4/8
thumb_downNot recommended:
Use data sources
Put data sources (https://www.terraform.io/docs/configuration/data-sources.html) next to the
resources that reference them. For example, if you are fetching an image to be used in
launching an instance, place it alongside the instance instead of collecting data
resources in their own file.
If the number of data sources becomes large, consider moving them to a dedicated
data.tf file.
To fetch data relative to the current environment, use variable or resource interpolation
 (https://www.terraform.io/language/expressions/strings#interpolation).
Limit the use of custom scripts
Use scripts only when necessary. The state of resources created through scripts is not
accounted for or managed by Terraform.
Avoid custom scripts, if possible. Use them only when Terraform resources don't
support the desired behavior.
Any custom scripts used must have a clearly documented reason for existing and
ideally a deprecation plan.
Terraform can call custom scripts through provisioners, including the local-exec
provisioner.
Put custom scripts called by Terraform in a scripts/ directory.
output "name" {
description = "Name of instance"
value = var.name
}
6/13/24, 11:17 AM Best practices for general style and structure | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/general-style-structure 5/8
Include helper scripts in a separate directory
Organize helper scripts that aren't called by Terraform in a helpers/ directory.
Document helper scripts in the README.md file with explanations and example
invocations.
If helper scripts accept arguments, provide argument-checking and --help output.
Put static files in a separate directory
Static files that Terraform references but doesn't execute (such as startup scripts loaded
onto Compute Engine instances) must be organized into a files/ directory.
Place lengthy HereDocs in external files, separate from their HCL. Reference them with
the file() function (https://www.terraform.io/language/functions/file).
For files that are read in by using the Terraform templatefile function
 (https://www.terraform.io/docs/configuration/functions/templatefile.html), use the file extension
.tftpl.
Templates must be placed in a templates/ directory.
Protect stateful resources
For stateful resources, such as databases, ensure that deletion protection
 (https://www.terraform.io/language/meta-arguments/lifecycle) is enabled. For example:
resource "google_sql_database_instance" "main" {
name = "primary-instance"
settings {
tier = "D0"
}
lifecycle {
prevent_destroy = true
}
6/13/24, 11:17 AM Best practices for general style and structure | Terraform | Google Cloud
https://cloud.google.com/docs/terraform/best-practices/general-style-structure 6/8
Use built-in formatting
All Terraform files must conform to the standards of terraform fmt.
Limit the complexity of expressions
Limit the complexity of any individual interpolated expressions. If many functions are
needed in a single expression, consider splitting it out into multiple expressions by using
local values (https://www.terraform.io/docs/configuration/locals.html).
Never have more than one ternary operation in a single line. Instead, use multiple local
values to build up the logic.
Use count for conditional values
To instantiate a resource conditionally, use the count
 (https://www.terraform.io/language/meta-arguments/count) meta-argument. For example:
Be sparing when using user-specified variables to set the count variable for resources. If a
resource attribute is provided for such a variable (like project_id) and that resource does not
}
variable "readers" {
description = "..."
type = list
default = []
}
resource "resource_type" "reference_name" {
// Do not create this resource if the list of readers is empty.
count = length(var.readers) == 0 ? 0 : 1
...
}

 """

from anthropic import AnthropicVertex
import json
client = AnthropicVertex(region="us-east5", project_id="next24-genai-app")


final_prompt = prompt_template % (bash_script, reference_doc)

message = client.messages.create(
  max_tokens=4090,
  system="You are a helpful assistant and you are subject matter expert in GCP & Terraform.",
  messages=[{
      "role": "user",
      "content": final_prompt,
    }
  ],
  model="claude-3-5-sonnet@20240620",
)
def extract_text_from_json(json_object):
  try:
    content = json_object["content"][0]["text"]  # Assuming the text is in the first element of the "content" list
    return content
  except KeyError:
    print("Error: The JSON object does not have the expected format.")
    return None
print(message.model_dump_json(indent=2))
# Parse the JSON string
json_object = json.loads(message.model_dump_json(indent=2))

# Extract and print the text content
text = extract_text_from_json(json_object)
if text:
  print(text)