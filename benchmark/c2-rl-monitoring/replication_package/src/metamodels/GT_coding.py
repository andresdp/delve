# ### Sources and Metadata ###
from codeable_models import CEnum, CMetaclass

source_type = CEnum("Source Type", values=["Discussion Forum Post", "General Audience Article",
                                           "Practitioner Audience Article", "Practitioner Book",
                                           "Tool Documentation", "Blog Post", "Slides",
                                           "Presentation Video"])
author_type = CEnum("Author Type", values=["Practitioner", "Mixed", "Academic", "Unknown"])

reference = CMetaclass("Reference",
                       attributes={"url": str,
                                   "archive url": str,
                                   "tiny url": str,
                                   "title": str,
                                   "bibliographic reference": str,
                                   "author type": author_type,
                                   "type": source_type,
                                   "example": bool,
                                   "source code": bool})

source = CMetaclass("Source", superclasses=reference)

source.association(reference, "reference: [source] * -> [referenced] *")

# ### Codes ###

# attributes on code only for better explainability in the paper
code = CMetaclass("Code", attributes={
    "name": str,
    "description": str
})
code.association(source, "contains codes: [contained_code] * -> [evidence] *")