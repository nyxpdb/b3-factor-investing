from pydantic import BaseModel, field_validator


class AcaoSchema(BaseModel):
    symbol: str
    priceEarnings: float
    returnOnEquity: float
    volume: int

    @field_validator("symbol")
    @classmethod
    def symbol_nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("symbol não pode ser vazio")
        return v.strip().upper()

    @field_validator("volume")
    @classmethod
    def volume_nao_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("volume não pode ser negativo")
        return v
