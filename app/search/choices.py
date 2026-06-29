from django.db import models
from django.utils.translation import gettext_lazy as _


class SearchModality(models.TextChoices):
    EAD = "ead", _("EAD")
    PRESENCIAL = "presencial", _("Presencial")
    HIBRIDO = "hibrido", _("Híbrido")
    # "Todas as modalidades" é representado por "" (string vazia) na persistência;
    # o rótulo "Todas" é tratado apenas na camada de formulário.

class SearchStatus(models.TextChoices):
    PENDING = "pending", _("Pendente")
    PROCESSING = "processing", _("Processando")
    COMPLETED = "completed", _("Concluída")
    FAILED = "failed", _("Falhou")
    NO_RESULTS = "no_results", _("Sem resultados")

class SearchArea(models.TextChoices):
    ADMINISTRACAO = "administracao", _("Administração")
    AGRARIAS = "agrarias", _("Ciências Agrárias")
    BIOLOGICAS = "biologicas", _("Ciências Biológicas")
    SAUDE = "saude", _("Ciências da Saúde")
    EXATAS = "exatas", _("Ciências Exatas e da Terra")
    HUMANAS = "humanas", _("Ciências Humanas")
    SOCIAIS = "sociais", _("Ciências Sociais Aplicadas")
    ENGENHARIAS = "engenharias", _("Engenharias")
    LINGUISTICA_LETRAS_ARTES = "linguistica_letras_artes", _("Linguística, Letras e Artes")
    MULTIDISCIPLINAR = "multidisciplinar", _("Multidisciplinar")

class SearchStates_Br(models.TextChoices):
    AC = "AC", _("Acre")
    AL = "AL", _("Alagoas")
    AP = "AP", _("Amapá")
    AM = "AM", _("Amazonas")
    BA = "BA", _("Bahia")
    CE = "CE", _("Ceará")
    DF = "DF", _("Distrito Federal")
    ES = "ES", _("Espírito Santo")
    GO = "GO", _("Goiás")
    MA = "MA", _("Maranhão")
    MT = "MT", _("Mato Grosso")
    MS = "MS", _("Mato Grosso do Sul")
    MG = "MG", _("Minas Gerais")
    PA = "PA", _("Pará")
    PB = "PB", _("Paraíba")
    PR = "PR", _("Paraná")
    PE = "PE", _("Pernambuco")
    PI = "PI", _("Piauí")
    RJ = "RJ", _("Rio de Janeiro")
    RN = "RN", _("Rio Grande do Norte")
    RS = "RS", _("Rio Grande do Sul")
    RO = "RO", _("Rondônia")
    RR = "RR", _("Roraima")
    SC = "SC", _("Santa Catarina")
    SP = "SP", _("São Paulo")
    SE = "SE", _("Sergipe")
    TO = "TO", _("Tocantins")
