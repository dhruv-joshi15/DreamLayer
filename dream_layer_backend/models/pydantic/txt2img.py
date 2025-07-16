from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ControlNetUnit(BaseModel):
    enabled: Optional[bool] = False
    input_image: Optional[str] = None
    model: Optional[str] = None
    module: Optional[str] = None
    weight: Optional[float] = None
    resize_mode: Optional[str] = None
    processor_res: Optional[int] = None


class ControlNetData(BaseModel):
    enabled: Optional[bool] = False
    units: Optional[List[ControlNetUnit]] = None


class Txt2ImgRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    model: str
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    steps: int = Field(default=20, gt=0)
    cfg_scale: float = Field(default=7.5, gt=0)
    seed: Optional[int] = None
    batch_size: int = Field(default=1, ge=1, le=1)
    lora: Optional[str] = None
    controlnet: Optional[ControlNetData] = None
    other_settings: Optional[Dict[str, Any]] = None
