from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str
    num_results: int = 10

class ModelConfig(BaseModel):
    model: str

class SearchResult(BaseModel):
    job_id: Optional[str]
    job_title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    salary_range: Optional[str]

class SearchDetail(BaseModel):
    job_id: str
    experience: Optional[str]
    qualifications: Optional[str]
    salary_range: Optional[str]
    location: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    work_type: Optional[str]
    company_size: Optional[int]
    job_posting_date: Optional[date]
    preference: Optional[str]
    contact_person: Optional[str]
    contact: Optional[str]
    job_title: Optional[str]
    role: Optional[str]
    job_portal: Optional[str]
    job_description: Optional[str]
    benefits: Optional[List[str]]
    skills: Optional[str]
    responsibilities: Optional[List[str]]
    company: Optional[str]
    company_profile: Optional[Dict]  # JSONB
class SearchResponse(BaseModel):
    results: List[SearchResult]
    # summary: str

class QuerySuggestionResponse(BaseModel):
    results: List[str]