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
class User_works_on(BaseModel):
    user: str
    project_id: str

# New delveloper on a project
class New_worker(User_works_on):
    role: str