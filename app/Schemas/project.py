from pydantic import BaseModel
from datetime import date

# Create a project
class Project(BaseModel):
    name: str
    description: str

# Response - get
class ProjectResponse(Project):
    id: str
    created_at: date

# A user works on a project
class user_works_on(BaseModel):
    user: str
    project_id: str