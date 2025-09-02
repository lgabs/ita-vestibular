from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from enum import StrEnum, auto
import warnings


class CategoryType(StrEnum):
    """Enumeration of ITA vestibular candidate categories."""

    EFETIVOS = auto()
    TREINEIROS = auto()
    ATIVA = auto()
    RESERVA = auto()
    GERAL = auto()


class CourseType(StrEnum):
    """Enumeration of ITA engineering specializations."""

    ENGENHARIA_AEROESPACIAL = "Engenharia Aeroespacial"
    ENGENHARIA_AERONAUTICA = "Engenharia Aeronáutica"
    ENGENHARIA_CIVIL_AERONAUTICA = "Engenharia Civil-Aeronáutica"
    ENGENHARIA_DE_COMPUTACAO = "Engenharia de Computação"
    ENGENHARIA_ELETRONICA = "Engenharia Eletrônica"
    ENGENHARIA_DE_ENERGIA = "Engenharia de Energia"
    ENGENHARIA_MECANICA_AERONAUTICA = "Engenharia Mecânica-Aeronáutica"
    ENGENHARIA_DE_SISTEMAS = "Engenharia de Sistemas"


class SchoolType(StrEnum):
    """Enumeration of school origin types for ITA candidates."""

    FEDERAL = "Federal"
    ESTADUAL = "Estadual"
    MUNICIPAL = "Municipal"
    PARTICULAR = "Particular"
    FIZERAM_CURSO_PREPARATORIO = "Fizeram Curso Preparatório"


class SubjectType(StrEnum):
    """Enumeration of exam subjects and average types for ITA vestibular."""

    MEDIA_1A_FASE = "Média 1ª Fase"
    MATEMATICA = "Matemática"
    FISICA = "Física"
    QUIMICA = "Química"
    PORTUGUES = "Português"
    REDACAO = "Redação"
    INGLES = "Inglês"
    MEDIA_GERAL_SEM_INGLES = "Média Geral (sem inglês)"


class AdmissionType(StrEnum):
    """Enumeration of admission types for ITA vestibular."""

    AMPLA_CONCORRENCIA = "Ampla Concorrência"  # Also known as "Vagas Ordinárias"
    COTA_RACIAL = "Cota Racial"  # Also known as "Vagas Privativas"


class ExamLocationCity(StrEnum):
    """Enumeration of exam location cities for ITA vestibular."""

    MANAUS_AM = "Manaus-AM"
    BELEM_PA = "Belém-PA"
    FORTALEZA_CE = "Fortaleza-CE"
    NATAL_RN = "Natal-RN"
    RECIFE_PE = "Recife-PE"
    SALVADOR_BA = "Salvador-BA"
    TERESINA_PI = "Teresina-PI"
    SAO_LUIS_MA = "São Luís-MA"
    BRASILIA_DF = "Brasília-DF"
    GOIANIA_GO = "Goiânia-GO"
    CAMPO_GRANDE_MS = "Campo Grande-MS"
    CUIABA_MT = "Cuiabá-MT"
    BELO_HORIZONTE_MG = "Belo Horizonte-MG"
    JUIZ_DE_FORA_MG = "Juiz de Fora-MG"
    VITORIA_ES = "Vitória-ES"
    RIO_DE_JANEIRO_RJ = "Rio de Janeiro-RJ"
    SAO_PAULO_SP = "São Paulo-SP"
    SAO_JOSE_DOS_CAMPOS_SP = "São José dos Campos-SP"
    CAMPINAS_SP = "Campinas-SP"
    RIBEIRAO_PRETO_SP = "Ribeirão Preto-SP"
    SAO_JOSE_DO_RIO_PRETO_SP = "São José do Rio Preto-SP"
    CURITIBA_PR = "Curitiba-PR"
    LONDRINA_PR = "Londrina-PR"
    FLORIANOPOLIS_SC = "Florianópolis-SC"
    PORTO_ALEGRE_RS = "Porto Alegre-RS"
    OTHER = "Other"  # For catching unexpected locations


class CandidateRegistration(BaseModel):
    """Registration data for a specific candidate category."""

    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data, or can be the total aggregated data labeled as 'geral' or 'total' (both should be mapped to 'GERAL')",
    )
    men: int = Field(description="Number of male candidates.")
    women: int = Field(description="Number of female candidates.")
    total: int = Field(description="Total number of candidates.")
    percentage: Optional[float] = Field(
        default=None, description="Percentage of total registrations for this category (0.0 to 1.0)."
    )


class SpecializationChoice(BaseModel):
    """Percentage of candidates choosing a specialization as their first option."""

    course: CourseType = Field(description="The engineering specialization.")
    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    percentage: float = Field(
        description="Percentage of applicants in this category for this course (0.0 to 1.0)."
    )


class SchoolOrigin(BaseModel):
    """Percentage of candidates from a specific type of school."""

    school_type: SchoolType = Field(
        description="Type of school origin for the candidate."
    )
    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    percentage: float = Field(
        description="Percentage of applicants in this category from this school type (0.0 to 1.0)."
    )


class Absenteeism(BaseModel):
    """Absenteeism rates by candidate category."""

    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    percentage: float = Field(
        description="The percentage of absenteeism for this category (0.0 to 1.0)."
    )


class SubjectAverage(BaseModel):
    """Average exam scores for convocated candidates."""

    subject: SubjectType = Field(
        description="The subject or exam phase for the average score."
    )
    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    average_score: float = Field(description="The average score.")


class CutoffScore(BaseModel):
    """Cutoff scores for admission."""

    candidate_category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    admission_type: AdmissionType = Field(
        description="The admission type for cutoff score calculation. They can be 'Ampla Concorrência' (also seen as 'Vagas Ordinárias') or 'Cota Racial' (also seen as 'Vagas Privativas')."
    )
    score: float = Field(description="The cutoff score.")


class ConvocationCount(BaseModel):
    """Number of convocated candidates by gender."""

    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    men: int = Field(description="Number of convocated men.")
    women: int = Field(description="Number of convocated women.")
    total: int = Field(description="Total number of convocated candidates.")


class ExamLocationStat(BaseModel):
    """Statistics for a single exam location (Banca)."""

    location: ExamLocationCity = Field(description="The city/state of the exam location.")
    registered_men: int
    registered_women: int
    registered_total: int
    convocated_men: int
    convocated_women: int
    convocated_total: int

    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        """Warn if location is 'Other' indicating an unexpected city."""
        if v == ExamLocationCity.OTHER:
            warnings.warn(
                f"Unexpected exam location found. Location was mapped to 'Other'. "
                f"Consider adding this location to the ExamLocationCity enum.",
                UserWarning
            )
        return v


class ExamLocationReport(BaseModel):
    """A collection of statistics for all exam locations, for a specific candidate group if applicable."""

    category: Optional[CategoryType] = Field(
        default=None,
        description="The candidate category. Optional - may not be present in all data.",
    )
    locations: List[ExamLocationStat]


class YearlyReport(BaseModel):
    """A comprehensive report containing all extracted statistics for a single year."""

    year: int

    registrations: List[CandidateRegistration] = Field(
        description="Corresponds to 'Número de candidatos inscritos'."
    )
    specialization_choices: List[SpecializationChoice] = Field(
        description="Corresponds to 'Especialidade escolhida em primeira opção'.",
    )
    school_origins: Optional[List[SchoolOrigin]] = Field(
        default=None,
        description="Corresponds to 'Procedência escolar dos candidatos inscritos'.",
    )
    absenteeism: Optional[List[Absenteeism]] = Field(
        default=None, description="Corresponds to 'Abstenção às provas'."
    )
    subject_averages: Optional[List[SubjectAverage]] = Field(
        default=None, description="Corresponds to 'Médias dos candidatos convocados'."
    )
    cutoff_scores: Optional[List[CutoffScore]] = Field(
        default=None, description="Corresponds to 'Nota de corte'."
    )
    convocation_counts: Optional[List[ConvocationCount]] = Field(
        default=None,
        description="Corresponds to 'Candidatos Convocados' counts by gender.",
    )
    exam_locations: Optional[List[ExamLocationReport]] = Field(
        default=None,
        description="Corresponds to 'Bancas Examinadoras'. Can contain multiple reports for different candidate types.",
    )
