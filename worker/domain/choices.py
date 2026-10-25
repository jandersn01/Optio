from enum import StrEnum

class SearchModality(StrEnum):
    EAD = "ead"
    PRESENCIAL = "presencial"
    HIBRIDO = "hibrido"
    # "Todas as modalidades" é representado por "" (string vazia) na persistência;
    # o rótulo "Todas" é tratado apenas na camada de formulário.

class SearchStates_Br(StrEnum):
    AC = "AC",
    AL = "AL",
    AP = "AP",
    AM = "AM",
    BA = "BA",
    CE = "CE",
    DF = "DF", 
    ES = "ES", 
    GO = "GO", 
    MA = "MA", 
    MT = "MT", 
    MS = "MS", 
    MG = "MG", 
    PA = "PA", 
    PB = "PB", 
    PR = "PR", 
    PE = "PE", 
    PI = "PI", 
    RJ = "RJ", 
    RN = "RN", 
    RS = "RS", 
    RO = "RO", 
    RR = "RR", 
    SC = "SC", 
    SP = "SP", 
    SE = "SE", 
    TO = "TO", 
