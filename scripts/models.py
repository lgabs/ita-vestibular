from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class CandidateRegistration(BaseModel):
    """Registration data for a specific candidate category."""
    category: str = Field(description="The category of registration (e.g., 'Efetivos', 'Treineiros', 'Ativa', 'Reserva').")
    men: int = Field(description="Number of male candidates.")
    women: int = Field(description="Number of female candidates.")
    total: int = Field(description="Total number of candidates.")
    percentage: Optional[str] = Field(default=None, description="Percentage of total registrations for this category.")

class SpecializationChoice(BaseModel):
    """Percentage of candidates choosing a specialization as their first option."""
    course: str = Field(description="The engineering specialization.")
    category: str = Field(description="The candidate category (e.g., 'Efetivos', 'Ativa').")
    percentage: str = Field(description="Percentage of applicants in this category for this course.")

class SchoolOrigin(BaseModel):
    """Percentage of candidates from a specific type of school."""
    school_type: str = Field(description="Type of school (e.g., 'Federal', 'Particular').")
    category: str = Field(description="The candidate category (e.g., 'Efetivos', 'Ativa').")
    percentage: str = Field(description="Percentage of applicants in this category from this school type.")

class Absenteeism(BaseModel):
    """Absenteeism rates by candidate category."""
    category: str = Field(description="The candidate category.")
    percentage: str = Field(description="The percentage of absenteeism for this category.")

class SubjectAverage(BaseModel):
    """Average exam scores for convocated candidates."""
    subject: str = Field(description="The subject or exam phase (e.g., 'Matemática', 'Média 1ª Fase').")
    category: str = Field(description="The candidate category (e.g., 'Ativa', 'Geral', or 'Overall' if not specified).")
    average_score: float = Field(description="The average score.")

class CutoffScore(BaseModel):
    """Cutoff scores for admission."""
    candidate_category: str = Field(description="The main candidate category (e.g., 'Efetivos', 'Ativa').")
    admission_type: str = Field(description="The admission type (e.g., 'Ampla Concorrência', 'Cota Racial').")
    score: float = Field(description="The cutoff score.")

class ConvocationCount(BaseModel):
    """Number of convocated candidates by gender."""
    category: str = Field(description="The candidate category (e.g., 'Ativa', 'Total', or 'Overall' if not specified).")
    men: int = Field(description="Number of convocated men.")
    women: int = Field(description="Number of convocated women.")
    total: int = Field(description="Total number of convocated candidates.")

class ExamLocationStat(BaseModel):
    """Statistics for a single exam location (Banca)."""
    location: str = Field(description="The city/state of the exam location.")
    registered_men: int
    registered_women: int
    registered_total: int
    convocated_men: int
    convocated_women: int
    convocated_total: int

class ExamLocationReport(BaseModel):
    """A collection of statistics for all exam locations, for a specific candidate group if applicable."""
    description: str = Field(description="A description of this report, e.g., 'Overall', 'Ativa Candidates', 'Reserva Candidates'.")
    locations: List[ExamLocationStat]


class YearlyReport(BaseModel):
    """A comprehensive report containing all extracted statistics for a single year."""
    year: int

    registrations: Optional[List[CandidateRegistration]] = Field(default=None, description="Corresponds to 'Número de candidatos inscritos'.")
    specialization_choices: Optional[List[SpecializationChoice]] = Field(default=None, description="Corresponds to 'Especialidade escolhida em primeira opção'.")
    school_origins: Optional[List[SchoolOrigin]] = Field(default=None, description="Corresponds to 'Procedência escolar dos candidatos inscritos'.")
    absenteeism: Optional[List[Absenteeism]] = Field(default=None, description="Corresponds to 'Abstenção às provas'.")
    subject_averages: Optional[List[SubjectAverage]] = Field(default=None, description="Corresponds to 'Médias dos candidatos convocados'.")
    cutoff_scores: Optional[List[CutoffScore]] = Field(default=None, description="Corresponds to 'Nota de corte'.")
    convocation_counts: Optional[List[ConvocationCount]] = Field(default=None, description="Corresponds to 'Candidatos Convocados' counts by gender.")
    exam_locations: Optional[List[ExamLocationReport]] = Field(default=None, description="Corresponds to 'Bancas Examinadoras'. Can contain multiple reports for different candidate types.")
